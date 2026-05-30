import os
import re
import imaplib
import hashlib
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "agent" / "input"
INPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_folder_line(line: str) -> tuple[list[str], str]:
    """Parse folder flags, delimiter, and name from IMAP LIST response line."""
    # Matches structure: (flags) "delimiter" name
    match = re.match(r'\((?P<flags>[^)]*)\)\s+"(?P<delim>[^"]*)"\s+(?P<name>.+)', line)
    if not match:
        # Matches structure: (flags) delimiter name (without delimiter quotes)
        match = re.match(r"\((?P<flags>[^)]*)\)\s+(?P<delim>\S+)\s+(?P<name>.+)", line)

    if match:
        flags = [f.strip().lower() for f in match.group("flags").split()]
        name = match.group("name").strip('"')
        return flags, name
    return [], ""


def find_trash_folder(mail) -> str:
    """Find the Gmail trash folder dynamically."""
    try:
        status, folder_list = mail.list()
        if status != "OK" or not folder_list:
            return "[Gmail]/Trash"

        # 1. Parse each line and look for the \trash attribute flag
        for folder_info in folder_list:
            decoded = folder_info.decode("utf-8", errors="ignore")
            flags, name = parse_folder_line(decoded)
            if "\\trash" in flags:
                return name

        # 2. If no explicit flag is found, search by common folder names
        common_patterns = [
            r"\[Gmail\]/Trash",
            r"\[Gmail\]/Bin",
            r"\[Gmail\]/Papierkorb",
            r"Trash",
            r"Bin",
            r"Papierkorb",
        ]
        for folder_info in folder_list:
            decoded = folder_info.decode("utf-8", errors="ignore")
            _, name = parse_folder_line(decoded)
            for pattern in common_patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    return name
    except Exception as e:
        print(f"Warning during trash folder detection: {e}")

    return "[Gmail]/Trash"


def fetch_emails():
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_app_password:
        print(
            "Error: GMAIL_USER or GMAIL_APP_PASSWORD environment variables are not set."
        )
        print("Please set them in your .env file or environment.")
        exit(1)

    try:
        print("Connecting to imap.gmail.com:993 via SSL...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        print("Logging in...")
        mail.login(gmail_user, gmail_app_password)
    except Exception as e:
        print(f"Error connecting or logging in to Gmail IMAP: {e}")
        exit(1)

    try:
        status, select_data = mail.select("INBOX")
        if status != "OK":
            print(f"Error selecting INBOX: {status}")
            mail.logout()
            exit(1)

        # Search for UNSEEN messages
        status, messages = mail.uid("search", None, "UNSEEN")
        if status != "OK":
            print(f"Error searching for UNSEEN messages: {status}")
            mail.logout()
            exit(1)

        msg_uids = messages[0].split()
        if not msg_uids:
            print("Inbox has no unseen (unread) emails to process.")
            mail.logout()
            exit(0)

        print(f"Found {len(msg_uids)} unseen email(s) to process.")

        # Dynamically determine the trash folder
        trash_folder = find_trash_folder(mail)
        print(f"Detected Gmail Trash folder: '{trash_folder}'")

        processed_count = 0
        written_count = 0
        deleted_count = 0

        for i, msg_uid in enumerate(msg_uids):
            uid_str = msg_uid.decode(errors="ignore")
            try:
                # Fetch full RFC822 email content
                status, data = mail.uid("fetch", msg_uid, "(RFC822)")
                if status != "OK" or not data or not data[0]:
                    print(
                        f"[{i + 1}/{len(msg_uids)}] Error fetching message UID {uid_str}: {status}"
                    )
                    continue

                raw_email_bytes = None
                for response_part in data:
                    if isinstance(response_part, tuple):
                        raw_email_bytes = response_part[1]
                        break

                if not raw_email_bytes:
                    print(
                        f"[{i + 1}/{len(msg_uids)}] Could not extract raw bytes for message UID {uid_str}"
                    )
                    continue

                # Generate a unique filename using timestamp and content hash
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                email_hash = hashlib.sha256(raw_email_bytes).hexdigest()[:10]
                filename = f"email_{timestamp}_{email_hash}.eml"
                file_path = INPUT_DIR / filename

                # Save email to input folder
                file_path.write_bytes(raw_email_bytes)
                written_count += 1

                # Move email to Gmail Trash
                copy_status, _ = mail.uid("COPY", msg_uid, trash_folder)
                if copy_status == "OK":
                    # Mark email as Deleted in current mailbox (INBOX)
                    delete_status, _ = mail.uid("STORE", msg_uid, "+FLAGS", "\\Deleted")
                    if delete_status == "OK":
                        deleted_count += 1
                    else:
                        print(
                            f"[{i + 1}/{len(msg_uids)}] Failed to mark UID {uid_str} as deleted: {delete_status}"
                        )
                else:
                    print(
                        f"[{i + 1}/{len(msg_uids)}] Failed to copy UID {uid_str} to Trash '{trash_folder}': {copy_status}"
                    )

                processed_count += 1

            except Exception as e:
                print(
                    f"[{i + 1}/{len(msg_uids)}] Error processing message UID {uid_str}: {e}"
                )

        # Expunge the deletions in the currently selected inbox
        if deleted_count > 0:
            try:
                mail.expunge()
            except Exception as e:
                print(f"Warning during expunge: {e}")

        print("\n=== Fetch Summary ===")
        print(f"Processed: {processed_count} of {len(msg_uids)} email(s)")
        print(f"Written:   {written_count} file(s) to 'agent/input/'")
        print(
            f"Deleted:   {deleted_count} email(s) from INBOX (moved to '{trash_folder}')"
        )

        mail.logout()

    except Exception as e:
        print(f"An unexpected error occurred during email ingestion: {e}")
        try:
            mail.logout()
        except Exception:
            pass
        exit(1)


if __name__ == "__main__":
    fetch_emails()

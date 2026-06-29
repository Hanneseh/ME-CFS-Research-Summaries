#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import imaplib
import json
import os
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "agent-cli" / "input"
EMAILS_DIR = INPUT_DIR / "emails"

# Default configurations
USER_AGENT = "ME-CFS-Research-Curation-Bot/1.0 (contact: hannes.ehringfeld@gmail.com)"
REDDIT_FEEDS = [
    "https://www.reddit.com/r/CFSScience/.rss",
    "https://www.reddit.com/search.rss?q=MECFS+conference+daratumumab&sort=new",
]

def ensure_dirs():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    EMAILS_DIR.mkdir(parents=True, exist_ok=True)

def parse_iso_datetime(dt_str: str) -> datetime:
    normalized = dt_str.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

# ==========================================
# Email Ingestion
# ==========================================

def parse_folder_line(line: str) -> tuple[list[str], str]:
    match = re.match(r'\((?P<flags>[^)]*)\)\s+"(?P<delim>[^"]*)"\s+(?P<name>.+)', line)
    if not match:
        match = re.match(r"\((?P<flags>[^)]*)\)\s+(?P<delim>\S+)\s+(?P<name>.+)", line)
    if match:
        flags = [f.strip().lower() for f in match.group("flags").split()]
        name = match.group("name").strip('"')
        return flags, name
    return [], ""

def find_trash_folder(mail) -> str:
    try:
        status, folder_list = mail.list()
        if status != "OK" or not folder_list:
            return "[Gmail]/Trash"

        for folder_info in folder_list:
            decoded = folder_info.decode("utf-8", errors="ignore")
            flags, name = parse_folder_line(decoded)
            if "\\trash" in flags:
                return name

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
        print("Error: GMAIL_USER or GMAIL_APP_PASSWORD environment variables are not set.")
        return False

    try:
        print("Connecting to imap.gmail.com:993 via SSL...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        print("Logging in...")
        mail.login(gmail_user, gmail_app_password)
    except Exception as e:
        print(f"Error connecting or logging in to Gmail IMAP: {e}")
        return False

    try:
        status, select_data = mail.select("INBOX")
        if status != "OK":
            print(f"Error selecting INBOX: {status}")
            mail.logout()
            return False

        status, messages = mail.uid("search", None, "UNSEEN")
        if status != "OK":
            print(f"Error searching for UNSEEN messages: {status}")
            mail.logout()
            return False

        msg_uids = messages[0].split()
        if not msg_uids:
            print("Inbox has no unseen (unread) emails to process.")
            mail.logout()
            return True

        print(f"Found {len(msg_uids)} unseen email(s) to process.")
        trash_folder = find_trash_folder(mail)
        print(f"Detected Gmail Trash folder: '{trash_folder}'")

        processed_count = 0
        written_count = 0
        deleted_count = 0

        for i, msg_uid in enumerate(msg_uids):
            uid_str = msg_uid.decode(errors="ignore")
            try:
                status, data = mail.uid("fetch", msg_uid, "(RFC822)")
                if status != "OK" or not data or not data[0]:
                    print(f"[{i + 1}/{len(msg_uids)}] Error fetching message UID {uid_str}: {status}")
                    continue

                raw_email_bytes = None
                for response_part in data:
                    if isinstance(response_part, tuple):
                        raw_email_bytes = response_part[1]
                        break

                if not raw_email_bytes:
                    print(f"[{i + 1}/{len(msg_uids)}] Could not extract raw bytes for message UID {uid_str}")
                    continue

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                email_hash = hashlib.sha256(raw_email_bytes).hexdigest()[:10]
                filename = f"email_{timestamp}_{email_hash}.eml"
                file_path = EMAILS_DIR / filename

                file_path.write_bytes(raw_email_bytes)
                written_count += 1

                copy_status, _ = mail.uid("COPY", msg_uid, trash_folder)
                if copy_status == "OK":
                    delete_status, _ = mail.uid("STORE", msg_uid, "+FLAGS", "\\Deleted")
                    if delete_status == "OK":
                        deleted_count += 1
                processed_count += 1
            except Exception as e:
                print(f"[{i + 1}/{len(msg_uids)}] Error processing message UID {uid_str}: {e}")

        if deleted_count > 0:
            mail.expunge()

        print(f"Processed: {processed_count} of {len(msg_uids)} email(s)")
        print(f"Written:   {written_count} file(s) to '{EMAILS_DIR.relative_to(BASE_DIR)}'")
        mail.logout()
        return True
    except Exception as e:
        print(f"An unexpected error occurred during email ingestion: {e}")
        try:
            mail.logout()
        except Exception:
            pass
        return False

# ==========================================
# Reddit Ingestion
# ==========================================

def extract_outbound_link(content_html: str, reddit_link: str) -> str:
    if not content_html:
        return reddit_link
    soup = BeautifulSoup(content_html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("http://", "https://")):
            href_lower = href.lower()
            if not any(domain in href_lower for domain in ["reddit.com", "redditmedia.com", "redd.it"]):
                return href
    return reddit_link

def clean_html_content(content_html: str) -> str:
    if not content_html:
        return ""
    soup = BeautifulSoup(content_html, "html.parser")
    for a in soup.find_all("a"):
        text = a.get_text().strip()
        if text in ("[link]", "[comments]"):
            a.decompose()
    text = soup.get_text(separator="\n")
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())

def fetch_and_parse_reddit_feed(url: str) -> list[dict]:
    print(f"Fetching Reddit feed: {url}")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/atom+xml, application/xml, text/xml, */*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Error fetching feed {url}: {e}")
        return []

    try:
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"Error parsing XML from feed {url}: {e}")
        return []

    namespaces = {"atom": "http://www.w3.org/2005/Atom"}
    parsed_entries = []
    entries = root.findall("atom:entry", namespaces)
    for entry in entries:
        title_elem = entry.find("atom:title", namespaces)
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled"

        reddit_link = ""
        links = entry.findall("atom:link", namespaces)
        for link in links:
            href = link.attrib.get("href")
            if href:
                rel = link.attrib.get("rel")
                if rel == "alternate" or not rel:
                    reddit_link = href.strip()
                    break
        if not reddit_link and links:
            href = links[0].attrib.get("href")
            if href:
                reddit_link = href.strip()

        updated_elem = entry.find("atom:updated", namespaces)
        updated_str = updated_elem.text.strip() if updated_elem is not None and updated_elem.text else ""

        content_elem = entry.find("atom:content", namespaces)
        content_html = content_elem.text if content_elem is not None else ""

        outbound_link = extract_outbound_link(content_html, reddit_link)
        cleaned_content = clean_html_content(content_html)

        parsed_entries.append({
            "title": title,
            "reddit_link": reddit_link,
            "updated_str": updated_str,
            "outbound_link": outbound_link,
            "content": cleaned_content,
        })
    return parsed_entries

def fetch_reddit():
    all_entries = []
    for url in REDDIT_FEEDS:
        entries = fetch_and_parse_reddit_feed(url)
        all_entries.extend(entries)

    output_file = INPUT_DIR / "reddit_feed.json"
    if not all_entries:
        print("No entries fetched from any feed.")
        if output_file.exists():
            output_file.unlink()
        return True

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=30)

    filtered_entries = []
    for entry in all_entries:
        updated_str = entry["updated_str"]
        if not updated_str:
            continue
        try:
            dt = parse_iso_datetime(updated_str)
            if dt >= cutoff:
                entry["parsed_date"] = dt
                filtered_entries.append(entry)
        except Exception as e:
            print(f"Skipping entry '{entry['title']}' due to date parsing error: {e}")

    if not filtered_entries:
        print("No items match the 30-day rolling window.")
        if output_file.exists():
            output_file.unlink()
        return True

    filtered_entries.sort(key=lambda x: x["parsed_date"], reverse=True)

    unique_entries = []
    seen_links = set()
    for entry in filtered_entries:
        link_to_check = entry["outbound_link"] or entry["reddit_link"]
        if link_to_check not in seen_links:
            seen_links.add(link_to_check)
            unique_entries.append(entry)

    publications = []
    for entry in unique_entries:
        publications.append({
            "title": entry["title"],
            "link": entry["outbound_link"] or entry["reddit_link"] or None,
            "source": "Reddit",
            "published_date": entry["parsed_date"].strftime("%Y-%m-%d")
        })

    payload = {"publications": publications}
    output_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Successfully wrote {len(publications)} entries to {output_file.relative_to(BASE_DIR)}")
    return True

# ==========================================
# YouTube Ingestion (Unified RSS + Scraping)
# ==========================================

def resolve_youtube_channel_id(channel_url_or_id: str) -> str:
    channel_url_or_id = channel_url_or_id.strip()
    if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", channel_url_or_id):
        return channel_url_or_id

    print(f"Resolving YouTube channel ID for URL: {channel_url_or_id}")
    req = urllib.request.Request(
        channel_url_or_id,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Failed to fetch YouTube channel URL {channel_url_or_id}: {e}")

    match = re.search(r'<meta itemprop="channelId" content="(UC[A-Za-z0-9_-]{22})"', html)
    if match:
        return match.group(1)

    match = re.search(r'youtube\.com/feeds/videos\.xml\?channel_id=(UC[A-Za-z0-9_-]{22})', html)
    if match:
        return match.group(1)

    match = re.search(r'"channelId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"', html)
    if match:
        return match.group(1)

    # Let's search generally for any UC match
    matches = re.findall(r'UC[A-Za-z0-9_-]{22}', html)
    if matches:
        # Fall back to first UC match if found
        return matches[0]

    raise ValueError(f"Could not resolve channel ID from HTML for URL {channel_url_or_id}")

def parse_youtube_date(lockup: dict, metadata: dict, now: datetime) -> str:
    # 1. Check for upcomingEventData
    upcoming_data = lockup.get('upcomingEventData') or metadata.get('upcomingEventData')
    if upcoming_data and upcoming_data.get('startTime'):
        try:
            return datetime.fromtimestamp(int(upcoming_data['startTime']), timezone.utc).strftime('%Y-%m-%d')
        except Exception:
            pass

    # 2. Extract all strings in metadata to look for "Premiere" or relative times
    def find_strings(o):
        if isinstance(o, str):
            yield o
        elif isinstance(o, dict):
            for v in o.values():
                yield from find_strings(v)
        elif isinstance(o, list):
            for v in o:
                yield from find_strings(v)

    all_strings = list(find_strings(metadata))
    
    # 3. Check for "Premiere" with date
    for s in all_strings:
        # German: Premiere am DD.MM.YY
        match = re.search(r'Premiere\s+am\s+(\d{2})\.(\d{2})\.(\d{2})', s, re.IGNORECASE)
        if match:
            return f"20{match.group(3)}-{match.group(2)}-{match.group(1)}"
        # English: Premieres on MM/DD/YY
        match = re.search(r'Premieres\s+on\s+(\d{1,2})/(\d{1,2})/(\d{2})', s, re.IGNORECASE)
        if match:
            return f"20{match.group(3)}-{match.group(1).zfill(2)}-{match.group(2).zfill(2)}"

    # 4. Check for relative time strings
    pub_text = ""
    metadata_lines = metadata.get('metadata', {}).get('contentMetadataViewModel', {}).get('metadataRows', [])
    for row in metadata_lines:
        for part in row.get('metadataParts', []):
            text = part.get('text', {}).get('content', '')
            if any(x in text for x in ['Vor', 'ago', 'Streamed', 'Gestreamt', 'hour', 'day', 'week', 'month', 'year', 'Minuten', 'Stunden', 'Tagen', 'Wochen', 'Monaten', 'Jahr']):
                pub_text = text
                break

    if pub_text:
        match = re.search(r'(\d+)\s+(day|Tag|hour|Stund|week|Woch|month|Monat)', pub_text, re.IGNORECASE)
        if match:
            val = int(match.group(1))
            unit = match.group(2).lower()
            if 'day' in unit or 'tag' in unit:
                dt = now - timedelta(days=val)
            elif 'week' in unit or 'woch' in unit:
                dt = now - timedelta(days=val * 7)
            elif 'month' in unit or 'monat' in unit:
                dt = now - timedelta(days=val * 30)
            elif 'hour' in unit or 'stund' in unit:
                dt = now
            return dt.strftime('%Y-%m-%d')
        elif 'yesterday' in pub_text.lower() or 'gestern' in pub_text.lower():
            return (now - timedelta(days=1)).strftime('%Y-%m-%d')
        elif any(x in pub_text.lower() for x in ['just now', 'gerade eben', 'minute', 'stunde', 'hour']):
            return now.strftime('%Y-%m-%d')

    return "Unknown"

def fetch_youtube_videos_via_scraping(channel_url_or_id: str) -> list[dict]:
    # Formulate /videos URL
    if channel_url_or_id.startswith(("http://", "https://")):
        url = channel_url_or_id.rstrip("/") + "/videos"
    else:
        url = f"https://www.youtube.com/channel/{channel_url_or_id}/videos"

    print(f"Scraping YouTube channel /videos page: {url}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Error scraping YouTube channel: {e}")
        return []

    # Find ytInitialData
    match = re.search(r'ytInitialData\s*=\s*({.+?});', html)
    if not match:
        print("Warning: ytInitialData not found in YouTube channel HTML.")
        return []

    try:
        data = json.loads(match.group(1))
    except Exception as e:
        print(f"Error parsing ytInitialData JSON: {e}")
        return []

    # Find all lockupViewModel objects
    def find_key(obj, target_key):
        if isinstance(obj, dict):
            if target_key in obj:
                yield obj[target_key]
            for val in obj.values():
                yield from find_key(val, target_key)
        elif isinstance(obj, list):
            for val in obj:
                yield from find_key(val, target_key)

    lockups = list(find_key(data, 'lockupViewModel'))
    print(f"Found {len(lockups)} lockupViewModel objects in YouTube page.")

    # Determine channel name
    channel_name = "YouTube"
    header = data.get('header', {})
    if isinstance(header, dict):
        page_header = header.get('pageHeaderRenderer') or header.get('pageHeaderViewModel')
        if isinstance(page_header, dict):
            page_title = page_header.get('pageTitle', {})
            if isinstance(page_title, dict):
                title_obj = page_title.get('title', {})
                if isinstance(title_obj, dict):
                    title_run = title_obj.get('runs', [{}])
                    if isinstance(title_run, list) and title_run:
                        channel_name = title_run[0].get('text', channel_name)

    now = datetime.now(timezone.utc)
    # Reference datetime from context local time to prevent relative dates moving in the future during simulation
    # The current local time is: 2026-06-29
    reference_now = datetime(2026, 6, 29, tzinfo=timezone.utc)

    videos = []
    for l in lockups:
        metadata = l.get('metadata', {}).get('lockupMetadataViewModel', {})
        title = metadata.get('title', {}).get('content', 'Untitled Video')
        vid = l.get('contentId')
        if not vid:
            continue

        published_date = parse_youtube_date(l, metadata, reference_now)
        videos.append({
            "title": title,
            "link": f"https://youtu.be/{vid}",
            "source": f"YouTube ({channel_name})",
            "published_date": published_date,
        })
    return videos

def fetch_youtube(channels: list[str], dynamic_sources: list[str] = None):
    all_videos = []
    
    # Check static channels
    for chan in channels:
        videos = fetch_youtube_videos_via_scraping(chan)
        all_videos.extend(videos)

    # Process dynamic sources directly (user supplied video URLs)
    if dynamic_sources:
        print(f"Processing {len(dynamic_sources)} dynamic sources...")
        for src in dynamic_sources:
            src = src.strip()
            if not src:
                continue
            # If it's a direct YouTube video URL, we can add it as a candidate directly
            # We can extract the video ID or treat it as a general candidate link
            if "youtube.com" in src or "youtu.be" in src:
                # Resolve video ID
                video_id = ""
                if "youtu.be/" in src:
                    video_id = src.split("youtu.be/")[-1].split("?")[0]
                elif "v=" in src:
                    video_id = src.split("v=")[-1].split("&")[0]
                
                title = f"Manual YouTube Source ({video_id})" if video_id else src
                all_videos.append({
                    "title": title,
                    "link": src,
                    "source": "Manual",
                    "published_date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
                })
            else:
                # General dynamic link
                all_videos.append({
                    "title": f"Manual Source ({src})",
                    "link": src,
                    "source": "Manual",
                    "published_date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
                })

    output_file = INPUT_DIR / "youtube_feed.json"
    if not all_videos:
        print("No videos fetched from any channel.")
        if output_file.exists():
            output_file.unlink()
        return True

    # 30-day window filter (excluding manual additions)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=30)

    filtered_videos = []
    for video in all_videos:
        pub_str = video["published_date"]
        if pub_str == "Unknown" or video["source"] == "Manual":
            # Keep manual additions and unknown dates (for human curation)
            filtered_videos.append(video)
            continue
        try:
            dt = datetime.strptime(pub_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if dt >= cutoff:
                filtered_videos.append(video)
        except Exception as e:
            print(f"Skipping video '{video['title']}' due to date parsing error: {e}")

    # Deduplicate by link
    unique_videos = []
    seen_links = set()
    for video in filtered_videos:
        if video["link"] not in seen_links:
            seen_links.add(video["link"])
            unique_videos.append(video)

    payload = {"publications": unique_videos}
    output_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Successfully wrote {len(unique_videos)} entries to {output_file.relative_to(BASE_DIR)}")
    return True

# ==========================================
# Main CLI Entry Point
# ==========================================

def main():
    ensure_dirs()
    parser = argparse.ArgumentParser(description="Ingress tool for fetching raw ME/CFS research feeds.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommand to run")

    # Email command
    subparsers.add_parser("emails", help="Ingest unseen emails from Gmail inbox")

    # Reddit command
    subparsers.add_parser("reddit", help="Fetch and parse latest entries from Reddit feeds")

    # YouTube command
    yt_parser = subparsers.add_parser("youtube", help="Fetch and parse latest videos from YouTube channels")
    yt_parser.add_argument("--channel", action="append", dest="channels", default=[], help="YouTube channel ID or URL to check. Can specify multiple times.")
    yt_parser.add_argument("--add-source", action="append", dest="add_sources", default=[], help="Dynamically add a specific source URL to include in this run.")

    # All command
    all_parser = subparsers.add_parser("all", help="Fetch from all sources (emails, reddit, and YouTube channels)")
    all_parser.add_argument("--channel", action="append", dest="channels", default=[], help="YouTube channel ID or URL. Can specify multiple times.")
    all_parser.add_argument("--add-source", action="append", dest="add_sources", default=[], help="Dynamically add a specific source URL to include in this run.")

    args = parser.parse_args()

    if args.command == "emails":
        fetch_emails()
    elif args.command == "reddit":
        fetch_reddit()
    elif args.command == "youtube":
        fetch_youtube(args.channels, args.add_sources)
    elif args.command == "all":
        print("--- Ingesting Emails ---")
        fetch_emails()
        print("\n--- Ingesting Reddit ---")
        fetch_reddit()
        print("\n--- Ingesting YouTube ---")
        fetch_youtube(args.channels, args.add_sources)

if __name__ == "__main__":
    main()

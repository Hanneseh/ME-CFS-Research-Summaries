import json
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

# Base Directories
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "agent" / "input"
OUTPUT_FILE = INPUT_DIR / "reddit_feed.json"

# Feeds Configuration
FEEDS = [
    "https://www.reddit.com/r/CFSScience/.rss",
    "https://www.reddit.com/search.rss?q=MECFS+conference+daratumumab&sort=new",
]

# Unique, descriptive User-Agent to avoid Reddit rate-limits
USER_AGENT = "ME-CFS-Research-Curation-Bot/1.0 (contact: hannes.ehringfeld@gmail.com)"


def parse_iso_datetime(dt_str: str) -> datetime:
    """Parse ISO 8601 date strings into timezone-aware datetime objects."""
    normalized = dt_str.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def extract_outbound_link(content_html: str, reddit_link: str) -> str:
    """
    Extract the outbound scientific paper/source URL from the HTML content block.
    Outbound links are absolute HTTP/HTTPS links not pointing to reddit.com, redd.it, or redditmedia.com.
    Falls back to reddit_link if no external outbound link is found.
    """
    if not content_html:
        return reddit_link

    soup = BeautifulSoup(content_html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("http://", "https://")):
            href_lower = href.lower()
            # Ignore Reddit-internal domains (profiles, comments, media servers, etc.)
            if not any(
                domain in href_lower
                for domain in ["reddit.com", "redditmedia.com", "redd.it"]
            ):
                return href
    return reddit_link


def clean_html_content(content_html: str) -> str:
    """Clean the HTML content block into a plain-text representation."""
    if not content_html:
        return ""

    soup = BeautifulSoup(content_html, "html.parser")

    # Remove metadata links (like [link], [comments]) added by Reddit's feed
    for a in soup.find_all("a"):
        text = a.get_text().strip()
        if text in ("[link]", "[comments]"):
            a.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def fetch_and_parse_feed(url: str) -> list[dict]:
    """Fetch feed XML and parse Atom entries."""
    print(f"Fetching feed: {url}")
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
    except urllib.error.HTTPError as e:
        print(f"HTTP Error fetching feed {url}: {e.code} {e.reason}")
        return []
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
        title = (
            title_elem.text.strip()
            if title_elem is not None and title_elem.text
            else "Untitled"
        )

        # Extract post/comments Reddit Link
        reddit_link = ""
        links = entry.findall("atom:link", namespaces)
        for link in links:
            href = link.attrib.get("href")
            if href:
                rel = link.attrib.get("rel")
                # alternate/default link usually represents the post resource
                if rel == "alternate" or not rel:
                    reddit_link = href.strip()
                    break
        if not reddit_link and links:
            href = links[0].attrib.get("href")
            if href:
                reddit_link = href.strip()

        updated_elem = entry.find("atom:updated", namespaces)
        updated_str = (
            updated_elem.text.strip()
            if updated_elem is not None and updated_elem.text
            else ""
        )

        content_elem = entry.find("atom:content", namespaces)
        content_html = content_elem.text if content_elem is not None else ""

        outbound_link = extract_outbound_link(content_html, reddit_link)
        cleaned_content = clean_html_content(content_html)

        parsed_entries.append(
            {
                "title": title,
                "reddit_link": reddit_link,
                "updated_str": updated_str,
                "outbound_link": outbound_link,
                "content": cleaned_content,
            }
        )

    print(f"Successfully parsed {len(parsed_entries)} entries from {url}")
    return parsed_entries


def main():
    # Ensure input directory exists
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Delete the old, unused output file reddit_feed.md if it exists
    old_md_file = INPUT_DIR / "reddit_feed.md"
    if old_md_file.exists():
        try:
            old_md_file.unlink()
            print(f"Deleted legacy output file: {old_md_file.name}")
        except Exception as e:
            print(f"Error deleting legacy output file: {e}")

    all_entries = []
    for url in FEEDS:
        entries = fetch_and_parse_feed(url)
        all_entries.extend(entries)

    if not all_entries:
        print("No entries fetched from any feed.")
        if OUTPUT_FILE.exists():
            OUTPUT_FILE.unlink()
            print(f"Removed stale {OUTPUT_FILE.name}")
        return

    # Check entries against the 30-day rolling window
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
        if OUTPUT_FILE.exists():
            OUTPUT_FILE.unlink()
            print(f"Removed stale {OUTPUT_FILE.name}")
        print("Exiting gracefully.")
        return

    # Deduplicate entries by outbound link (or reddit link if fallback) to ensure unique publications.
    # Sort entries by parsed date descending to retain the newest info when deduplicating.
    filtered_entries.sort(key=lambda x: x["parsed_date"], reverse=True)

    unique_entries = []
    seen_links = set()
    for entry in filtered_entries:
        # Use outbound link for deduplication when available, falling back to reddit link
        link_to_check = entry["outbound_link"] or entry["reddit_link"]
        if link_to_check not in seen_links:
            seen_links.add(link_to_check)
            unique_entries.append(entry)

    print(f"Found {len(unique_entries)} unique entries within the 30-day window.")

    # Format unique entries as a structured JSON payload matching Stage1Output
    publications = []
    for entry in unique_entries:
        publications.append(
            {
                "title": entry["title"],
                "link": entry["outbound_link"] or entry["reddit_link"] or None,
                "source": "Reddit",
            }
        )

    payload = {"publications": publications}

    try:
        OUTPUT_FILE.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Successfully wrote {len(unique_entries)} entries to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing to output file {OUTPUT_FILE}: {e}")
        exit(1)


if __name__ == "__main__":
    main()

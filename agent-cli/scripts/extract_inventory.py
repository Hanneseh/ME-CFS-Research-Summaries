#!/usr/bin/env python
from __future__ import annotations

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONTENT_DIR = BASE_DIR / "content"
OUTPUT_FILE = BASE_DIR / "agent-cli" / "state" / "existing_sources_cache.json"

def extract_youtube_id(url: str) -> str | None:
    # Match common YouTube URL patterns and extract 11-char video ID
    # https://youtu.be/VIDEO_ID
    # https://www.youtube.com/watch?v=VIDEO_ID
    # https://www.youtube.com/embed/VIDEO_ID
    # https://www.youtube.com/live/VIDEO_ID
    # https://www.youtube.com/shorts/VIDEO_ID
    match = re.search(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|live/|shorts/))([A-Za-z0-9_-]{11})', url)
    if match:
        return match.group(1)
    return None

def normalize_url(url: str) -> str:
    url = url.strip()
    # Remove fragment and query parameters
    url = url.split('#')[0].split('?')[0]
    # Remove trailing slash
    url = url.rstrip('/')
    return url.lower()

def main():
    print(f"Scanning markdown files in: {CONTENT_DIR.relative_to(BASE_DIR)}")
    
    urls = set()
    youtube_ids = set()
    
    # Walk content directory
    for path in CONTENT_DIR.glob("**/*.md"):
        if not path.is_file():
            continue
        # Skip homepage index
        if path.name == "index.md" and path.parent == CONTENT_DIR:
            continue
            
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"Error reading {path}: {e}")
            continue
            
        # Find all markdown links [text](url)
        links = re.findall(r'\[[^\]]*\]\((https?://[^\s)]+)\)', text)
        # Find raw urls in text
        raw_urls = re.findall(r'(https?://[^\s\)]+)', text)
        
        for url in links + raw_urls:
            yt_id = extract_youtube_id(url)
            if yt_id:
                youtube_ids.add(yt_id)
            else:
                urls.add(normalize_url(url))

    print(f"Extracted {len(urls)} unique standard URLs and {len(youtube_ids)} unique YouTube Video IDs.")
    
    # Save cache
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "urls": sorted(list(urls)),
        "youtube_ids": sorted(list(youtube_ids))
    }
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved cache to: {OUTPUT_FILE.relative_to(BASE_DIR)}")

if __name__ == "__main__":
    main()

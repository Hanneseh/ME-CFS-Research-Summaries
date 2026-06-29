#!/usr/bin/env python
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "agent-cli" / "input"
STATE_DIR = BASE_DIR / "agent-cli" / "state"

CACHE_FILE = STATE_DIR / "existing_sources_cache.json"
EMAILS_FILE = STATE_DIR / "email_publications.json"
REDDIT_FILE = INPUT_DIR / "reddit_feed.json"
YOUTUBE_FILE = INPUT_DIR / "youtube_feed.json"

RAW_CANDIDATES_FILE = STATE_DIR / "raw_candidates.json"

def extract_youtube_id(url: str) -> str | None:
    match = re.search(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|live/|shorts/))([A-Za-z0-9_-]{11})', url)
    if match:
        return match.group(1)
    return None

def normalize_url(url: str) -> str:
    url = url.strip()
    url = url.split('#')[0].split('?')[0]
    url = url.rstrip('/')
    return url.lower()

def load_json_list(file_path: Path) -> list[dict]:
    if not file_path.exists():
        return []
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "publications" in data:
            return data["publications"]
        elif isinstance(data, list):
            return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return []

def main():
    # 1. Load cited sources inventory cache
    if not CACHE_FILE.exists():
        print("Error: existing_sources_cache.json not found. Run extract_inventory.py first.")
        return
        
    cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    existing_urls = set(cache.get("urls", []))
    existing_youtube_ids = set(cache.get("youtube_ids", []))
    
    # 2. Gather candidates from all feeds
    raw_candidates = []
    
    # Load Reddit
    reddit_pubs = load_json_list(REDDIT_FILE)
    for p in reddit_pubs:
        raw_candidates.append({
            "title": p.get("title", "No Title"),
            "link": p.get("link", ""),
            "source": "Reddit",
            "published_date": p.get("published_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        })
        
    # Load YouTube
    youtube_pubs = load_json_list(YOUTUBE_FILE)
    for p in youtube_pubs:
        raw_candidates.append({
            "title": p.get("title", "No Title"),
            "link": p.get("link", ""),
            "source": p.get("source", "YouTube"),
            "published_date": p.get("published_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        })
        
    # Load Emails
    email_pubs = load_json_list(EMAILS_FILE)
    for p in email_pubs:
        raw_candidates.append({
            "title": p.get("title", "No Title"),
            "link": p.get("link", ""),
            "source": p.get("source", "Email Alert"),
            "published_date": p.get("published_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        })

    print(f"Total raw staged candidates from all feeds: {len(raw_candidates)}")

    # 3. Deterministic Pre-Filtering
    filtered_candidates = []
    seen_urls = set()
    seen_yt_ids = set()
    
    exact_duplicates_skipped = 0
    cross_feed_duplicates_skipped = 0
    
    for c in raw_candidates:
        url = c["link"]
        if not url:
            filtered_candidates.append(c)
            continue
            
        normalized = normalize_url(url)
        yt_id = extract_youtube_id(url)
        
        # Check against existing cited sources
        is_already_cited = False
        if yt_id:
            if yt_id in existing_youtube_ids:
                is_already_cited = True
        else:
            if normalized in existing_urls:
                is_already_cited = True
                
        if is_already_cited:
            exact_duplicates_skipped += 1
            continue
            
        # Check against already processed items in this run
        is_seen = False
        if yt_id:
            if yt_id in seen_yt_ids:
                is_seen = True
            else:
                seen_yt_ids.add(yt_id)
        else:
            if normalized in seen_urls:
                is_seen = True
            else:
                seen_urls.add(normalized)
                
        if is_seen:
            cross_feed_duplicates_skipped += 1
            continue
            
        filtered_candidates.append(c)

    print(f"Skipped {exact_duplicates_skipped} exact duplicates already cited in the garden.")
    print(f"Skipped {cross_feed_duplicates_skipped} duplicates within the new staged feeds.")
    print(f"Remaining unique candidates for curation: {len(filtered_candidates)}")

    # Save raw candidates
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_CANDIDATES_FILE.write_text(json.dumps(filtered_candidates, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote unique candidates to: {RAW_CANDIDATES_FILE.relative_to(BASE_DIR)}")

if __name__ == "__main__":
    main()

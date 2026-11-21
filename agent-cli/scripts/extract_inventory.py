#!/usr/bin/env python
from __future__ import annotations

import json
import re

from atomic_content import (
    BASE_DIR,
    CONTENT_DIR,
    entry_paths,
    external_markdown_links,
    read_yaml,
    thread_directories,
)

OUTPUT_FILE = BASE_DIR / "agent-cli" / "state" / "existing_sources_cache.json"


def extract_youtube_id(url: str) -> str | None:
    # Match common YouTube URL patterns and extract 11-char video ID
    # https://youtu.be/VIDEO_ID
    # https://www.youtube.com/watch?v=VIDEO_ID
    # https://www.youtube.com/embed/VIDEO_ID
    # https://www.youtube.com/live/VIDEO_ID
    # https://www.youtube.com/shorts/VIDEO_ID
    match = re.search(
        r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|live/|shorts/))([A-Za-z0-9_-]{11})",
        url,
    )
    if match:
        return match.group(1)
    return None


def normalize_url(url: str) -> str:
    url = url.strip()
    # Remove fragment and query parameters
    url = url.split("#")[0].split("?")[0]
    # Remove trailing slash
    url = url.rstrip("/")
    return url.lower()


def main() -> None:
    print(
        f"Scanning atomic entries in: {CONTENT_DIR.relative_to(BASE_DIR) / 'threads'}"
    )
    paths = [
        path
        for thread in thread_directories(CONTENT_DIR)
        for path in entry_paths(thread)
    ]
    if not paths:
        raise SystemExit("No atomic entry files found")

    urls = set()
    youtube_ids = set()
    for path in paths:
        entry = read_yaml(path)
        sources = [source["url"] for source in entry["sources"]]
        for language in ("en", "de"):
            sources.extend(
                url for _, url in external_markdown_links(entry[language]["detail"])
            )
        for url in sources:
            if youtube_id := extract_youtube_id(url):
                youtube_ids.add(youtube_id)
            else:
                urls.add(normalize_url(url))

    print(
        f"Extracted {len(urls)} unique standard URLs and {len(youtube_ids)} unique YouTube Video IDs."
    )
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {"urls": sorted(urls), "youtube_ids": sorted(youtube_ids)}
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved cache to: {OUTPUT_FILE.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()

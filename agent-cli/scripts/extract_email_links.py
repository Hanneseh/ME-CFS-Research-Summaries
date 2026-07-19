#!/usr/bin/env python
"""Deterministic extraction of candidate paper links from raw alert .eml files.

Step 1.5 helper: parses each email, pulls the HTML part, extracts outbound
paper/registry links (resolving Google Scholar redirect wrappers from the URL
itself, no network), captures anchor text as a title candidate, and writes a
raw link list for downstream relevance screening.
"""
from __future__ import annotations

import email
import glob
import html
import json
import re
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

BASE = Path(__file__).resolve().parents[2]
EMAIL_DIR = BASE / "agent-cli" / "input" / "emails"
OUT = BASE / "agent-cli" / "state" / "email_raw_links.json"

# Domains we treat as candidate primary sources / registries.
DIRECT_HOST_HINTS = (
    "doi.org", "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov", "sciencedirect.com",
    "mdpi.com", "frontiersin.org", "nature.com", "biorxiv.org", "medrxiv.org",
    "springer.com", "wiley.com", "tandfonline.com", "bmj.com", "cell.com",
    "jamanetwork.com", "thelancet.com", "plos.org", "oup.com", "sagepub.com",
    "clinicaltrials.gov", "researchsquare.com", "ssrn.com", "preprints.org",
    "journals.rcsi.science", "academic.oup.com", "karger.com", "physiology.org",
    "ahajournals.org", "jci.org", "elifesciences.org", "pnas.org",
)

SKIP_HOST_SUBSTR = (
    "scholar.google", "google.com/alerts", "googlealerts", "accounts.google",
    "support.google", "youtube.com", "google.com/scholar_share",
    "sciencedirect.com/customer", "sciencedirect.com/user", "unsubscribe",
    "ncbi.nlm.nih.gov/account", "ncbi.nlm.nih.gov/sites", "myncbi",
    "facebook.com", "twitter.com", "x.com", "linkedin.com",
)


def get_html(msg) -> str:
    parts = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                try:
                    parts.append(part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="replace"))
                except Exception:
                    pass
    else:
        if msg.get_content_type() == "text/html":
            try:
                parts.append(msg.get_payload(decode=True).decode(
                    msg.get_content_charset() or "utf-8", errors="replace"))
            except Exception:
                pass
    return "\n".join(parts)


def resolve_scholar(url: str) -> str:
    """If a Google Scholar redirect wrapper, pull the embedded real url."""
    p = urlparse(url)
    if "scholar.google" in p.netloc and "scholar_url" in p.path:
        q = parse_qs(p.query)
        if "url" in q:
            return unquote(q["url"][0])
    if "google.com" in p.netloc and p.path == "/url":
        q = parse_qs(p.query)
        for k in ("q", "url"):
            if k in q:
                return unquote(q[k][0])
    return url


def looks_direct(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    if any(s in url.lower() for s in SKIP_HOST_SUBSTR):
        return False
    return any(h in host for h in DIRECT_HOST_HINTS)


ANCHOR_RE = re.compile(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")


def clean_text(t: str) -> str:
    return html.unescape(TAG_RE.sub(" ", t)).strip()


def main() -> None:
    items = []
    for f in sorted(glob.glob(str(EMAIL_DIR / "*.eml"))):
        with open(f, "rb") as fh:
            msg = email.message_from_binary_file(fh)
        try:
            date = parsedate_to_datetime(msg.get("Date", "")).strftime("%Y-%m-%d")
        except Exception:
            date = None
        frm = str(msg.get("From", ""))
        if "scholar" in frm.lower():
            source = "Google Scholar Alert"
        elif "ncbi" in frm.lower():
            source = "PubMed Alert"
        elif "sciencedirect" in frm.lower():
            source = "ScienceDirect Alert"
        elif "googlealerts" in frm.lower() or "Google Alerts" in frm:
            source = "Google Alert"
        else:
            source = "Email Alert"
        html_body = get_html(msg)
        for href, text in ANCHOR_RE.findall(html_body):
            url = resolve_scholar(html.unescape(href))
            if not looks_direct(url):
                continue
            title = clean_text(text)
            if len(title) < 8:
                continue
            items.append({
                "title": title,
                "link": url.split("?utm")[0].split("&utm")[0],
                "source": source,
                "published_date": date,
                "source_email": Path(f).name,
            })
    # de-dup by (normalized link) keeping first, and by title
    seen = set()
    deduped = []
    for it in items:
        key = it["link"].rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)
    OUT.write_text(json.dumps({"raw_link_count": len(items),
                               "unique_link_count": len(deduped),
                               "links": deduped}, indent=2), encoding="utf-8")
    print(f"Parsed {len(glob.glob(str(EMAIL_DIR / '*.eml')))} emails")
    print(f"Extracted {len(items)} candidate links, {len(deduped)} unique")
    print(f"Wrote {OUT.relative_to(BASE)}")


if __name__ == "__main__":
    main()

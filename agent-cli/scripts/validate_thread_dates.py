#!/usr/bin/env python
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONTENT_DIR = BASE_DIR / "content"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMELINE_HEADING_RE = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})\b", re.MULTILINE)


@dataclass(frozen=True)
class ThreadDateIssue:
    path: Path
    expected: str
    current_date: str | None
    current_last_updated: str | None


def split_frontmatter(text: str) -> tuple[str, str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    return text[:4], text[4:end], text[end:]


def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", frontmatter, flags=re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip("\"'")


def set_frontmatter_value(frontmatter: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^({re.escape(key)}:\s*).*$", flags=re.MULTILINE)
    if pattern.search(frontmatter):
        return pattern.sub(rf"\g<1>{value}", frontmatter)
    return f"{frontmatter.rstrip()}\n{key}: {value}\n"


def timeline_body(markdown_body: str) -> str:
    match = re.search(r"^##\s+Timeline\s*$", markdown_body, flags=re.MULTILINE)
    if not match:
        return ""
    next_section = re.search(r"^##\s+", markdown_body[match.end() :], flags=re.MULTILINE)
    if not next_section:
        return markdown_body[match.end() :]
    return markdown_body[match.end() : match.end() + next_section.start()]


def newest_timeline_date(markdown_body: str) -> str | None:
    dates = TIMELINE_HEADING_RE.findall(timeline_body(markdown_body))
    return max(dates) if dates else None


def iter_thread_pages(content_dir: Path) -> list[Path]:
    pages = []
    for path in sorted(content_dir.glob("*/*/index.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        parsed = split_frontmatter(text)
        if not parsed:
            continue
        _, frontmatter, _ = parsed
        if frontmatter_value(frontmatter, "thread_status"):
            pages.append(path)
    return pages


def validate_page(path: Path) -> ThreadDateIssue | None:
    text = path.read_text(encoding="utf-8")
    parsed = split_frontmatter(text)
    if not parsed:
        return None
    _, frontmatter, rest = parsed
    expected = newest_timeline_date(rest)
    if not expected:
        return None
    current_date = frontmatter_value(frontmatter, "date")
    current_last_updated = frontmatter_value(frontmatter, "last_updated")
    if current_date == expected and current_last_updated == expected:
        return None
    return ThreadDateIssue(path, expected, current_date, current_last_updated)


def fix_page(issue: ThreadDateIssue) -> None:
    text = issue.path.read_text(encoding="utf-8")
    parsed = split_frontmatter(text)
    if not parsed:
        return
    prefix, frontmatter, suffix = parsed
    frontmatter = set_frontmatter_value(frontmatter, "date", issue.expected)
    frontmatter = set_frontmatter_value(frontmatter, "last_updated", issue.expected)
    issue.path.write_text(f"{prefix}{frontmatter}{suffix}", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate thread frontmatter dates against the newest Timeline entry date."
    )
    parser.add_argument("--content-dir", type=Path, default=DEFAULT_CONTENT_DIR)
    parser.add_argument("--fix", action="store_true", help="Rewrite date and last_updated when they drift.")
    args = parser.parse_args()

    issues = [issue for path in iter_thread_pages(args.content_dir) if (issue := validate_page(path))]

    if args.fix:
        for issue in issues:
            fix_page(issue)

    for issue in issues:
        rel = issue.path.relative_to(BASE_DIR)
        action = "fixed" if args.fix else "mismatch"
        print(
            f"{action}: {rel}: expected {issue.expected}, "
            f"date={issue.current_date}, last_updated={issue.current_last_updated}"
        )

    if issues and not args.fix:
        print(f"{len(issues)} thread date mismatch(es). Run with --fix to update frontmatter.")
        return 1

    print(f"checked {len(iter_thread_pages(args.content_dir))} thread page(s); {len(issues)} issue(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

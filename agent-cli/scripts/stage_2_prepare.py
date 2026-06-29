#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_STATE_DIR = BASE_DIR / "agent-cli" / "state"
DEFAULT_CONTENT_DIR = BASE_DIR / "content"

TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "si",
}


@dataclass(frozen=True)
class SourceIdentity:
    canonical_url: str
    doi: str | None
    pmid: str | None
    nct_id: str | None
    youtube_id: str | None


def normalize_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower().replace("&", " and ")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def stable_id(prefix: str, *parts: str) -> str:
    payload = "\n".join(part or "" for part in parts)
    return f"{prefix}_{hashlib.sha1(payload.encode('utf-8')).hexdigest()[:12]}"


def extract_youtube_id(value: str) -> str | None:
    if not value:
        return None
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value.strip()):
        return value.strip()
    parsed = urlparse(value)
    host = parsed.netloc.lower().removeprefix("www.")
    if host in {"youtube.com", "m.youtube.com"}:
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if query.get("v") and re.fullmatch(r"[A-Za-z0-9_-]{11}", query["v"]):
            return query["v"]
        path_parts = [part for part in parsed.path.split("/") if part]
        if len(path_parts) >= 2 and path_parts[0] in {"embed", "live", "shorts"}:
            return path_parts[1]
    if host == "youtu.be":
        path_parts = [part for part in parsed.path.split("/") if part]
        if path_parts:
            return path_parts[0]
    return None


def extract_doi(value: str) -> str | None:
    if not value:
        return None
    decoded = value.replace("%2F", "/").replace("%2f", "/")
    patterns = [
        r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)",
        r"/content/(?:early/)?(?:\d{4}/\d{2}/\d{2}/)?(\d{4}\.\d{2}\.\d{2}\.\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, decoded, flags=re.IGNORECASE)
        if match:
            doi = match.group(1).rstrip(").,;")
            if doi.startswith("20") and "." in doi:
                # bioRxiv/medRxiv manuscript IDs are DOI suffixes under 10.1101.
                doi = f"10.1101/{doi}"
            return doi.lower()
    return None


def extract_pmid(value: str) -> str | None:
    match = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", value or "", flags=re.IGNORECASE)
    return match.group(1) if match else None


def extract_nct_id(value: str) -> str | None:
    match = re.search(r"\b(NCT\d{8})\b", value or "", flags=re.IGNORECASE)
    return match.group(1).upper() if match else None


def canonicalize_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""

    youtube_id = extract_youtube_id(value)
    if youtube_id:
        return f"https://youtu.be/{youtube_id}"

    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return value

    scheme = "https" if parsed.scheme in {"http", "https"} else parsed.scheme
    host = parsed.netloc.lower().removeprefix("www.")
    path = re.sub(r"/+", "/", parsed.path).rstrip("/")
    query_items = []
    for key, val in parse_qsl(parsed.query, keep_blank_values=True):
        lower_key = key.lower()
        if lower_key in TRACKING_QUERY_KEYS:
            continue
        if any(lower_key.startswith(prefix) for prefix in TRACKING_QUERY_PREFIXES):
            continue
        query_items.append((key, val))
    query = urlencode(query_items, doseq=True)
    return urlunparse((scheme, host, path, "", query, ""))


def identity_for(title: str, link: str) -> SourceIdentity:
    searchable = f"{title or ''} {link or ''}"
    canonical_url = canonicalize_url(link)
    return SourceIdentity(
        canonical_url=canonical_url,
        doi=extract_doi(searchable),
        pmid=extract_pmid(searchable),
        nct_id=extract_nct_id(searchable),
        youtube_id=extract_youtube_id(link),
    )


def source_type_for(source: str, title: str, link: str) -> str:
    text = f"{source} {title} {link}".lower()
    if "youtu" in text or "konferenz" in text or "conference" in text or "symposium" in text:
        return "conference_or_video"
    if "reddit" in source.lower():
        return "social_or_reddit_wrapper"
    if "x.com/" in link or "twitter.com/" in link or "skywriter.blue" in link:
        return "social_or_reddit_wrapper"
    if any(token in text for token in ["trial", "randomised", "randomized", "protocol", "registry", "nct"]):
        return "trial_or_protocol"
    if any(token in text for token in ["news", "awards", "funding", "project launch"]):
        return "news_or_infrastructure"
    if any(token in text for token in ["review", "statement", "guideline", "leitfaden", "chapter"]):
        return "review_or_guideline"
    return "paper_or_preprint"


def wrapper_kind_for(source: str, link: str) -> str:
    host = urlparse(link or "").netloc.lower().removeprefix("www.")
    if source.lower() == "reddit" or "reddit.com" in host:
        return "reddit_wrapper"
    if host in {"x.com", "twitter.com", "skywriter.blue", "bsky.app"}:
        return "social_post"
    if "news" in host or host.endswith("edu") and "/news" in (link or ""):
        return "news_article"
    if "youtu" in host:
        return "conference_video"
    return "direct_source"


def read_json_list(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "publications" in data:
        data = data["publications"]
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list or publications object in {path}")
    return data


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", text)


def timeline_sections(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^###\s+(.+)$", text, flags=re.MULTILINE))
    sections = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((heading, text[start:end]))
    return sections


def load_existing_inventory(content_dir: Path) -> list[dict]:
    inventory: list[dict] = []
    for path in sorted(content_dir.glob("**/index.md")):
        if path == content_dir / "index.md":
            continue
        rel = path.relative_to(content_dir)
        parts = rel.parts
        if len(parts) < 3:
            continue
        thread_group = parts[0]
        thread_slug = parts[1]
        text = path.read_text(encoding="utf-8", errors="replace")
        for heading, section_text in timeline_sections(text):
            heading_title = re.sub(r"^\S+\s+-\s+", "", heading).strip()
            heading_ident = identity_for(heading_title, "")
            inventory.append(
                {
                    "source_id": stable_id("existing", str(rel), heading),
                    "kind": "timeline_heading",
                    "title": heading_title,
                    "title_normalized": normalize_title(heading_title),
                    "link": "",
                    "canonical_url": "",
                    "doi": heading_ident.doi,
                    "pmid": heading_ident.pmid,
                    "nct_id": heading_ident.nct_id,
                    "youtube_id": heading_ident.youtube_id,
                    "thread_group": thread_group,
                    "thread_slug": thread_slug,
                    "content_path": str(path.relative_to(BASE_DIR)),
                    "timeline_heading": heading,
                }
            )
            for label, url in extract_markdown_links(section_text):
                ident = identity_for(f"{heading_title} {label}", url)
                inventory.append(
                    {
                        "source_id": stable_id("existing", str(rel), heading, label, url),
                        "kind": "timeline_source_link",
                        "title": heading_title,
                        "title_normalized": normalize_title(heading_title),
                        "link_label": label.strip(),
                        "link": url,
                        "canonical_url": ident.canonical_url,
                        "doi": ident.doi,
                        "pmid": ident.pmid,
                        "nct_id": ident.nct_id,
                        "youtube_id": ident.youtube_id,
                        "thread_group": thread_group,
                        "thread_slug": thread_slug,
                        "content_path": str(path.relative_to(BASE_DIR)),
                        "timeline_heading": heading,
                    }
                )
    return inventory


def normalize_candidates(candidates: list[dict]) -> list[dict]:
    normalized = []
    for idx, item in enumerate(candidates, start=1):
        title = str(item.get("title") or "Untitled").strip()
        link = str(item.get("link") or "").strip()
        source = str(item.get("source") or "Unknown").strip()
        ident = identity_for(title, link)
        normalized.append(
            {
                "candidate_id": stable_id("cand", title, link, source),
                "ingress_order": idx,
                "title": title,
                "title_normalized": normalize_title(title),
                "link": link,
                "canonical_url": ident.canonical_url,
                "doi": ident.doi,
                "pmid": ident.pmid,
                "nct_id": ident.nct_id,
                "youtube_id": ident.youtube_id,
                "source": source,
                "source_type": source_type_for(source, title, link),
                "wrapper_kind": wrapper_kind_for(source, link),
                "published_date": item.get("published_date") or "",
            }
        )
    return normalized


def strong_keys(record: dict) -> list[str]:
    keys = []
    for field in ("doi", "pmid", "nct_id", "youtube_id", "canonical_url"):
        value = record.get(field)
        if value:
            keys.append(f"{field}:{value}")
    return keys


def build_existing_indexes(inventory: list[dict]) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    by_key: dict[str, list[dict]] = defaultdict(list)
    by_title: dict[str, list[dict]] = defaultdict(list)
    for source in inventory:
        for key in strong_keys(source):
            by_key[key].append(source)
        if source.get("title_normalized"):
            by_title[source["title_normalized"]].append(source)
    return by_key, by_title


def top_title_matches(title_normalized: str, inventory: list[dict], *, limit: int = 3) -> list[dict]:
    if not title_normalized:
        return []
    matches = []
    for source in inventory:
        existing_title = source.get("title_normalized") or ""
        if len(existing_title) < 12:
            continue
        score = SequenceMatcher(None, title_normalized, existing_title).ratio()
        if score >= 0.78:
            matches.append(
                {
                    "score": round(score, 3),
                    "source_id": source["source_id"],
                    "title": source["title"],
                    "thread_slug": source["thread_slug"],
                    "content_path": source["content_path"],
                    "kind": source["kind"],
                }
            )
    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:limit]


def attach_matches(candidates: list[dict], inventory: list[dict]) -> list[dict]:
    by_key, by_title = build_existing_indexes(inventory)
    enriched = []
    for candidate in candidates:
        exact_matches = []
        for key in strong_keys(candidate):
            exact_matches.extend(by_key.get(key, []))
        title_matches = by_title.get(candidate["title_normalized"], [])
        fuzzy_matches = top_title_matches(candidate["title_normalized"], inventory)

        seen = set()
        compact_exact = []
        for match in exact_matches + title_matches:
            if match["source_id"] in seen:
                continue
            seen.add(match["source_id"])
            compact_exact.append(
                {
                    "source_id": match["source_id"],
                    "kind": match["kind"],
                    "title": match["title"],
                    "thread_slug": match["thread_slug"],
                    "content_path": match["content_path"],
                    "match_basis": "strong_key_or_exact_title",
                }
            )

        deterministic_status = "needs_semantic_review"
        if compact_exact:
            deterministic_status = "existing_source_match"
        elif candidate["wrapper_kind"] in {"reddit_wrapper", "social_post", "news_article"}:
            deterministic_status = "wrapper_needs_source_resolution"

        item = dict(candidate)
        item["existing_matches"] = compact_exact
        item["possible_existing_matches"] = fuzzy_matches
        item["deterministic_status"] = deterministic_status
        enriched.append(item)
    return enriched


def cluster_key_for(candidate: dict) -> str:
    for field in ("doi", "pmid", "nct_id", "youtube_id", "canonical_url"):
        value = candidate.get(field)
        if value:
            return f"{field}:{value}"
    title = candidate.get("title_normalized") or "untitled"
    return f"title:{title}"


def title_tokens(title_normalized: str) -> set[str]:
    stopwords = {"a", "an", "and", "in", "of", "on", "for", "the", "to", "with"}
    return {token for token in title_normalized.split() if len(token) > 2 and token not in stopwords}


def titles_are_near_duplicates(left: str, right: str) -> bool:
    if not left or not right:
        return False
    if min(len(left), len(right)) < 45:
        return False
    if left == right:
        return True
    ratio = SequenceMatcher(None, left, right).ratio()
    if ratio >= 0.9:
        return True
    shorter, longer = sorted([left, right], key=len)
    if shorter in longer and len(shorter) / len(longer) >= 0.62:
        return True
    left_tokens = title_tokens(left)
    right_tokens = title_tokens(right)
    if min(len(left_tokens), len(right_tokens)) < 6:
        return False
    overlap = len(left_tokens & right_tokens) / min(len(left_tokens), len(right_tokens))
    return overlap >= 0.86 and ratio >= 0.78


def assign_theme(candidate: dict) -> str:
    text = f"{candidate.get('title', '')} {candidate.get('source_type', '')}".lower()
    if candidate["source_type"] == "conference_or_video":
        return "conference_video"
    if any(term in text for term in ["daratumumab", "immunoadsorption", "hyperbaric", "naltrexone", "rapamycin", "vagus", "trial", "therapy", "treatment", "pharmacologic", "drug"]):
        return "treatments_interventions"
    if any(term in text for term in ["diagnos", "biomarker", "machine learning", "scale", "questionnaire", "classification", "symptom profile", "epidemiology", "guideline", "care", "severe"]):
        return "diagnostics_symptoms_care"
    if any(term in text for term in ["genetic", "genome", "mitochond", "immune", "autoantibod", "microclot", "vascular", "endothel", "neuroinflammation", "brain", "gut", "microbiome", "viral", "herpes", "metabolic", "pots", "autonomic"]):
        return "disease_models_mechanisms"
    return "general_review"


def build_clusters(candidates: list[dict]) -> list[dict]:
    parent = {candidate["candidate_id"]: candidate["candidate_id"] for candidate in candidates}

    def find(candidate_id: str) -> str:
        while parent[candidate_id] != candidate_id:
            parent[candidate_id] = parent[parent[candidate_id]]
            candidate_id = parent[candidate_id]
        return candidate_id

    def union(left: str, right: str) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    connected_keys: dict[str, str] = {}
    for candidate in candidates:
        keys = strong_keys(candidate)
        if candidate.get("title_normalized"):
            keys.append(f"title:{candidate['title_normalized']}")
        for key in keys:
            existing_candidate_id = connected_keys.get(key)
            if existing_candidate_id:
                union(existing_candidate_id, candidate["candidate_id"])
            else:
                connected_keys[key] = candidate["candidate_id"]

    for left_index, left in enumerate(candidates):
        left_title = left.get("title_normalized") or ""
        for right in candidates[left_index + 1 :]:
            if titles_are_near_duplicates(left_title, right.get("title_normalized") or ""):
                union(left["candidate_id"], right["candidate_id"])

    groups: dict[str, list[dict]] = defaultdict(list)
    for candidate in candidates:
        groups[find(candidate["candidate_id"])].append(candidate)

    clusters = []
    for _, members in groups.items():
        members.sort(key=lambda item: item["ingress_order"])
        key = cluster_key_for(members[0])
        themes = Counter(assign_theme(member) for member in members)
        statuses = Counter(member["deterministic_status"] for member in members)
        exact_existing = []
        possible_existing = []
        for member in members:
            exact_existing.extend(member["existing_matches"])
            possible_existing.extend(member["possible_existing_matches"])

        exact_existing = list({item["source_id"]: item for item in exact_existing}.values())
        possible_existing = list({item["source_id"]: item for item in possible_existing}.values())
        cluster = {
            "cluster_id": stable_id("cluster", key),
            "cluster_key": key,
            "theme": themes.most_common(1)[0][0],
            "deterministic_status": statuses.most_common(1)[0][0],
            "member_count": len(members),
            "titles": sorted({member["title"] for member in members}),
            "sources": sorted({member["source"] for member in members}),
            "exact_existing_matches": exact_existing,
            "possible_existing_matches": possible_existing[:5],
            "members": members,
            "worker_decision": None,
        }
        clusters.append(cluster)
    clusters.sort(key=lambda item: (item["theme"], item["cluster_key"]))
    return clusters


def compact_cluster_for_worker(cluster: dict) -> dict:
    return {
        "cluster_id": cluster["cluster_id"],
        "theme": cluster["theme"],
        "deterministic_status": cluster["deterministic_status"],
        "member_count": cluster["member_count"],
        "titles": cluster["titles"],
        "sources": cluster["sources"],
        "exact_existing_matches": cluster["exact_existing_matches"],
        "possible_existing_matches": cluster["possible_existing_matches"],
        "members": [
            {
                "candidate_id": member["candidate_id"],
                "title": member["title"],
                "link": member["link"],
                "source": member["source"],
                "source_type": member["source_type"],
                "wrapper_kind": member["wrapper_kind"],
                "published_date": member["published_date"],
                "doi": member["doi"],
                "pmid": member["pmid"],
                "nct_id": member["nct_id"],
                "youtube_id": member["youtube_id"],
            }
            for member in cluster["members"]
        ],
    }


def write_worker_batches(clusters: list[dict], output_dir: Path, batch_size: int) -> list[Path]:
    if output_dir.exists():
        for path in output_dir.glob("*.json"):
            path.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    grouped: dict[str, list[dict]] = defaultdict(list)
    for cluster in clusters:
        grouped[cluster["theme"]].append(compact_cluster_for_worker(cluster))

    for theme, theme_clusters in sorted(grouped.items()):
        for index in range(0, len(theme_clusters), batch_size):
            batch_number = index // batch_size + 1
            batch_path = output_dir / f"{theme}_{batch_number:02d}.json"
            payload = {
                "batch_id": batch_path.stem,
                "theme": theme,
                "cluster_count": len(theme_clusters[index : index + batch_size]),
                "clusters": theme_clusters[index : index + batch_size],
            }
            batch_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            paths.append(batch_path)
    return paths


def write_report(path: Path, candidates: list[dict], clusters: list[dict], batches: list[Path]) -> None:
    status_counts = Counter(candidate["deterministic_status"] for candidate in candidates)
    source_counts = Counter(candidate["source"] for candidate in candidates)
    theme_counts = Counter(cluster["theme"] for cluster in clusters)
    lines = [
        "# Stage 2 Preparation Report",
        "",
        f"- Normalized candidates: {len(candidates)}",
        f"- Candidate clusters: {len(clusters)}",
        f"- Worker batch files: {len(batches)}",
        "",
        "## Candidate Sources",
        "",
    ]
    lines.extend(f"- {source}: {count}" for source, count in sorted(source_counts.items()))
    lines.extend(["", "## Deterministic Status", ""])
    lines.extend(f"- {status}: {count}" for status, count in sorted(status_counts.items()))
    lines.extend(["", "## Cluster Themes", ""])
    lines.extend(f"- {theme}: {count}" for theme, count in sorted(theme_counts.items()))
    lines.extend(["", "## Worker Batches", ""])
    lines.extend(f"- `{batch.relative_to(BASE_DIR)}`" for batch in batches)
    lines.extend(
        [
            "",
            "## Worker Reviews",
            "",
            "- Store Gemini/Antigravity review outputs under `agent-cli/state/worker_reviews/`.",
            "- Rerunning this preparation step rewrites deterministic batches but does not remove worker reviews.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare Stage 2 normalized candidates, global matches, clusters, and worker batches."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_STATE_DIR / "raw_candidates.json",
        help="Raw candidates JSON file. Default: agent-cli/state/raw_candidates.json",
    )
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=DEFAULT_CONTENT_DIR,
        help="Quartz content directory used to build existing-source inventory.",
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=DEFAULT_STATE_DIR,
        help="Directory for output state artifacts.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=25,
        help="Maximum clusters per worker batch file.",
    )
    parser.add_argument(
        "--batches-dir",
        type=Path,
        default=DEFAULT_STATE_DIR / "worker_batches",
        help="Directory for Gemini/Antigravity worker batch packets.",
    )
    parser.add_argument(
        "--worker-review-dir",
        type=Path,
        default=DEFAULT_STATE_DIR / "worker_reviews",
        help="Directory reserved for Gemini/Antigravity review outputs. It is created but never deleted.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.state_dir.mkdir(parents=True, exist_ok=True)
    args.worker_review_dir.mkdir(parents=True, exist_ok=True)

    raw_candidates = read_json_list(args.input)
    existing_inventory = load_existing_inventory(args.content_dir)
    normalized = normalize_candidates(raw_candidates)
    matched = attach_matches(normalized, existing_inventory)
    clusters = build_clusters(matched)

    inventory_path = args.state_dir / "existing_sources_inventory.json"
    normalized_path = args.state_dir / "normalized_candidates.json"
    clusters_path = args.state_dir / "candidate_clusters.json"
    report_path = args.state_dir / "stage_2_report.md"

    inventory_path.write_text(json.dumps(existing_inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    normalized_path.write_text(json.dumps(matched, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    clusters_path.write_text(json.dumps(clusters, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    batches = write_worker_batches(clusters, args.batches_dir, args.batch_size)
    write_report(report_path, matched, clusters, batches)

    print(f"Wrote existing inventory: {inventory_path.relative_to(BASE_DIR)}")
    print(f"Wrote normalized candidates: {normalized_path.relative_to(BASE_DIR)}")
    print(f"Wrote candidate clusters: {clusters_path.relative_to(BASE_DIR)}")
    print(f"Wrote worker batches: {args.batches_dir.relative_to(BASE_DIR)} ({len(batches)} files)")
    print(f"Wrote report: {report_path.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()

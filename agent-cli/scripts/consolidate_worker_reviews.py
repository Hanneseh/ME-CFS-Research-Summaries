#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import yaml


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_STATE_DIR = BASE_DIR / "agent-cli" / "state"
DEFAULT_RULES_FILE = BASE_DIR / "agent-cli" / "thread_content_rules.yaml"
DEFAULT_OVERRIDES_FILE = DEFAULT_STATE_DIR / "manual_overrides.json"

VALID_DECISIONS = {
    "new_source",
    "update_of_existing_thread",
    "update_of_existing_source",
    "duplicate",
    "exclude",
    "needs_human_review",
    "propose_new_thread",
}


def load_valid_thread_slugs(rules_file: Path) -> set[str]:
    rules = yaml.safe_load(rules_file.read_text(encoding="utf-8"))
    valid = set()
    for group in rules["thread_taxonomy"]["groups"].values():
        valid.update(group["threads"].keys())
    return valid


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_review_items(review_dir: Path) -> tuple[list[dict], list[str], dict[str, str]]:
    items: list[dict] = []
    skipped: list[str] = []
    safe_exclude_overrides: dict[str, str] = {}
    for path in sorted(review_dir.glob("*.json")):
        data = load_json(path)
        for item in data.get("safe_excludes", []):
            cluster_id = item.get("cluster_id")
            reason = item.get("reason")
            if cluster_id and reason:
                safe_exclude_overrides[cluster_id] = reason

        curated = data.get("curated_clusters")
        if not isinstance(curated, list):
            skipped.append(str(path.relative_to(BASE_DIR)))
            continue
        for item in curated:
            enriched = dict(item)
            enriched["review_file"] = str(path.relative_to(BASE_DIR))
            enriched["batch_id"] = data.get("batch_id")
            enriched["model"] = data.get("model")
            items.append(enriched)
    return items, skipped, safe_exclude_overrides


def load_manual_overrides(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    data = load_json(path)
    overrides = data.get("overrides", [])
    if not isinstance(overrides, list):
        raise ValueError(f"Expected overrides list in {path}")
    return {
        item["cluster_id"]: item
        for item in overrides
        if isinstance(item, dict) and item.get("cluster_id")
    }


def validate_items(items: list[dict], valid_threads: set[str]) -> list[dict]:
    errors = []
    seen_cluster_ids = set()
    for item in items:
        cluster_id = item.get("cluster_id")
        if not cluster_id:
            errors.append({"error": "missing_cluster_id", "item": item})
        elif cluster_id in seen_cluster_ids:
            errors.append({"error": "duplicate_cluster_review", "cluster_id": cluster_id})
        else:
            seen_cluster_ids.add(cluster_id)

        decision = item.get("decision")
        if decision not in VALID_DECISIONS:
            errors.append({"error": "invalid_decision", "cluster_id": cluster_id, "decision": decision})

        for field in ("primary_thread",):
            slug = item.get(field)
            if slug and slug not in valid_threads:
                errors.append({"error": "invalid_thread_slug", "cluster_id": cluster_id, "field": field, "slug": slug})

        for slug in item.get("secondary_threads") or []:
            if slug not in valid_threads:
                errors.append({"error": "invalid_thread_slug", "cluster_id": cluster_id, "field": "secondary_threads", "slug": slug})
    return errors


def build_work_items(
    clusters: list[dict],
    review_items: list[dict],
    skipped_review_files: list[str],
    validation_errors: list[dict],
    safe_exclude_overrides: dict[str, str],
    manual_overrides: dict[str, dict],
) -> dict:
    by_cluster_id = {cluster["cluster_id"]: cluster for cluster in clusters}
    by_review_cluster_id = {item["cluster_id"]: item for item in review_items if item.get("cluster_id")}
    missing_review_cluster_ids = sorted(set(by_cluster_id) - set(by_review_cluster_id))
    extra_review_cluster_ids = sorted(set(by_review_cluster_id) - set(by_cluster_id))

    work_items = []
    for cluster_id, review in sorted(by_review_cluster_id.items()):
        cluster = by_cluster_id.get(cluster_id)
        decision = review.get("decision")
        exclusion_reason = review.get("exclusion_reason")
        primary_thread = review.get("primary_thread")
        secondary_threads = review.get("secondary_threads") or []
        source_resolution_notes = review.get("source_resolution_notes")
        if cluster_id in safe_exclude_overrides:
            decision = "exclude"
            exclusion_reason = safe_exclude_overrides[cluster_id]
            primary_thread = None
            secondary_threads = []
            source_resolution_notes = (
                f"Overridden by global safe-exclude audit. Batch worker decision was: "
                f"{review.get('decision')}."
            )
        if cluster_id in manual_overrides:
            override = manual_overrides[cluster_id]
            decision = override.get("decision", decision)
            exclusion_reason = override.get("exclusion_reason", exclusion_reason)
            primary_thread = override.get("primary_thread")
            secondary_threads = override.get("secondary_threads") or []
            source_resolution_notes = override.get(
                "source_resolution_notes",
                f"Manual override applied. Batch worker decision was: {review.get('decision')}.",
            )
        work_items.append(
            {
                "cluster_id": cluster_id,
                "decision": decision,
                "canonical_candidate_id": review.get("canonical_candidate_id"),
                "duplicate_candidate_ids": review.get("duplicate_candidate_ids") or [],
                "exclusion_reason": exclusion_reason,
                "primary_thread": primary_thread,
                "secondary_threads": secondary_threads,
                "takeaway_summary": review.get("takeaway_summary"),
                "source_resolution_notes": source_resolution_notes,
                "batch_id": review.get("batch_id"),
                "review_file": review.get("review_file"),
                "cluster_theme": cluster.get("theme") if cluster else None,
                "candidate_ids": [member["candidate_id"] for member in cluster.get("members", [])] if cluster else [],
            }
        )

    decision_counts = Counter(item["decision"] for item in work_items)
    return {
        "status": "partial" if missing_review_cluster_ids else "complete",
        "cluster_count": len(clusters),
        "reviewed_cluster_count": len(by_review_cluster_id),
        "missing_review_cluster_ids": missing_review_cluster_ids,
        "extra_review_cluster_ids": extra_review_cluster_ids,
        "skipped_review_files": skipped_review_files,
        "safe_exclude_override_count": len(safe_exclude_overrides),
        "manual_override_count": len(manual_overrides),
        "validation_errors": validation_errors,
        "decision_counts": dict(sorted(decision_counts.items())),
        "work_items": work_items,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and consolidate Gemini worker curation reviews.")
    parser.add_argument(
        "--clusters",
        type=Path,
        default=DEFAULT_STATE_DIR / "candidate_clusters.json",
        help="Candidate clusters JSON generated by stage_2_prepare.py.",
    )
    parser.add_argument(
        "--review-dir",
        type=Path,
        default=DEFAULT_STATE_DIR / "worker_reviews",
        help="Directory containing worker review JSON files.",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=DEFAULT_RULES_FILE,
        help="Thread content rules YAML.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_STATE_DIR / "work_items.json",
        help="Consolidated work items JSON output path.",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=DEFAULT_OVERRIDES_FILE,
        help="Manual override JSON file for human decisions.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    clusters = load_json(args.clusters)
    if not isinstance(clusters, list):
        raise ValueError(f"Expected cluster list in {args.clusters}")

    valid_threads = load_valid_thread_slugs(args.rules)
    review_items, skipped_review_files, safe_exclude_overrides = load_review_items(args.review_dir)
    manual_overrides = load_manual_overrides(args.overrides)
    validation_errors = validate_items(review_items, valid_threads)
    payload = build_work_items(
        clusters,
        review_items,
        skipped_review_files,
        validation_errors,
        safe_exclude_overrides,
        manual_overrides,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote consolidated work items: {args.output.relative_to(BASE_DIR)}")
    print(f"Status: {payload['status']}")
    print(f"Reviewed clusters: {payload['reviewed_cluster_count']} / {payload['cluster_count']}")
    print(f"Validation errors: {len(validation_errors)}")
    if validation_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

# Agent CLI

Working area for the new thread-first local agent system.

This directory is separate from the legacy `agent/` pipeline. The legacy `agent/`
directory remains useful as reference for the old ingestion and summary flow, but
new Antigravity/Codex-driven thread maintenance work should live here.

## Contents

- `thread_content_rules.yaml` - machine-readable content rules for thread pages,
  source notes, source verification, dates, links, and video-source handling.
- `scripts/` - deterministic helper scripts used for bounded source checks.

## Current Tools

Run Python tools through Poetry from the repository root.

Prepare normalized Stage 2 artifacts after `raw_candidates.json` exists:

```bash
poetry run python agent-cli/scripts/stage_2_prepare.py
```

This writes:

- `agent-cli/state/existing_sources_inventory.json`
- `agent-cli/state/normalized_candidates.json`
- `agent-cli/state/candidate_clusters.json`
- `agent-cli/state/worker_batches/*.json`
- `agent-cli/state/stage_2_report.md`

Use `agent-cli/state/worker_batches/*.json` as bounded Antigravity/Gemini
inputs. Store worker outputs in `agent-cli/state/worker_reviews/`; rerunning
Stage 2 rewrites deterministic batches but does not delete review outputs.

Validate and consolidate worker review outputs:

```bash
poetry run python agent-cli/scripts/consolidate_worker_reviews.py
```

This writes `agent-cli/state/work_items.json`, validates decision values and
thread slugs, and applies any global `safe_excludes` audit overrides found in
`agent-cli/state/worker_reviews/*.json`.

Fetch a YouTube transcript segment without using Gemini:

```bash
poetry run python agent-cli/scripts/youtube_video_summary.py "https://youtu.be/VIDEO_ID" --start 297 --end 357
```

Summarize a bounded transcript segment with Gemini:

```bash
poetry run python agent-cli/scripts/youtube_video_summary.py "https://youtu.be/VIDEO_ID" --start 297 --end 357 --topic "daratumumab ResetME update" --summarize
```

The YouTube tool is only for video-source checking. Prefer direct papers,
registries, abstracts, official pages, and written reports when those are the
best available source material.

## Public Thread Structure

Public content should converge toward an index-only Quartz folder model:

- group page: `content/<thread-group>/index.md`
- thread page: `content/<thread-group>/<thread-slug>/index.md`
- no public per-source pages inside thread folders

Thread pages should include `cssclasses: [thread-page]`. This hides Quartz's
empty child-page listing on thread folders while preserving folder listings on
group pages.

## Intended Direction

Future additions should include:

- deterministic Python helpers for source inventories, link checks, and
  frontmatter validation
- review reports produced by worker agents

Codex remains the management agent: it decides the next slice, applies final
edits, and validates the repository. Worker agents should be used for bounded
source reading, clustering, extraction, and draft generation.

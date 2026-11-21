# Ingestion & Validation Scripts

Local helper scripts for collecting new research alerts, deduplicating sources against the existing corpus, and validating the bilingual YAML content before building the site.

## Contents

- `thread_content_rules.yaml` — machine-readable taxonomy, classification policy, and bilingual atomic YAML schema rules.
- `scripts/` — deterministic Python helpers for source intake, inventory extraction, deduplication, and strict Pydantic content validation.
- `state/` — gitignored temporary directory used during a single intake run.

## Commands

Run Python tools through Poetry from the repository root.

### 1. Ingest raw alerts & feeds

```bash
poetry run python agent-cli/ingress.py all --channel <YOUTUBE_CHANNEL_URL_OR_ID> --add-source <URL>
```

### 2. Extract existing source inventory & pre-filter

`extract_inventory.py` and `stage_2_prepare.py` read structured `sources[]` and titles directly from `content/threads/*/entries/*.yaml`:

```bash
poetry run python agent-cli/scripts/extract_inventory.py
poetry run python agent-cli/scripts/pre_filter.py
poetry run python agent-cli/scripts/stage_2_prepare.py
```

### 3. Consolidate review outputs

```bash
poetry run python agent-cli/scripts/consolidate_worker_reviews.py
```

### 4. Validate content & build site

```bash
poetry run python agent-cli/scripts/validate_content.py --require-bilingual
poetry run python agent-cli/scripts/validate_thread_dates.py
npm run check
npm run build
```

## Atomic Content Layout

```text
content/
  groups.yaml
  glossary.yaml
  threads/
    <thread-slug>/
      thread.yaml
      entries/
        YYYY-MM-DD_<entry-slug>.yaml
```

- Adding a new study creates one YAML file under `content/threads/<slug>/entries/` containing both `en` and `de` fields (`title`, `plain_summary`, `detail`) and structured `sources[]`.
- Update `thread.yaml` only when new evidence materially changes the synthesis.
- Thread `last_updated` dates are derived automatically from `max(entry.date)`.
- Use `[Label](thread:<slug>)` for cross-thread links in prose.
- Remove `agent-cli/state/` and `agent-cli/input/` before committing.

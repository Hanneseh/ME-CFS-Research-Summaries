# Ingestion & Validation Scripts

Local helper scripts for collecting new research alerts, deduplicating sources against the existing corpus, and validating the bilingual YAML content before building the site.

## Contents

- `thread_content_rules.yaml` — machine-readable taxonomy, classification policy, and bilingual atomic YAML schema rules.
- `scripts/` — deterministic Python helpers for source intake, inventory extraction, deduplication, and strict Pydantic content validation.
- `state/` — gitignored temporary directory used during a single intake run.

## Commands

Install uv, then run `uv sync --locked` from the repository root.

### 1. Ingest raw alerts & feeds

```bash
uv run --locked python agent-cli/ingress.py all --channel <YOUTUBE_CHANNEL_URL_OR_ID> --add-source <URL>
```

### 2. Extract existing source inventory & pre-filter

`extract_inventory.py` and `stage_2_prepare.py` read structured `sources[]` and titles directly from `content/threads/*/entries/*.yaml`:

```bash
uv run --locked python agent-cli/scripts/extract_inventory.py
uv run --locked python agent-cli/scripts/pre_filter.py
uv run --locked python agent-cli/scripts/stage_2_prepare.py
```

### 3. Consolidate review outputs

```bash
uv run --locked python agent-cli/scripts/consolidate_worker_reviews.py
```

### 4. Validate content & build site

```bash
uv run --locked python agent-cli/scripts/validate_content.py --require-bilingual
uv run --locked python agent-cli/scripts/validate_thread_dates.py
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
  updates/
    YYYY-MM-DD.yaml
```

- Adding a new study creates one YAML file under `content/threads/<slug>/entries/` containing both `en` and `de` fields (`title`, `plain_summary`, `detail`) and structured `sources[]`.
- Update `thread.yaml` only when new evidence materially changes the synthesis.
- Thread `last_updated` dates are derived automatically from `max(entry.date)`.
- Use `[Label](thread:<slug>)` for cross-thread links in prose.
- Remove `agent-cli/state/` and `agent-cli/input/` before committing.

### Update briefings

Use `content/updates/YYYY-MM-DD.yaml` to summarize a reporting period across threads. Quote `id`, `date`, `period_from`, and `period_to` as ISO dates. Set `id` to the filename stem and keep `period_from` on or before `period_to`.

- List at least one record in `added_entries` with `thread`, `entry_id`, and `action` (`added` or `upgraded`). Each thread and entry pair may occur once in this list.
- Provide `title`, `lead`, `highlights`, and `what_to_skip_or_caveats` in both `en` and `de`. Use the same number of highlights in each language. Each highlight has `tag`, `title`, `summary`, and `links`.
- Each highlight link uses `thread` and `entry_id`. References in highlights and `added_entries` must resolve to `content/threads/<thread>/entries/<entry_id>.yaml`. Use canonical thread links in prose and omit legacy relative links.
- The content validator checks every briefing in the optional `content/updates/` directory. Pass `--require-bilingual` to require all briefing text fields to be filled in.

<p align="center">
  <a href="https://hanneseh.github.io/ME-CFS-Research-Summaries/">
    <img alt="GitHub Pages" src="https://github.com/Hanneseh/ME-CFS-Research-Summaries/actions/workflows/deploy.yml/badge.svg">
  </a>
  <a href="https://astro.build/">
    <img alt="Astro" src="https://img.shields.io/badge/Built%20with-Astro%205-bc52ee?logo=astro&logoColor=white">
  </a>
  <a href="https://docs.pydantic.dev/">
    <img alt="Pydantic" src="https://img.shields.io/badge/Validation-Pydantic-e92063?logo=pydantic&logoColor=white">
  </a>
  <a href="LICENSE">
    <img alt="License" src="https://img.shields.io/badge/License-CC0%201.0-lightgray?logo=creative-commons">
  </a>
</p>

# ME/CFS Research Summaries

A bilingual (**German & English**), thread-first static research tracker for ME/CFS and closely related post-viral research.

Its goal is to reduce noise and surface what is actually moving in the field — **accessible for patients, caregivers, and families** through plain-language summaries, while keeping **full scientific detail, caveats, and direct primary source links** one click away.

- **Live site:** [hanneseh.github.io/ME-CFS-Research-Summaries](https://hanneseh.github.io/ME-CFS-Research-Summaries/)
- **German:** `/de/` · **English:** `/en/`

## How the Site Is Organized

1. **Two-layer readability:** Every research thread and every entry pairs a short, jargon-free **plain-language summary** (*Kurz erklärt* / *In Plain Terms*) with full **technical detail**, explicit limitations, and direct links to primary papers, trial registries, and conference talks.
2. **Latest Feed + Living Threads:** The homepage shows a reverse-chronological **Latest Research Feed** alongside living research threads across three groups (*Treatments & Interventions*, *Disease Models & Mechanisms*, *Diagnostics, Symptoms & Care*).
3. **Low-glare, accessible reading:** Built for limited cognitive bandwidth and light sensitivity — clean typography, automatic and toggleable dark mode, mobile-first layout, progressive disclosure, instant client-side search, and a bilingual glossary.
4. **Atomic content files:** Every thread synthesis lives in `thread.yaml` and every individual study or milestone lives in its own small YAML file under `entries/`, validated with Pydantic.

## Content Structure

```text
content/
  groups.yaml                                    # Thread groups (EN + DE)
  glossary.yaml                                  # Evidence tiers & key terms (EN + DE)
  threads/
    <thread-slug>/
      thread.yaml                                # Metadata + bilingual synthesis (EN + DE)
      entries/
        YYYY-MM-DD_<entry-slug>.yaml             # Atomic research entry (EN + DE + sources[])
  updates/
    YYYY-MM-DD.yaml                             # Optional bilingual update briefing
```

- Thread `last_updated` dates are derived automatically from the newest entry date at build time.
- Internal cross-thread links in prose use `[Label](thread:<slug>)`, resolved automatically to the active language.
- Legacy URLs (`/treatments-interventions/<slug>/`, etc.) redirect automatically so existing bookmarks and shared links keep working.

## Adding New Research

New studies, trial registrations, and conference updates are collected periodically from journal alerts, preprints, and research feeds, deduplicated against existing `sources[]`, screened for relevance and evidence quality, and added as individual bilingual YAML entries under `content/threads/<slug>/entries/`. A thread's `thread.yaml` synthesis (`plain_summary`, `takeaway`, `state_of_evidence`, `open_questions`) is updated only when new findings materially change the overall picture.

An update briefing in `content/updates/YYYY-MM-DD.yaml` covers a reporting period and summarizes newly added or upgraded entries, with highlights and caveats in German and English. Briefing references point to existing entries. See the [briefing format](agent-cli/README.md#update-briefings) for the required fields.

## Local Development & Validation

```bash
# Install site dependencies
npm install

# Install Python dependencies and enable the repository hook
uv sync --locked
git config --local core.hooksPath .githooks

# Check the Python tooling
make codegate
uv run --locked deptry agent-cli

# Validate all bilingual YAML content (schema, dates, URLs, cross-links, EN/DE completeness)
uv run --locked python agent-cli/scripts/validate_content.py --require-bilingual

# Typecheck & build static site to dist/
npm run check
npm run build

# Start local dev server
npm run dev
```

The pre-commit hook runs `make codegate` against the staged files.

Pushing to `main` builds and deploys the static site automatically via GitHub Actions (`.github/workflows/deploy.yml`).

## Disclaimer & License

These pages are curated research synthesis notes created with AI assistance and are **not medical advice**. Synthesis notes are released under [CC0 1.0 Universal](LICENSE); linked original papers remain under their respective authors' and publishers' copyrights.

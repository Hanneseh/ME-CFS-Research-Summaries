# ME/CFS Research Tagging Taxonomy

This document defines the strict tagging taxonomy for the ME/CFS Research Summaries project. These tags are used in the YAML frontmatter of each research summary to enable structured navigation and filtering in the Digital Garden.

## Primary Tags

Each study should be assigned one or more of the following tags:

- `⭐ Landmark`: **Landmark Studies.** Use this for high-impact, groundbreaking, or exceptionally promising research. These are the studies that provide significant hope to the community (e.g., successful trial of a potent medication, discovery of a major disease mechanism in a high-impact journal like Nature/Science).
- `💊 Treatment`: **Clinical Trials & Therapies.** Use this for papers evaluating specific medical treatments, drug trials (even if small), or novel therapeutic approaches. 
- `🧪 Biomarker`: **Diagnostics & Testability.** Use this for research focusing on identifying physiological markers (DNA, blood markers, etc.) that can distinguish ME/CFS patients from healthy controls.
- `⏳ Trial`: **Ongoing & Upcoming Trials.** Use this for summaries of study platforms, trial designs, or links to clinicaltrials.gov for studies that haven't concluded yet.
- `📰 News`: **News⁄ & Reports.** Use this for conference reports, news articles, or summaries of events rather than direct scientific papers.
## Tagging Guidelines for the Agent

When classifying a paper, the agent should follow these priorities:

1.  **Context Matters**: If a study describes a biological mechanism BUT also tests a treatment, use both `biomarker` and `treatment`.
2.  **Evidence Strength**: Only use `starred` if the paper represents a major leap forward, not just for every "interesting" result.
3.  **Treatment vs. Trial**: If a paper reports *results* of a finished trial, use `treatment`. If it only announces the *design* of a future trial, use `trial`.
4.  **News**: If the source is a news outlet (e.g., ScienceDaily) or a conference summary rather than a peer-reviewed journal paper, use `news`.

## YAML Format

```yaml
---
title: "Article Title"
date: YYYY-MM-DD
tags:
  - ⭐ Landmark
  - 🧪 Biomarker
---
```

# ME/CFS Research Tagging Taxonomy

This document defines the strict tagging taxonomy for the ME/CFS Research Summaries project. These tags are used in the YAML frontmatter of each research summary to enable structured navigation and filtering in the Digital Garden.

## Primary Tags

Each study should be assigned one or more of the following tags:

- `⭐ Landmark`: **Landmark Studies.** Use this very sparingly for genuinely field-shifting work: a strong interventional signal in the target illness, a major mechanistic breakthrough with clear causal or translational weight, or unusually strong diagnostic progress. Most interesting papers are NOT landmark papers.
- `💊 Treatment`: **Clinical Trials & Therapies.** Use this for papers evaluating a specific intervention in ME/CFS, Long COVID with strong or strategically relevant post-viral overlap, or a tightly related autonomic/post-viral subgroup. Do NOT use it for generic reviews of supplements, broad management overviews, implausible alternative therapies, or purely speculative therapeutic discussions.
- `🧪 Biomarker`: **Diagnostics & Testability.** Use this for research that identifies or validates physiological markers with meaningful diagnostic, stratification, or provocation value. Do NOT use it for every generic association study or exploratory difference between patients and controls.
- `⏳ Trial`: **Ongoing & Upcoming Trials.** Use this for important ongoing trials or study protocols that could materially change treatment or diagnostics. Do NOT use it for minor protocol papers or loosely relevant observational study designs.
- `📰 News`: **News⁄ & Reports.** Use this for conference reports, news articles, funding announcements, project updates, or event summaries rather than direct scientific papers. This tag is valid and useful when the item gives patients meaningful orientation about research momentum.
## Tagging Guidelines for the Agent

When classifying a paper, the agent should follow these priorities:

1.  **Patient-Relevance First**: Tags should reflect what is materially useful for a patient/caregiver-facing research garden, not everything that is academically interesting.
2.  **Context Matters**: If a study describes a biological mechanism BUT also tests a treatment, use both `🧪 Biomarker` and `💊 Treatment` only if each tag is independently justified.
3.  **Evidence Strength**: Only use `⭐ Landmark` if the paper represents a major leap forward, not just an interesting signal, a routine review, a minor protocol, or a confirmatory finding. Some major reviews or major field-shaping news items can still qualify if they genuinely reorient the field.
4.  **Treatment vs. Trial**: If a paper reports *results* of a finished intervention study, use `💊 Treatment`. If it only announces the *design* of a future trial, use `⏳ Trial`. Protocol papers usually should NOT also receive `⭐ Landmark`.
5.  **Biomarker Restraint**: A paper that finds altered cytokines, metabolites, microbiome composition, imaging features, or autoantibodies should only receive `🧪 Biomarker` if the work moves toward diagnosis, stratification, or actionable mechanism.
6.  **News**: If the source is a news outlet, funding announcement, project page, or conference summary rather than a primary paper, use `📰 News`. Do not treat this tag as synonymous with "low value"; some news items are important because they show momentum, trial activity, or institutional recognition.
7.  **Low-Credibility Therapies**: Be highly conservative with `💊 Treatment` on herbal formulas, traditional medicine mixtures, vague supplements, or low-plausibility alternative therapies unless the evidence is unusually strong.

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

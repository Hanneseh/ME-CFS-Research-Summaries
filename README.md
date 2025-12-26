<p align="center">
    <a href="https://hanneseh.github.io/ME-CFS-Research-Summaries/">
        <img alt="GitHub Pages" src="https://github.com/Hanneseh/ME-CFS-Research-Summaries/actions/workflows/deploy.yml/badge.svg">
    </a>
    <a href="https://quartz.jzhao.xyz/">
        <img alt="Quartz" src="https://img.shields.io/badge/Powered%20by%20Quartz-4ea94b?logo=quartz&logoColor=white">
    <a href="https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Flash-Model-Card.pdf">
        <img alt="Gemini" src="https://img.shields.io/badge/AI-Gemini%203.0%20Flash-blue?logo=googlegemini&logoColor=white">
    </a>
    <a href="https://docs.pydantic.dev/">
        <img alt="Pydantic" src="https://img.shields.io/badge/Data%20Layer-Pydantic-e92063?logo=pydantic&logoColor=white">
    </a>
    <a href="#readme">
        <img alt="Python Version" src="https://img.shields.io/badge/Python-3.13-purple?logo=python">
    </a>
    <a href="https://python-poetry.org/">
        <img alt="Poetry" src="https://img.shields.io/badge/Built%20with%20Poetry-gold?style=flat&logo=poetry&labelColor=black">
    </a>
    <a href="LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-CC0%201.0-lightgray?logo=creative-commons">
    </a>
</p>

# ME/CFS Research Summaries

An automated pipeline and digital garden for processing and summarizing ME/CFS and Long COVID research. This project uses generative AI to bridge the gap between complex scientific publications and community accessibility.

## 🤖 How the Research Agent Works

This project uses a multi-stage AI agent to process research alerts. Each stage is a distinct Gemini API call with a specialized system prompt, Pydantic-enforced output schemas, and persistent state for fault-tolerant resumption.

```mermaid
flowchart LR
    subgraph Ingestion
        A["📧 Raw Input<br/>(Emails, Feeds)"]
    end

    subgraph Pipeline["Agent Pipeline (Gemini 3 Flash)"]
        direction LR
        S1["Stage 1<br/>Parse"] --> S2["Stage 2<br/>Dedupe"]
        S2 --> S3{"Stage 3<br/>Screen"}
        S3 -- Relevant --> S4["Stage 4<br/>Summarize"]
        S3 -- Excluded --> X["❌"]
        S4 --> S5["Stage 5<br/>Tag"]
    end

    subgraph Tools["Agentic Tools"]
        T1["🌍 Google Search"]
        T2["🔗 URL Context"]
    end

    subgraph Output
        O["🌿 Digital Garden<br/>(Quartz)"]
    end

    A --> S1
    S4 <-. grounding .-> Tools
    S5 --> O

    style Pipeline fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style Tools fill:#fffde7,stroke:#f9a825,stroke-width:1px,stroke-dasharray: 5 5
```

| Stage            | Purpose                                                               | Key Features                          |
| :--------------- | :-------------------------------------------------------------------- | :------------------------------------ |
| **1. Parse**     | Extracts structured paper metadata from raw email/feed data.          | EML/HTML parsing, `BeautifulSoup`     |
| **2. Dedupe**    | Compares new items against the existing corpus to prevent duplicates. | Fuzzy title matching                  |
| **3. Screen**    | Applies strict inclusion/exclusion criteria for ME/CFS relevance.     | Rule-based prompt, `is_relevant` flag |
| **4. Summarize** | Deep-dives into the paper using grounded tools.                       | **Google Search**, **URL Context**    |
| **5. Tag**       | Applies a consistent taxonomy to the final summary.                   | Version-controlled tagging schema     |

All intermediate state is persisted to `agent/state/`, making the pipeline **idempotent and resumable**.

## 📂 Project Structure
- `agent/`:
    - `research_agent.py`: Principal agent orchestration logic.
    - `prompts/`: Version-controlled system and input prompts.
    - `state/`: Persistent JSON state to allow safe job resumption.
- `content/summaries/`: Generated markdown summaries for the digital garden.
- `content/index.md`: The landing page of the public website.

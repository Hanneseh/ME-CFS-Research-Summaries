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

## 🏗️ Technical Architecture: The Research Agent

The core of this project is a multi-stage **Research Agent** implemented in `agent/research_agent.py`. It uses structured outputs and tool calling to automate research ingestion.

### Workflow Visualization

```mermaid
graph TD
    Input["Input Data (agent/input/)"] --> S1["Stage 1: Synthesis"]
    S1 -->|"Publication List"| S2["Stage 2: Deduplication"]
    S2 -->|"Unique Items"| S3["Stage 3: Screening"]
    
    subgraph "Agent Logic (Gemini 3 Flash)"
    S1
    S2
    S3
    S4["Stage 4: Extraction"]
    S5["Stage 5: Tagging"]
    end
    
    S3 -->|"Relevant"| S4
    S3 -->|"Irrelevant"| Excl["Excluded (agent/state/excluded/)"]
    
    S4 -->|"Structured Data"| S5
    S5 -->|"Markdown Files"| Content["Summaries (content/summaries/)"]
    
    Content --> Agg["Aggregator"]
    Agg --> Final["all_summaries.md"]
    
    subgraph "State Management"
    State["State (agent/state/*.json)"]
    end
    
    S1 -.-> State
    S2 -.-> State
    S3 -.-> State
    S4 -.-> State
```

### Pipeline Stages
1.  **Synthesis (Stage 1):** Processes messy sources (.eml, .md) into a structured list of potential publications using high-level "thinking" prompts.
2.  **Deduplication (Stage 2):** Compares new findings against existing files to ensure idempotency.
3.  **Screening (Stage 3):** Applies rigorous `inclusion_rules.md` to filter for ME/CFS-specific research.
4.  **Extraction (Stage 4):** Uses Google Search and URL context to find full texts, extracting deep metadata and generating summaries using Pydantic schemas.
5.  **Tagging (Stage 5):** Categorizes summaries based on a specialized [Research Tagging Taxonomy](agent/prompts/tagging_system.md).

## 📂 Project Structure
- `agent/`:
    - `research_agent.py`: Principal agent orchestration logic.
    - `prompts/`: Version-controlled system and input prompts.
    - `state/`: Persistent JSON state to allow safe job resumption.
- `content/summaries/`: Generated markdown summaries for the digital garden.
- `content/index.md`: The landing page of the public website.

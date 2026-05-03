import argparse
import asyncio
import csv
import json
import os
import re
import shlex
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


load_dotenv()

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content" / "summaries"
PROMPTS_DIR = BASE_DIR / "agent" / "prompts"
AUDIT_ROOT = BASE_DIR / ".agent" / "relevance_audits"

DEFAULT_MODEL_ID = "gemini-3-flash-preview"
DEFAULT_THINKING_LEVEL = "high"


class SummaryInput(BaseModel):
    file_path: str
    title: str
    link: str | None = None
    published: str | None = None
    tags: list[str] = Field(default_factory=list)
    markdown: str


class RelevanceAuditResult(BaseModel):
    file_path: str
    title: str
    decision: Literal["keep", "borderline", "remove"]
    is_relevant: bool
    confidence: float = Field(ge=0, le=1)
    patient_value_score: int = Field(ge=0, le=5)
    scientific_value_score: int = Field(ge=0, le=5)
    field_momentum_score: int = Field(ge=0, le=5)
    treatment_plausibility_score: int = Field(ge=0, le=5)
    overall_relevance_score: int = Field(ge=0, le=5)
    evidence_level: str
    primary_reason: str
    matched_inclusion_criteria: list[str] = Field(default_factory=list)
    matched_exclusion_criteria: list[str] = Field(default_factory=list)
    rationale: str
    what_would_be_lost_if_removed: str
    review_warning: str | None = None


def read_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def strip_yaml_frontmatter(markdown: str) -> tuple[dict[str, object], str]:
    if not markdown.startswith("---\n"):
        return {}, markdown

    end = markdown.find("\n---\n", 4)
    if end == -1:
        return {}, markdown

    raw = markdown[4:end]
    body = markdown[end + 5 :]
    metadata: dict[str, object] = {}
    current_key: str | None = None

    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("- ") and current_key:
            metadata.setdefault(current_key, [])
            if isinstance(metadata[current_key], list):
                metadata[current_key].append(line[2:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip().strip("'").strip('"')
            metadata[current_key] = value if value else []

    return metadata, body


def extract_link(markdown: str) -> str | None:
    match = re.search(r"\*\*Link:\*\*\s*\[[^\]]+\]\(([^)]+)\)", markdown)
    if match:
        return match.group(1)
    match = re.search(r"https?://[^\s)]+", markdown)
    if match:
        return match.group(0)
    return None


def load_summary(path: Path) -> SummaryInput:
    markdown = path.read_text(encoding="utf-8")
    metadata, body = strip_yaml_frontmatter(markdown)
    title = str(metadata.get("title") or path.stem)
    link = extract_link(markdown)
    tags = metadata.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    return SummaryInput(
        file_path=str(path.relative_to(BASE_DIR)),
        title=title,
        link=link,
        published=str(metadata.get("published") or metadata.get("created") or "") or None,
        tags=[str(tag) for tag in tags],
        markdown=body.strip(),
    )


def safe_result_name(file_path: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", file_path)[:180] + ".json"


def build_user_prompt(summary: SummaryInput) -> str:
    payload = summary.model_dump()
    return (
        "# Existing Summary Relevance Audit\n\n"
        "Evaluate this existing collection item under the current relevance criteria.\n\n"
        "<summary_payload>\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
        "</summary_payload>\n"
    )


async def audit_one(
    client: genai.Client,
    model_id: str,
    system_prompt: str,
    summary: SummaryInput,
    result_path: Path,
    force: bool,
) -> RelevanceAuditResult:
    if result_path.exists() and not force:
        return RelevanceAuditResult.model_validate_json(result_path.read_text(encoding="utf-8"))

    response = await client.aio.models.generate_content(
        model=model_id,
        contents=build_user_prompt(summary),
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=RelevanceAuditResult,
            tools=[
                types.Tool(google_search=types.GoogleSearch()),
                types.Tool(url_context=types.UrlContext()),
            ],
            thinking_config=types.ThinkingConfig(thinking_level=DEFAULT_THINKING_LEVEL),
        ),
    )

    result = RelevanceAuditResult.model_validate_json(response.text)
    result.file_path = summary.file_path
    result.title = summary.title
    result_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result


async def run_audit(args: argparse.Namespace) -> Path:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env or the shell environment.")

    run_dir = Path(args.run_dir).expanduser() if args.run_dir else AUDIT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
    if not run_dir.is_absolute():
        run_dir = BASE_DIR / run_dir
    results_dir = run_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    inclusion_rules = read_prompt("inclusion_rules.md")
    system_prompt = read_prompt("relevance_audit_system.md").replace(
        "{{INCLUSION_RULES}}", inclusion_rules
    )
    (run_dir / "system_prompt.md").write_text(system_prompt, encoding="utf-8")
    (run_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "model": args.model,
                "concurrency": args.concurrency,
                "limit": args.limit,
                "created_or_resumed_at": datetime.now().isoformat(timespec="seconds"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    summaries = [load_summary(path) for path in sorted(CONTENT_DIR.glob("*.md"))]
    if args.limit:
        summaries = summaries[: args.limit]

    client = genai.Client(api_key=api_key)
    sem = asyncio.Semaphore(args.concurrency)
    results: list[RelevanceAuditResult] = []

    async def worker(index: int, summary: SummaryInput) -> None:
        result_path = results_dir / safe_result_name(summary.file_path)
        async with sem:
            print(f"[{index}/{len(summaries)}] Auditing {summary.file_path}")
            try:
                result = await audit_one(
                    client=client,
                    model_id=args.model,
                    system_prompt=system_prompt,
                    summary=summary,
                    result_path=result_path,
                    force=args.force,
                )
                results.append(result)
                print(
                    f"[{index}/{len(summaries)}] {result.decision.upper()} "
                    f"score={result.overall_relevance_score} confidence={result.confidence:.2f}"
                )
            except Exception as exc:
                error_path = results_dir / (safe_result_name(summary.file_path) + ".error")
                error_path.write_text(str(exc), encoding="utf-8")
                print(f"[{index}/{len(summaries)}] ERROR {summary.file_path}: {exc}")

    await asyncio.gather(*(worker(i + 1, summary) for i, summary in enumerate(summaries)))

    results.sort(key=lambda item: (item.decision, item.overall_relevance_score, item.file_path))
    write_reports(run_dir, results)
    return run_dir


def write_reports(run_dir: Path, results: list[RelevanceAuditResult]) -> None:
    csv_path = run_dir / "relevance_spectrum.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "decision",
                "overall_relevance_score",
                "confidence",
                "patient_value_score",
                "scientific_value_score",
                "field_momentum_score",
                "treatment_plausibility_score",
                "evidence_level",
                "primary_reason",
                "file_path",
                "title",
                "rationale",
                "review_warning",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "decision": result.decision,
                    "overall_relevance_score": result.overall_relevance_score,
                    "confidence": result.confidence,
                    "patient_value_score": result.patient_value_score,
                    "scientific_value_score": result.scientific_value_score,
                    "field_momentum_score": result.field_momentum_score,
                    "treatment_plausibility_score": result.treatment_plausibility_score,
                    "evidence_level": result.evidence_level,
                    "primary_reason": result.primary_reason,
                    "file_path": result.file_path,
                    "title": result.title,
                    "rationale": result.rationale,
                    "review_warning": result.review_warning or "",
                }
            )

    grouped = {
        "remove": [item for item in results if item.decision == "remove"],
        "borderline": [item for item in results if item.decision == "borderline"],
        "keep": [item for item in results if item.decision == "keep"],
    }

    report_lines = [
        "# Relevance Audit Results",
        "",
        f"- Total reviewed: {len(results)}",
        f"- Keep: {len(grouped['keep'])}",
        f"- Borderline: {len(grouped['borderline'])}",
        f"- Remove: {len(grouped['remove'])}",
        "",
        "## Recommended Removals",
        "",
    ]

    for result in grouped["remove"]:
        report_lines.extend(format_result_block(result, include_command=True))

    report_lines.extend(["", "## Borderline", ""])
    for result in grouped["borderline"]:
        report_lines.extend(format_result_block(result, include_command=False))

    report_lines.extend(["", "## Keep", ""])
    for result in grouped["keep"]:
        report_lines.extend(format_result_block(result, include_command=False))

    (run_dir / "audit_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    delete_script = run_dir / "delete_recommended.sh"
    delete_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Review audit_report.md before running this file.",
    ]
    for result in grouped["remove"]:
        delete_lines.append(f"git rm -- {shlex.quote(result.file_path)}")
    delete_script.write_text("\n".join(delete_lines) + "\n", encoding="utf-8")
    delete_script.chmod(0o755)


def format_result_block(result: RelevanceAuditResult, include_command: bool) -> list[str]:
    lines = [
        f"### {result.file_path}",
        "",
        f"- Decision: `{result.decision}`",
        f"- Overall score: `{result.overall_relevance_score}/5`",
        f"- Confidence: `{result.confidence:.2f}`",
        f"- Evidence level: `{result.evidence_level}`",
        f"- Primary reason: `{result.primary_reason}`",
        f"- Rationale: {result.rationale}",
        f"- What would be lost: {result.what_would_be_lost_if_removed}",
    ]
    if result.review_warning:
        lines.append(f"- Review warning: {result.review_warning}")
    if include_command:
        lines.extend(["", "```bash", f"git rm -- {shlex.quote(result.file_path)}", "```"])
    lines.append("")
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retrospectively audit existing summaries against current relevance criteria."
    )
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="Re-run items with existing result JSON.")
    parser.add_argument(
        "--run-dir",
        default=None,
        help="Resume or write to an existing audit directory. Existing result JSON is reused unless --force is set.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    output_dir = asyncio.run(run_audit(parse_args()))
    print(f"\nAudit complete. Review outputs in: {output_dir}")

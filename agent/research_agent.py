import asyncio
import json
import os
import re
import email
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from difflib import SequenceMatcher

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Base Directories
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "agent" / "input"
STATE_DIR = BASE_DIR / "agent" / "state"
PROMPTS_DIR = BASE_DIR / "agent" / "prompts"
CONTENT_DIR = BASE_DIR / "content" / "summaries"
PROMPT_DUMP_DIR = BASE_DIR / "agent" / "debug_prompts"

# Configuration
DEBUG_PROMPTS = True

# State Files (Located in STATE_DIR)
STAGE_1_OUTPUT = STATE_DIR / "stage_1_output.json"
STAGE_2_OUTPUT = STATE_DIR / "stage_2_output.json"
STAGE_3_OUTPUT = STATE_DIR / "stage_3_output.json"
STAGE_4_DIR = STATE_DIR / "stage_4"  # Directory for individual Stage 4 results
EXCLUDED_DIR = STATE_DIR / "excluded"
INACCESSIBLE_DIR = STATE_DIR / "inaccessible"

# Ensure directories exist
for d in [
    INPUT_DIR,
    STATE_DIR,
    STAGE_4_DIR,
    EXCLUDED_DIR,
    INACCESSIBLE_DIR,
    CONTENT_DIR,
]:
    d.mkdir(parents=True, exist_ok=True)

if DEBUG_PROMPTS:
    PROMPT_DUMP_DIR.mkdir(parents=True, exist_ok=True)

# Thinking Levels
THINKING_LEVEL_STAGE_1 = "high"
THINKING_LEVEL_STAGE_2 = "high"
THINKING_LEVEL_STAGE_3 = "high"
THINKING_LEVEL_STAGE_4 = "high"

# Configure Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-3.5-flash"

# Pydantic Models for Structured Outputs


class PublicationItem(BaseModel):
    title: str
    link: Optional[str] = None
    source: Optional[str] = None


class Stage1Output(BaseModel):
    publications: List[PublicationItem]


class Stage2Output(BaseModel):
    unique_publications: List[PublicationItem]


class Stage3ScreeningResult(BaseModel):
    is_relevant: bool
    reason: str
    title: str
    link: Optional[str] = None


class Stage3Output(BaseModel):
    screened_publications: List[Stage3ScreeningResult]


class Stage4Result(BaseModel):
    is_accessible: bool = True
    title: str
    apa_summary_line: str = Field(description="Format: 'Author et al. (Year)'")
    authors: List[str]
    institutes: List[str]
    publisher: str
    link: Optional[str] = None
    published_date: Optional[str] = Field(None, description="YYYY-MM-DD")
    tags: List[str] = Field(
        default_factory=list,
        description="Strict list of matching taxonomy tags from the project rules: '⭐ Landmark', '💊 Treatment', '🧪 Biomarker', '⏳ Trial', '📰 News'",
    )

    # Body Content
    summary_impact: Optional[str] = Field(
        None, description="High-level impact paragraph. Length: 1-6 sentences."
    )
    what_was_researched: Optional[str] = Field(
        None,
        description="Central research question or objective. Length: 1-3 sentences.",
    )
    why_was_it_researched: Optional[str] = Field(
        None, description="Background and motivation. Length: 1-3 sentences."
    )
    how_was_it_researched: Optional[str] = Field(
        None,
        description="Methodology, study type, cohort details. Length: 1-5 sentences.",
    )
    what_has_been_found: Optional[str] = Field(
        None, description="Primary results and novel findings. Length: 1-5 sentences."
    )
    discussion: Optional[str] = Field(
        None,
        description="Limitations, strengths, or weaknesses. Length: 1-4 sentences.",
    )
    conclusion: Optional[str] = Field(
        None,
        description="Main conclusions and future research suggestions. Length: 1-3 sentences.",
    )


class ResearchAgent:
    def __init__(self):
        self.model_id = MODEL_ID

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=lambda retry_state: print(
            f"Temporary API connection or rate limit issue. Retrying in {retry_state.next_action.sleep:.1f} seconds..."
        ),
    )
    async def _generate_content_with_retry(self, *args, **kwargs):
        """Wrapper to generate content from Gemini with exponential back-off retries."""
        return await client.aio.models.generate_content(*args, **kwargs)

    def _read_prompt(self, name: str) -> str:
        path = PROMPTS_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8")

    def _clean_json_response(self, text: str) -> str:
        return re.sub(r"```(?:json)?\n?|\n?```", "", text).strip()

    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content using BeautifulSoup."""
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        # Remove scripts and styles
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Replace links with "Link Text (URL)"
        for a in soup.find_all("a"):
            href = a.get("href")
            if href:
                a.replace_with(f"{a.get_text()} ({href})")

        # Get text with better spacing
        text = soup.get_text(separator="\n")
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def _parse_eml(self, eml_content: str) -> str:
        """Extract text content from an email (EML) file."""
        msg = email.message_from_string(eml_content)
        text_parts = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True).decode(errors="replace")
                        text_parts.append(payload)
                    except Exception:
                        pass
                elif content_type == "text/html":
                    try:
                        html_payload = part.get_payload(decode=True).decode(
                            errors="replace"
                        )
                        text_parts.append(self._clean_html(html_payload))
                    except Exception:
                        pass
        else:
            content_type = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True).decode(errors="replace")
                if content_type == "text/html":
                    text_parts.append(self._clean_html(payload))
                else:
                    text_parts.append(payload)
            except Exception:
                pass

        return "\n".join(text_parts)

    def _save_debug_prompt(self, stage: str, system_prompt: str, user_prompt: str):
        """Save the full prompt payload to a markdown file for debugging."""
        if not DEBUG_PROMPTS:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}_{stage}.md"
        path = PROMPT_DUMP_DIR / filename

        content = f"# {stage.upper()} PROMPT DEBUG\n\n"
        content += "## SYSTEM INSTRUCTION\n"
        content += "---BEGIN SYSTEM---\n"
        content += system_prompt
        content += "\n---END SYSTEM---\n\n"
        content += "## USER PROMPT\n"
        content += "---BEGIN USER---\n"
        content += user_prompt
        content += "\n---END USER---\n"

        path.write_text(content, encoding="utf-8")

    def _assemble_markdown(self, result: Stage4Result) -> str:
        """Construct the Markdown summary from the structured result."""
        md = f"<details>\n<summary>{result.apa_summary_line}</summary>\n\n"
        md += f"- **Authors:** {', '.join(result.authors)}\n"
        md += f"- **Institutes:** {', '.join(result.institutes)}\n"
        md += f"- **Publisher:** {result.publisher}\n"
        md += f"- **Link:** [DOI]({result.link})\n\n"
        md += "</details>\n\n"

        md += f"## Summary\n\n{result.summary_impact}\n\n"
        md += f"## What was researched?\n\n{result.what_was_researched}\n\n"
        md += f"## Why was it researched?\n\n{result.why_was_it_researched}\n\n"
        md += f"## How was it researched?\n\n{result.how_was_it_researched}\n\n"
        md += f"## What has been found?\n\n{result.what_has_been_found}\n\n"
        md += f"## Discussion\n\n{result.discussion}\n\n"
        md += f"## Conclusion & Future Work\n\n{result.conclusion}\n"

        return md

    async def stage_1_synthesis(self):
        """Aggregate input files into a structured list."""
        print("\n=== Stage 1: Data Synthesis ===")

        # 1. Check State
        if STAGE_1_OUTPUT.exists():
            print("Found existing Stage 1 output. Skipping synthesis.")
            data = Stage1Output.model_validate_json(
                STAGE_1_OUTPUT.read_text(encoding="utf-8")
            )
            return data.publications

        # Load pre-structured publications from reddit_feed.json programmatically if it exists
        reddit_path = INPUT_DIR / "reddit_feed.json"
        reddit_publications = []
        if reddit_path.exists():
            try:
                print("Loading pre-structured publications from reddit_feed.json...")
                reddit_data = Stage1Output.model_validate_json(
                    reddit_path.read_text(encoding="utf-8")
                )
                reddit_publications = reddit_data.publications
                print(f"Loaded {len(reddit_publications)} programmatic publications.")
            except Exception as e:
                print(f"Error loading reddit_feed.json programmatically: {e}")

        # 2. Gather Input
        input_content = []
        for file in INPUT_DIR.glob("*"):
            if file.name.startswith("."):
                continue
            if not file.is_file():
                continue
            if file.name == "reddit_feed.json":
                continue
            if file.suffix not in [".eml", ".md", ".txt"]:
                continue
            if file.name in [STAGE_1_OUTPUT.name, STAGE_2_OUTPUT.name]:
                continue

            raw_content = file.read_text(encoding="utf-8", errors="replace")

            if file.suffix == ".eml":
                content = self._parse_eml(raw_content)
            elif file.suffix == ".md":
                content = raw_content
            else:
                content = raw_content

            input_content.append(f"--- FILE: {file.name} ---\n{content}\n")

        llm_publications = []
        if input_content:
            full_input = "\n".join(input_content)

            # 3. Prepare Prompt
            system_prompt = self._read_prompt("stage_1_system.md")
            input_template = self._read_prompt("stage_1_input.md")
            final_prompt = input_template.replace("{{INPUT_DATA}}", full_input)

            self._save_debug_prompt("stage_1", system_prompt, final_prompt)

            # 4. Call Gemini
            print("Sending request to Gemini...")
            response = await self._generate_content_with_retry(
                model=self.model_id,
                contents=final_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=Stage1Output,
                ),
            )

            # 5. Parse LLM response
            data = Stage1Output.model_validate_json(response.text)
            llm_publications = data.publications
            print(f"LLM parsed {len(llm_publications)} publications.")
        else:
            print("No raw input files to parse with Gemini. Bypassing LLM call.")

        # Combine both programmatic and LLM parsed publications
        combined_list = reddit_publications + llm_publications

        if not combined_list:
            print("No publications found from either Reddit or LLM parsing.")
            return []

        # Validate the final merged output
        final_output = Stage1Output(publications=combined_list)
        STAGE_1_OUTPUT.write_text(
            final_output.model_dump_json(indent=2), encoding="utf-8"
        )
        print(f"Stage 1 complete. Found {len(combined_list)} combined publications.")
        return combined_list

    async def stage_2_deduplication(self, new_items: List[PublicationItem]):
        """Deduplicate against existing summaries."""
        print("\n=== Stage 2: Data Deduplication ===")

        if STAGE_2_OUTPUT.exists():
            print("Found existing Stage 2 output. Skipping deduplication.")
            data = Stage2Output.model_validate_json(
                STAGE_2_OUTPUT.read_text(encoding="utf-8")
            )
            return data.unique_publications

        if not new_items:
            print("No items to deduplicate.")
            return []

        # 1. Collect Existing Metadata (Title & Link)
        existing_summaries = []
        for file in CONTENT_DIR.glob("*.md"):
            # Skip aggregate files or special files
            if (
                file.name == "index.md"
                or file.name == "README.md"
                or "aggregate" in file.name.lower()
            ):
                continue
            try:
                content = file.read_text(encoding="utf-8")

                # Extract title from frontmatter
                title = None
                parts = content.split("---")
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    for line in frontmatter.splitlines():
                        line = line.strip()
                        if line.startswith("title:"):
                            title_val = line.split("title:", 1)[1].strip()
                            if title_val.startswith('"') and title_val.endswith('"'):
                                title_val = title_val[1:-1]
                            elif title_val.startswith("'") and title_val.endswith("'"):
                                title_val = title_val[1:-1]
                            title = title_val
                            break

                # Extract link / URL from the body
                body = "---".join(parts[2:]) if len(parts) >= 3 else content
                link = None
                for line in body.splitlines():
                    line = line.strip()
                    if "**Link:**" in line:
                        md_match = re.search(r"\[[^\]]*\]\((https?://[^\)]+)\)", line)
                        if md_match:
                            link = md_match.group(1).strip()
                            break
                        url_match = re.search(r"(https?://\S+)", line)
                        if url_match:
                            link = url_match.group(1).strip()
                            break

                # Extract first 10 lines for header reference
                header_lines = content.split("\n")[:10]
                header_str = f"File: {file.name}\n" + "\n".join(header_lines)

                existing_summaries.append(
                    {
                        "file_name": file.name,
                        "title": title,
                        "link": link,
                        "header": header_str,
                    }
                )
            except Exception as e:
                print(
                    f"Warning: Failed to parse existing summary file {file.name}: {e}"
                )
                continue

        # 2. Programmatic Filtering
        programmatically_kept = []
        ambiguous_candidates = []
        ambiguous_headers_set = set()

        for candidate in new_items:
            candidate_link = candidate.link
            candidate_title = candidate.title

            normalized_candidate = (
                re.sub(r"[^a-z0-9]", "", candidate_title.lower())
                if candidate_title
                else ""
            )
            if candidate_link:
                candidate_link = candidate_link.strip()

            is_duplicate = False
            is_ambiguous = False
            candidate_matched_headers = []

            for existing in existing_summaries:
                # Exact Link Matching
                if candidate_link and existing["link"]:
                    if candidate_link == existing["link"].strip():
                        print(
                            f"Exact link match: Discarding candidate '{candidate_title}' (matches existing link: {existing['link']})"
                        )
                        is_duplicate = True
                        break

                # Fuzzy Title Matching
                existing_title = existing["title"]
                normalized_existing = (
                    re.sub(r"[^a-z0-9]", "", existing_title.lower())
                    if existing_title
                    else ""
                )

                if not normalized_candidate or not normalized_existing:
                    continue

                if normalized_candidate == normalized_existing:
                    print(
                        f"Exact normalized title match: Discarding candidate '{candidate_title}'"
                    )
                    is_duplicate = True
                    break

                ratio = SequenceMatcher(
                    None, normalized_candidate, normalized_existing
                ).ratio()
                if ratio >= 0.95:
                    print(
                        f"Certain duplicate by title similarity ({ratio:.3f}): Discarding candidate '{candidate_title}' vs existing '{existing_title}'"
                    )
                    is_duplicate = True
                    break
                elif 0.75 <= ratio < 0.95:
                    print(
                        f"Ambiguous title similarity ({ratio:.3f}): Candidate '{candidate_title}' vs existing '{existing_title}'. Saving for LLM."
                    )
                    is_ambiguous = True
                    candidate_matched_headers.append(existing["header"])

            if is_duplicate:
                continue
            elif is_ambiguous:
                ambiguous_candidates.append(candidate)
                for h in candidate_matched_headers:
                    ambiguous_headers_set.add(h)
            else:
                # Certain New
                print(
                    f"Certain new: Programmatically keeping candidate '{candidate_title}'"
                )
                programmatically_kept.append(candidate)

        # 3. Gemini Fallback & Bypass
        llm_kept = []
        if ambiguous_candidates:
            print(
                f"Calling Gemini Fallback for {len(ambiguous_candidates)} ambiguous candidates."
            )
            existing_list_str = "\n---\n".join(sorted(list(ambiguous_headers_set)))
            new_list_str = json.dumps(
                [item.model_dump() for item in ambiguous_candidates], indent=2
            )

            system_prompt = self._read_prompt("stage_2_system.md")
            input_template = self._read_prompt("stage_2_input.md")
            final_prompt = input_template.replace("{{NEW_LIST}}", new_list_str).replace(
                "{{EXISTING_LIST}}", existing_list_str
            )

            self._save_debug_prompt("stage_2", system_prompt, final_prompt)

            response = await self._generate_content_with_retry(
                model=self.model_id,
                contents=final_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=Stage2Output,
                ),
            )

            llm_data = Stage2Output.model_validate_json(response.text)
            llm_kept = llm_data.unique_publications
            print(f"Gemini Fallback cleared {len(llm_kept)} unique publications.")
        else:
            print(
                "No ambiguous candidates. Completely bypassing Gemini Stage 2 API call."
            )

        # 4. Consolidation & Validation
        combined_unique_candidates = programmatically_kept + llm_kept
        final_output = Stage2Output(unique_publications=combined_unique_candidates)

        STAGE_2_OUTPUT.write_text(
            final_output.model_dump_json(indent=2), encoding="utf-8"
        )
        print(
            f"Stage 2 complete. {len(combined_unique_candidates)} unique publications remain."
        )
        return combined_unique_candidates

    async def stage_3_relevance_screening(self, items: List[PublicationItem]):
        """Screen new publications for relevance."""
        print("\n=== Stage 3: Relevance Screening ===")

        if STAGE_3_OUTPUT.exists():
            print("Found existing Stage 3 output. Skipping screening.")
            data = Stage3Output.model_validate_json(
                STAGE_3_OUTPUT.read_text(encoding="utf-8")
            )
            # Filter to relevant ones
            relevant = [
                item
                for item in items
                if any(
                    s.title == item.title and s.is_relevant
                    for s in data.screened_publications
                )
            ]
            return relevant

        if not items:
            print("No items to screen.")
            return []

        # 1. Prepare Prompt
        inclusion_rules = self._read_prompt("inclusion_rules.md")
        system_prompt = self._read_prompt("stage_3_system.md").replace(
            "{{INCLUSION_RULES}}", inclusion_rules
        )
        input_template = self._read_prompt("stage_3_input.md")

        # 2. Batch and Call Gemini
        batch_size = 10
        batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
        sem = asyncio.Semaphore(3)

        async def process_batch(
            batch_items: List[PublicationItem], batch_idx: int
        ) -> List[Stage3ScreeningResult]:
            async with sem:
                print(
                    f"Processing Stage 3 batch {batch_idx + 1}/{len(batches)} ({len(batch_items)} items)..."
                )
                batch_list_str = json.dumps(
                    [item.model_dump() for item in batch_items], indent=2
                )
                batch_prompt = input_template.replace("{{NEW_LIST}}", batch_list_str)

                # Save debug prompt for the batch
                self._save_debug_prompt(
                    f"stage_3_batch_{batch_idx + 1}", system_prompt, batch_prompt
                )

                response = await self._generate_content_with_retry(
                    model=self.model_id,
                    contents=batch_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        response_schema=Stage3Output,
                    ),
                )
                batch_output = Stage3Output.model_validate_json(response.text)
                return batch_output.screened_publications

        tasks = [process_batch(batch, i) for i, batch in enumerate(batches)]
        batch_results = await asyncio.gather(*tasks)

        # Consolidate all batch results into a single list of Stage3ScreeningResult
        all_screened = []
        for res in batch_results:
            all_screened.extend(res)

        data = Stage3Output(screened_publications=all_screened)
        STAGE_3_OUTPUT.write_text(data.model_dump_json(indent=2), encoding="utf-8")

        # 4. Process Exclusions
        relevant_titles = []
        for res in data.screened_publications:
            if not res.is_relevant:
                safe_title = re.sub(r"[^a-zA-Z0-9]", "_", res.title)[:50]
                path = EXCLUDED_DIR / f"{safe_title}.json"
                path.write_text(res.model_dump_json(indent=2), encoding="utf-8")
                print(f"EXCLUDED: {res.title[:30]}... ({res.reason})")
            else:
                relevant_titles.append(res.title)
        relevant_items = [item for item in items if item.title in relevant_titles]
        print(f"Stage 3 complete. {len(relevant_items)} relevant publications found.")
        return relevant_items

    async def _process_single_paper(
        self, item: PublicationItem, sem: asyncio.Semaphore, index: int, total: int
    ):
        """Process a single paper (Stage 4) with concurrency limit."""
        safe_title = re.sub(r"[^a-zA-Z0-9]", "_", item.title)[:50]
        stage_4_path = STAGE_4_DIR / f"{safe_title}.json"

        # Check idempotency
        final_file = next(CONTENT_DIR.glob(f"*_{safe_title}.md"), None)
        if final_file:
            print(
                f"[{index}/{total}] Skipping {item.title[:20]}... (Already completed)"
            )
            return

        if (EXCLUDED_DIR / f"{safe_title}.json").exists():
            print(f"[{index}/{total}] Skipping {item.title[:20]}... (Already excluded)")
            return
        if (INACCESSIBLE_DIR / f"{safe_title}.json").exists():
            print(
                f"[{index}/{total}] Skipping {item.title[:20]}... (Already marked inaccessible)"
            )
            return

        async with sem:
            # --- STAGE 4: Summarization & Tagging ---
            result_4 = None
            if stage_4_path.exists():
                print(
                    f"[{index}/{total}] Using existing Stage 4 result for: {item.title[:30]}"
                )
                result_4 = Stage4Result.model_validate_json(
                    stage_4_path.read_text(encoding="utf-8")
                )
            else:
                print(f"[{index}/{total}] Processing Stage 4: {item.title[:30]}...")
                system_prompt_4 = self._read_prompt("stage_4_system.md")
                input_template_4 = self._read_prompt("stage_4_input.md")
                item_prompt_4 = input_template_4.replace(
                    "{{TITLE}}", item.title
                ).replace("{{LINK}}", item.link or "N/A")

                self._save_debug_prompt(
                    f"stage_4_{safe_title}", system_prompt_4, item_prompt_4
                )

                try:
                    response_4 = await self._generate_content_with_retry(
                        model=self.model_id,
                        contents=item_prompt_4,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt_4,
                            response_mime_type="application/json",
                            response_schema=Stage4Result,
                            tools=[
                                types.Tool(google_search=types.GoogleSearch()),
                                types.Tool(url_context=types.UrlContext()),
                            ],
                            thinking_config=types.ThinkingConfig(
                                thinking_level=THINKING_LEVEL_STAGE_4
                            ),
                        ),
                    )

                    result_4 = Stage4Result.model_validate_json(response_4.text)

                    if not result_4.is_accessible:
                        filename = f"{safe_title}.json"
                        path = INACCESSIBLE_DIR / filename
                        path.write_text(
                            result_4.model_dump_json(indent=2), encoding="utf-8"
                        )
                        print(f"[{index}/{total}] INACCESSIBLE: {filename}")
                        return

                    # Save Stage 4 intermediate result
                    stage_4_path.write_text(
                        result_4.model_dump_json(indent=2), encoding="utf-8"
                    )

                except Exception as e:
                    print(f"[ERROR in Stage 4 for {item.title}: {e}]")
                    return

            # --- Final Integration and Saving ---
            try:
                # Assemble Markdown Body
                markdown_body = self._assemble_markdown(result_4)

                pub_date = result_4.published_date or "0000-00-00"
                date_prefix = pub_date
                filename = f"{date_prefix}_{safe_title}.md"
                path = CONTENT_DIR / filename

                md_content = "---\n"
                md_content += f'title: "{result_4.title}"\n'
                md_content += "tags:\n"
                # Add release date tag
                current_date = datetime.now().strftime("%Y-%m-%d")
                md_content += f"- ➕ {current_date}\n"
                for tag in result_4.tags:
                    md_content += f"- {tag}\n"
                md_content += f"created: '{pub_date}'\n"
                md_content += f"published: '{pub_date}'\n"
                md_content += "---\n\n"
                md_content += f"{markdown_body}\n"

                path.write_text(md_content, encoding="utf-8")
                print(f"[{index}/{total}] DONE: {filename}")

                # Cleanup Stage 4 intermediate file if desired (optional)
                # stage_4_path.unlink()

            except Exception as e:
                print(
                    f"[{index}/{total}] ERROR in Markdown generation/saving for {item.title}: {e}"
                )

    async def stage_4_execution(self, items: List[PublicationItem]):
        """Parallel execution of Stage 4 with Semaphore."""
        print("\n=== Stage 4: Data Extraction & Tagging ===")

        if not items:
            print("No items to process.")
            return

        # Limit concurrency to 5
        sem = asyncio.Semaphore(5)
        total = len(items)
        tasks = [
            self._process_single_paper(item, sem, i + 1, total)
            for i, item in enumerate(items)
        ]
        await asyncio.gather(*tasks)

    async def run(self):
        try:
            # Stage 1
            publications = await self.stage_1_synthesis()

            # Stage 2
            unique_publications = await self.stage_2_deduplication(publications)

            # Stage 3
            relevant_publications = await self.stage_3_relevance_screening(
                unique_publications
            )

            # Stage 4
            await self.stage_4_execution(relevant_publications)

            print("\nAll stages completed successfully.")

        except Exception as e:
            print(f"\nWorkflow Failed: {e}")


if __name__ == "__main__":
    agent = ResearchAgent()
    asyncio.run(agent.run())

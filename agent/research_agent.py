import asyncio
import json
import os
import re
import email
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

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
DEBUG_PROMPTS = False

# State Files (Located in STATE_DIR)
STAGE_1_OUTPUT = STATE_DIR / "stage_1_output.json"
STAGE_2_OUTPUT = STATE_DIR / "stage_2_output.json"
STAGE_3_OUTPUT = STATE_DIR / "stage_3_output.json"
STAGE_4_DIR = STATE_DIR / "stage_4"  # Directory for individual Stage 4 results
EXCLUDED_DIR = STATE_DIR / "excluded"
INACCESSIBLE_DIR = STATE_DIR / "inaccessible"

# Ensure directories exist
for d in [INPUT_DIR, STATE_DIR, STAGE_4_DIR, EXCLUDED_DIR, INACCESSIBLE_DIR, CONTENT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

if DEBUG_PROMPTS:
    PROMPT_DUMP_DIR.mkdir(parents=True, exist_ok=True)

# Thinking Levels
THINKING_LEVEL_STAGE_1 = "high"
THINKING_LEVEL_STAGE_2 = "high"
THINKING_LEVEL_STAGE_3 = "high"
THINKING_LEVEL_STAGE_4 = "high"
THINKING_LEVEL_STAGE_5 = "high"

# Configure Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-3-flash-preview"

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
    
    # Body Content
    summary_impact: Optional[str] = Field(None, description="High-level impact paragraph. Length: 1-6 sentences.")
    what_was_researched: Optional[str] = Field(None, description="Central research question or objective. Length: 1-3 sentences.")
    why_was_it_researched: Optional[str] = Field(None, description="Background and motivation. Length: 1-3 sentences.")
    how_was_it_researched: Optional[str] = Field(None, description="Methodology, study type, cohort details. Length: 1-5 sentences.")
    what_has_been_found: Optional[str] = Field(None, description="Primary results and novel findings. Length: 1-5 sentences.")
    discussion: Optional[str] = Field(None, description="Limitations, strengths, or weaknesses. Length: 1-4 sentences.")
    conclusion: Optional[str] = Field(None, description="Main conclusions and future research suggestions. Length: 1-3 sentences.")

class Stage5Result(BaseModel):
    tags: List[str]

class ResearchAgent:
    def __init__(self):
        self.model_id = MODEL_ID

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
        for a in soup.find_all('a'):
            href = a.get('href')
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
                        html_payload = part.get_payload(decode=True).decode(errors="replace")
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

    def aggregate_summaries(self):
        """Concatenate all individual markdown summaries into a single file."""
        print("\n=== Aggregating Summaries ===")
        all_md_files = sorted(list(CONTENT_DIR.glob("*.md")))
        
        # Filter out the aggregate file itself if it exists
        aggregate_file_name = "all_summaries.md"
        all_md_files = [f for f in all_md_files if f.name != aggregate_file_name]

        if not all_md_files:
            print("No summaries found to aggregate.")
            return

        aggregated_content = "# ME/CFS Research Summaries - Full Collection\n\n"
        aggregated_content += f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        aggregated_content += "---\n\n"

        for file_path in all_md_files:
            content = file_path.read_text(encoding="utf-8")
            # Optional: Remove YAML frontmatter from individual summaries for the aggregate view
            # but usually it's better to keep it or transform it.
            # For now, let's just append with a separator.
            aggregated_content += content + "\n\n---\n\n"

        output_path = BASE_DIR / aggregate_file_name
        output_path.write_text(aggregated_content, encoding="utf-8")
        print(f"Aggregated {len(all_md_files)} summaries into {output_path.name}")

    async def stage_1_synthesis(self):
        """Aggregate input files into a structured list."""
        print("\n=== Stage 1: Data Synthesis ===")
        
        # 1. Check State
        if STAGE_1_OUTPUT.exists():
            print("Found existing Stage 1 output. Skipping synthesis.")
            data = Stage1Output.model_validate_json(STAGE_1_OUTPUT.read_text(encoding="utf-8"))
            return data.publications
        
        # 2. Gather Input
        input_content = []
        for file in INPUT_DIR.glob("*"):
            if file.name.startswith("."): continue
            if not file.is_file(): continue
            if file.suffix not in ['.eml', '.md']: continue 
            if file.name in [STAGE_1_OUTPUT.name, STAGE_2_OUTPUT.name]: continue

            raw_content = file.read_text(encoding='utf-8', errors='replace')
            
            if file.suffix == '.eml':
                content = self._parse_eml(raw_content)
            elif file.suffix == '.md':
                content = raw_content
            else:
                content = raw_content

            input_content.append(f"--- FILE: {file.name} ---\n{content}\n")
        
        if not input_content:
            print("No valid input files (.eml, .md) found.")
            return []

        full_input = "\n".join(input_content)
        
        # 3. Prepare Prompt
        system_prompt = self._read_prompt("stage_1_system.md")
        input_template = self._read_prompt("stage_1_input.md")
        final_prompt = input_template.replace("{{INPUT_DATA}}", full_input)

        self._save_debug_prompt("stage_1", system_prompt, final_prompt)

        # 4. Call Gemini
        print("Sending request to Gemini...")
        response = client.models.generate_content(
            model=self.model_id,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=Stage1Output,
                tools=[types.Tool(url_context=types.UrlContext())],
                thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL_STAGE_1)
            )
        )
        
        # 5. Parse and Save
        data = Stage1Output.model_validate_json(response.text)
        STAGE_1_OUTPUT.write_text(response.text, encoding="utf-8")
        print(f"Stage 1 complete. Found {len(data.publications)} publications.")
        return data.publications

    async def stage_2_deduplication(self, new_items: List[PublicationItem]):
        """Deduplicate against existing summaries."""
        print("\n=== Stage 2: Data Deduplication ===")
        
        if STAGE_2_OUTPUT.exists():
            print("Found existing Stage 2 output. Skipping deduplication.")
            data = Stage2Output.model_validate_json(STAGE_2_OUTPUT.read_text(encoding="utf-8"))
            return data.unique_publications

        if not new_items:
            print("No items to deduplicate.")
            return []

        # 1. Collect Existing Metadata
        existing_headers = []
        for file in CONTENT_DIR.glob("*.md"):
            try:
                content = file.read_text(encoding="utf-8")
                header_lines = content.split('\n')[:10] 
                existing_headers.append(f"File: {file.name}\n" + "\n".join(header_lines))
            except Exception:
                continue
        
        existing_list_str = "\n---\n".join(existing_headers)
        new_list_str = json.dumps([item.model_dump() for item in new_items], indent=2)

        # 2. Prepare Prompt
        system_prompt = self._read_prompt("stage_2_system.md")
        input_template = self._read_prompt("stage_2_input.md")
        final_prompt = input_template.replace("{{NEW_LIST}}", new_list_str).replace("{{EXISTING_LIST}}", existing_list_str)

        self._save_debug_prompt("stage_2", system_prompt, final_prompt)

        # 3. Call Gemini
        print("Sending request to Gemini...")
        response = client.models.generate_content(
            model=self.model_id,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=Stage2Output,
                thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL_STAGE_2)
            )
        )
        
        # 4. Parse and Save
        data = Stage2Output.model_validate_json(response.text)
        STAGE_2_OUTPUT.write_text(response.text, encoding="utf-8")
        
        print(f"Stage 2 complete. {len(data.unique_publications)} unique publications remain.")
        return data.unique_publications

    async def stage_3_relevance_screening(self, items: List[PublicationItem]):
        """Screen new publications for relevance."""
        print("\n=== Stage 3: Relevance Screening ===")

        if STAGE_3_OUTPUT.exists():
            print("Found existing Stage 3 output. Skipping screening.")
            data = Stage3Output.model_validate_json(STAGE_3_OUTPUT.read_text(encoding="utf-8"))
            # Filter to relevant ones
            relevant = [
                item for item in items 
                if any(s.title == item.title and s.is_relevant for s in data.screened_publications)
            ]
            return relevant

        if not items:
            print("No items to screen.")
            return []

        # 1. Prepare Prompt
        inclusion_rules = self._read_prompt("inclusion_rules.md")
        system_prompt = self._read_prompt("stage_3_system.md").replace("{{INCLUSION_RULES}}", inclusion_rules)
        input_template = self._read_prompt("stage_3_input.md")
        new_list_str = json.dumps([item.model_dump() for item in items], indent=2)
        final_prompt = input_template.replace("{{NEW_LIST}}", new_list_str)

        self._save_debug_prompt("stage_3", system_prompt, final_prompt)

        # 2. Call Gemini
        print("Sending request to Gemini...")
        response = client.models.generate_content(
            model=self.model_id,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=Stage3Output,
                tools=[types.Tool(url_context=types.UrlContext())],
                thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL_STAGE_3)
            )
        )

        # 3. Parse and Save
        data = Stage3Output.model_validate_json(response.text)
        STAGE_3_OUTPUT.write_text(response.text, encoding="utf-8")

        # 4. Process Exclusions
        relevant_titles = []
        for res in data.screened_publications:
            if not res.is_relevant:
                safe_title = re.sub(r'[^a-zA-Z0-9]', '_', res.title)[:50]
                path = EXCLUDED_DIR / f"{safe_title}.json"
                path.write_text(res.model_dump_json(indent=2), encoding="utf-8")
                print(f"EXCLUDED: {res.title[:30]}... ({res.reason})")
            else:
                relevant_titles.append(res.title)

        relevant_items = [item for item in items if item.title in relevant_titles]
        print(f"Stage 3 complete. {len(relevant_items)} relevant publications found.")
        return relevant_items

    async def _process_single_paper(self, item: PublicationItem, sem: asyncio.Semaphore, index: int, total: int):
        """Process a single paper (Stage 4 & 5) with concurrency limit."""
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', item.title)[:50]
        stage_4_path = STAGE_4_DIR / f"{safe_title}.json"
        
        # Check idempotency
        final_file = next(CONTENT_DIR.glob(f"*_{safe_title}.md"), None)
        if final_file:
            print(f"[{index}/{total}] Skipping {item.title[:20]}... (Already completed)")
            return
            
        if (EXCLUDED_DIR / f"{safe_title}.json").exists():
            print(f"[{index}/{total}] Skipping {item.title[:20]}... (Already excluded)")
            return
        if (INACCESSIBLE_DIR / f"{safe_title}.json").exists():
            print(f"[{index}/{total}] Skipping {item.title[:20]}... (Already marked inaccessible)")
            return

        async with sem:
            # --- STAGE 4: Summarization ---
            result_4 = None
            if stage_4_path.exists():
                print(f"[{index}/{total}] Using existing Stage 4 result for: {item.title[:30]}")
                result_4 = Stage4Result.model_validate_json(stage_4_path.read_text(encoding="utf-8"))
            else:
                print(f"[{index}/{total}] Processing Stage 4: {item.title[:30]}...")
                system_prompt_4 = self._read_prompt("stage_4_system.md")
                input_template_4 = self._read_prompt("stage_4_input.md")
                item_prompt_4 = input_template_4.replace("{{TITLE}}", item.title).replace("{{LINK}}", item.link or "N/A")

                self._save_debug_prompt(f"stage_4_{safe_title}", system_prompt_4, item_prompt_4)

                try:
                    response_4 = await client.aio.models.generate_content(
                        model=self.model_id,
                        contents=item_prompt_4,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt_4,
                            response_mime_type="application/json",
                            response_schema=Stage4Result,
                            tools=[types.Tool(google_search=types.GoogleSearch()), types.Tool(url_context=types.UrlContext())],
                            thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL_STAGE_4)
                        )
                    )

                    result_4 = Stage4Result.model_validate_json(response_4.text)
                    
                    if not result_4.is_accessible:
                        filename = f"{safe_title}.json"
                        path = INACCESSIBLE_DIR / filename
                        path.write_text(result_4.model_dump_json(indent=2), encoding="utf-8")
                        print(f"[{index}/{total}] INACCESSIBLE: {filename}")
                        return
                    
                    # Save Stage 4 intermediate result
                    stage_4_path.write_text(result_4.model_dump_json(indent=2), encoding="utf-8")

                except Exception as e:
                    print(f"[{index}/{total}] ERROR in Stage 4 for {item.title}: {e}")
                    return

            # --- STAGE 5: Tagging ---
            try:
                # Assemble Markdown Body
                markdown_body = self._assemble_markdown(result_4)

                print(f"[{index}/{total}] Processing Stage 5: {item.title[:30]}...")
                tagging_system = self._read_prompt("tagging_system.md")
                system_prompt_5 = self._read_prompt("stage_5_system.md").replace("{{TAGGING_SYSTEM}}", tagging_system)
                input_template_5 = self._read_prompt("stage_5_input.md")
                item_prompt_5 = input_template_5.replace("{{SUMMARY}}", markdown_body)

                self._save_debug_prompt(f"stage_5_{safe_title}", system_prompt_5, item_prompt_5)

                response_5 = await client.aio.models.generate_content(
                    model=self.model_id,
                    contents=item_prompt_5,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt_5,
                        response_mime_type="application/json",
                        response_schema=Stage5Result,
                        thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL_STAGE_5)
                    )
                )

                result_5 = Stage5Result.model_validate_json(response_5.text)

                # Final Integration and Saving
                pub_date = result_4.published_date or "0000-00-00"
                date_prefix = pub_date
                filename = f"{date_prefix}_{safe_title}.md"
                path = CONTENT_DIR / filename
                
                md_content = "---\n"
                md_content += f"title: \"{result_4.title}\"\n"
                md_content += "tags:\n"
                # Add release date tag
                current_date = datetime.now().strftime("%Y-%m-%d")
                md_content += f"- ➕ {current_date}\n"
                for tag in result_5.tags:
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
                print(f"[{index}/{total}] ERROR in Stage 5 for {item.title}: {e}")

    async def stage_4_execution(self, items: List[PublicationItem]):
        """Parallel execution of Stages 4 & 5 with Semaphore."""
        print("\n=== Stage 4 & 5: Data Extraction & Tagging ===")
        
        if not items:
            print("No items to process.")
            return

        # Limit concurrency to 5
        sem = asyncio.Semaphore(5)
        total = len(items)
        tasks = [self._process_single_paper(item, sem, i+1, total) for i, item in enumerate(items)]
        await asyncio.gather(*tasks)

    async def run(self):
        try:
            # Stage 1
            publications = await self.stage_1_synthesis()
            
            # Stage 2
            unique_publications = await self.stage_2_deduplication(publications)
            
            # Stage 3
            relevant_publications = await self.stage_3_relevance_screening(unique_publications)
            
            # Stage 4 & 5
            await self.stage_4_execution(relevant_publications)
            
            # Final Aggregation
            self.aggregate_summaries()
            
            print("\nAll stages completed successfully.")
            
        except Exception as e:
            print(f"\nWorkflow Failed: {e}")

if __name__ == "__main__":
    agent = ResearchAgent()
    asyncio.run(agent.run())

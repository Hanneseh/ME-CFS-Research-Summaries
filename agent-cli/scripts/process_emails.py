#!/usr/bin/env python
from __future__ import annotations

import email
import json
import os
from pathlib import Path
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "agent-cli" / "input"
EMAILS_DIR = INPUT_DIR / "emails"
OUTPUT_FILE = BASE_DIR / "agent-cli" / "state" / "email_publications.json"
MODEL_ID = "gemini-3.5-flash"

class PublicationItem(BaseModel):
    title: str = Field(description="The scientific paper or article title.")
    link: str | None = Field(None, description="The URL of the paper, abstract, or news item.")
    source: str | None = Field(None, description="Source name (e.g. PubMed, Google Scholar, ScienceDaily).")

class EmailPublications(BaseModel):
    publications: list[PublicationItem]

def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove script and style elements
    for s in soup(["script", "style"]):
        s.decompose()
    # Replace link tags with text containing URL
    for a in soup.find_all("a"):
        href = a.get("href")
        if href:
            a.replace_with(f"{a.get_text()} ({href})")
    text = soup.get_text(separator="\n")
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())

def parse_eml(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        msg = email.message_from_binary_file(f)
    
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
                    text_parts.append(clean_html(html_payload))
                except Exception:
                    pass
    else:
        content_type = msg.get_content_type()
        try:
            payload = msg.get_payload(decode=True).decode(errors="replace")
            if content_type == "text/html":
                text_parts.append(clean_html(payload))
            else:
                text_parts.append(payload)
        except Exception:
            pass
            
    return "\n".join(text_parts)

def main():
    if not EMAILS_DIR.exists():
        print(f"Emails directory {EMAILS_DIR} does not exist.")
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(json.dumps({"publications": []}), encoding="utf-8")
        return

    eml_files = list(EMAILS_DIR.glob("*.eml"))
    if not eml_files:
        print("No .eml files found in the ingress emails directory.")
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(json.dumps({"publications": []}), encoding="utf-8")
        return

    print(f"Found {len(eml_files)} emails to process.")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set.")
        return

    client = genai.Client(api_key=api_key)

    combined_text = []
    for f in eml_files:
        content = parse_eml(f)
        combined_text.append(f"--- EMAIL FILE: {f.name} ---\n{content}\n")

    full_input = "\n".join(combined_text)

    system_prompt = """You are an Expert Research Curator specialized in Biomedical Science, specifically ME/CFS (Myalgic Encephalomyelitis/Chronic Fatigue Syndrome) and Long COVID.
Your goal is to parse a collection of raw search alert emails into a clean, structured JSON list of unique research publications.

Rules:
1. Focus on Primary Sources: You prefer scientific papers (Journal Articles, Preprints, Trial Registries) over news articles. If a news alert discusses a specific paper, extract the paper's title and link.
2. Relevance Curation: ONLY extract publications relevant to ME/CFS, Long COVID (specifically mechanistic, immune, mitochondrial, or therapeutic studies),POTs/Dysautonomia, and post-viral illness. Exclude unrelated medicine, job advertisements, and news noise.
3. Link Extraction: Find the direct external URL to the paper or abstract (e.g. DOI, PubMed, or journal link).
4. Output JSON schema: {"publications": [{"title": "...", "link": "...", "source": "..."}]}"""

    user_prompt = f"Please extract all relevant publication candidates from the following emails:\n\n{full_input}"

    print("Requesting email publication extraction from Gemini...")
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=EmailPublications,
            )
        )
        
        # Verify and save
        data = EmailPublications.model_validate_json(response.text)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(json.dumps(data.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Successfully extracted {len(data.publications)} email publications to {OUTPUT_FILE.relative_to(BASE_DIR)}")
        
    except Exception as e:
        print(f"Error calling Gemini or validating output: {e}")
        # Write empty fallback
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(json.dumps({"publications": []}), encoding="utf-8")

if __name__ == "__main__":
    main()

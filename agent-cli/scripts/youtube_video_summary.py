#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = BASE_DIR / "agent-cli" / "state" / "youtube"
DEFAULT_MODEL = "gemini-3.5-flash"


@dataclass(frozen=True)
class TranscriptLine:
    start: float
    duration: float
    text: str

    @property
    def end(self) -> float:
        return self.start + self.duration

    @property
    def timestamp(self) -> str:
        total_seconds = int(self.start)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"


def parse_video_id(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower().removeprefix("www.")

    if host in {"youtube.com", "m.youtube.com"}:
        query_id = parse_qs(parsed.query).get("v")
        if query_id:
            return query_id[0]

        path_parts = [part for part in parsed.path.split("/") if part]
        if len(path_parts) >= 2 and path_parts[0] in {"embed", "shorts", "live"}:
            return path_parts[1]

    if host == "youtu.be":
        path_parts = [part for part in parsed.path.split("/") if part]
        if path_parts:
            return path_parts[0]

    raise ValueError(f"Could not extract a YouTube video ID from: {value}")


def fetch_transcript(video_id: str, languages: list[str]) -> list[TranscriptLine]:
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=languages)
    return [
        TranscriptLine(start=item.start, duration=item.duration, text=item.text)
        for item in transcript
    ]


def filter_segment(
    lines: list[TranscriptLine], start: float | None, end: float | None
) -> list[TranscriptLine]:
    if start is None and end is None:
        return lines
    return [
        line
        for line in lines
        if (start is None or line.end >= start) and (end is None or line.start <= end)
    ]


def format_transcript(lines: list[TranscriptLine]) -> str:
    return "\n".join(f"[{line.timestamp}] {line.text}" for line in lines)


def summarize_with_gemini(
    transcript_text: str,
    *,
    video_source: str,
    topic: str | None,
    model: str,
) -> str:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env or the shell environment.")

    topic_instruction = (
        f"Relevant topic: {topic}\n"
        if topic
        else "Relevant topic: extract only ME/CFS, Long COVID, source, trial, treatment, mechanism, or conference-update claims.\n"
    )
    prompt = f"""You are a source-checking assistant for an ME/CFS research-thread project.

Video source: {video_source}
{topic_instruction}
Use only the transcript segment below. Do not infer beyond it. YouTube captions may contain transcription errors, especially for biomedical terms, so flag uncertainty when wording is unclear.

Return Markdown with exactly these sections:
- Video Source Metadata
- Relevant Segment
- Transcript-Derived Claim Summary
- Speaker Attribution
- Limitations
- Candidate Thread Relevance

For each claim, include timestamp references when possible.

Transcript:
{transcript_text}
"""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text or ""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch YouTube captions and optionally summarize a bounded segment with Gemini. "
            "Use only for YouTube video source checking."
        )
    )
    parser.add_argument("video", help="YouTube URL or 11-character video ID.")
    parser.add_argument(
        "--language",
        action="append",
        dest="languages",
        default=None,
        help="Preferred caption language. Repeat to add fallbacks. Default: en.",
    )
    parser.add_argument(
        "--start",
        type=float,
        default=None,
        help="Start time in seconds for a bounded transcript segment.",
    )
    parser.add_argument(
        "--end",
        type=float,
        default=None,
        help="End time in seconds for a bounded transcript segment.",
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Topic to focus the Gemini summary on, e.g. 'daratumumab ResetME update'.",
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Call Gemini to summarize the transcript segment. This may incur API cost.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model for --summarize. Default: {DEFAULT_MODEL}.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for transcript and summary artifacts. Default: {DEFAULT_OUTPUT_DIR}.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print transcript or summary output to stdout in addition to writing files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also write the filtered transcript segment as structured JSON.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.start is not None and args.end is not None and args.end < args.start:
        parser.error("--end must be greater than or equal to --start")

    video_id = parse_video_id(args.video)
    languages = args.languages or ["en"]
    transcript = fetch_transcript(video_id, languages)
    segment = filter_segment(transcript, args.start, args.end)
    transcript_text = format_transcript(segment)

    if not transcript_text.strip():
        raise RuntimeError("Transcript segment is empty for the requested time range.")

    range_suffix = ""
    if args.start is not None or args.end is not None:
        start_label = "start" if args.start is None else str(int(args.start))
        end_label = "end" if args.end is None else str(int(args.end))
        range_suffix = f"_{start_label}-{end_label}"

    transcript_path = args.output_dir / f"{video_id}{range_suffix}_transcript.md"
    write_text(transcript_path, transcript_text + "\n")
    print(f"Wrote transcript: {transcript_path}")

    if args.json:
        json_path = args.output_dir / f"{video_id}{range_suffix}_transcript.json"
        write_text(
            json_path,
            json.dumps([asdict(line) for line in segment], ensure_ascii=False, indent=2)
            + "\n",
        )
        print(f"Wrote transcript JSON: {json_path}")

    output_text = transcript_text
    if args.summarize:
        summary = summarize_with_gemini(
            transcript_text,
            video_source=args.video,
            topic=args.topic,
            model=args.model,
        )
        summary_path = args.output_dir / f"{video_id}{range_suffix}_summary.md"
        write_text(summary_path, summary.rstrip() + "\n")
        print(f"Wrote Gemini summary: {summary_path}")
        output_text = summary

    if args.stdout:
        print(output_text)


if __name__ == "__main__":
    main()

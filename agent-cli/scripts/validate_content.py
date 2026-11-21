#!/usr/bin/env python3
"""Validate the atomic research content and its cross-file references."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import urlsplit

import yaml
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)

from atomic_content import (
    CONTENT_DIR,
    EVIDENCE_TIERS,
    GROUPS,
    entry_paths,
    read_yaml,
    thread_directories,
)

SLUG_PATTERN = r"[a-z0-9]+(?:-[a-z0-9]+)*"
DATE_PATTERN = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
THREAD_LINK = re.compile(r"\bthread:([^\s<>\])\"']*)")
LEGACY_LINK = re.compile(r"\.\./|/summaries/")
GroupSlug = Literal[
    "treatments-interventions", "disease-models-mechanisms", "diagnostics-symptoms-care"
]
EvidenceTier = Literal[
    "established", "active_trials", "early_clinical", "mechanistic", "hypothesis"
]
Slug = Annotated[str, Field(pattern=rf"^{SLUG_PATTERN}$")]


def non_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("must contain text")
    return value


def iso_date(value: str) -> str:
    if not re.fullmatch(DATE_PATTERN, value):
        raise ValueError("expected an ISO YYYY-MM-DD date")
    date.fromisoformat(value)
    return value


def http_url(value: str) -> str:
    if re.search(r"[\s<>]", value):
        raise ValueError("URL contains whitespace or angle brackets")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("expected an HTTP(S) URL with a host")
    _ = parsed.port
    return value


Text = Annotated[str, AfterValidator(non_blank)]
ISODate = Annotated[str, AfterValidator(iso_date)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class GroupCopy(StrictModel):
    title: Text
    short_title: Text
    description: Text


class Group(StrictModel):
    slug: GroupSlug
    order: int = Field(gt=0)
    accent: Slug
    en: GroupCopy
    de: GroupCopy


class TierCopy(StrictModel):
    label: Text
    short: Text
    description: Text


class Tier(StrictModel):
    id: EvidenceTier
    order: int = Field(gt=0)
    en: TierCopy
    de: TierCopy


class Groups(StrictModel):
    groups: list[Group]

    @model_validator(mode="after")
    def check_catalog(self):
        if sorted(group.slug for group in self.groups) != sorted(GROUPS):
            raise ValueError("groups must contain each group slug exactly once")
        if len({group.order for group in self.groups}) != len(self.groups):
            raise ValueError("group order must be unique")
        return self


class GlossaryCopy(StrictModel):
    full_name: Text
    definition: Text


class GlossaryTerm(StrictModel):
    term: Text
    category: Literal["symptom", "care", "research", "diagnostic", "biology"]
    en: GlossaryCopy
    de: GlossaryCopy


class Glossary(StrictModel):
    evidence_tiers: list[Tier]
    terms: list[GlossaryTerm] = Field(min_length=1)

    @model_validator(mode="after")
    def check_catalog(self):
        if sorted(tier.id for tier in self.evidence_tiers) != sorted(EVIDENCE_TIERS):
            raise ValueError("evidence_tiers must contain each tier exactly once")
        if len({tier.order for tier in self.evidence_tiers}) != len(
            self.evidence_tiers
        ):
            raise ValueError("evidence tier order must be unique")
        terms = {record.term.strip().casefold() for record in self.terms}
        if len(terms) != len(self.terms):
            raise ValueError("glossary terms must be unique")
        return self


class EvidenceBlock(StrictModel):
    status: Literal[
        "established", "plausible", "not_established", "limitations", "negative", "note"
    ]
    label: Text
    items: list[Text] = Field(min_length=1)


class ThreadCopy(StrictModel):
    title: str
    subtitle: str
    evidence_label: str
    plain_summary: str
    takeaway: str
    why_it_matters: str
    state_of_evidence: list[EvidenceBlock]
    open_questions: list[Text]


class EnglishThreadCopy(ThreadCopy):
    title: Text
    subtitle: Text
    evidence_label: Text
    takeaway: Text
    why_it_matters: Text
    state_of_evidence: list[EvidenceBlock] = Field(min_length=1)


class Thread(StrictModel):
    slug: Slug
    group: GroupSlug
    status: Literal["active", "paused", "emerging"]
    evidence_tier: EvidenceTier
    topics: list[Text]
    aliases: list[Text]
    related_threads: list[Slug]
    legacy_path: Text
    en: EnglishThreadCopy
    de: ThreadCopy

    @model_validator(mode="after")
    def check_metadata(self):
        if self.legacy_path != f"{self.group}/{self.slug}":
            raise ValueError("legacy_path must match group/slug")
        if self.slug in self.related_threads or len(set(self.related_threads)) != len(
            self.related_threads
        ):
            raise ValueError("related_threads must be unique and exclude this thread")
        return self


class Source(StrictModel):
    label: Text
    url: Annotated[str, AfterValidator(http_url)]
    kind: Literal[
        "paper",
        "preprint",
        "registry",
        "conference",
        "video",
        "announcement",
        "report",
        "other",
    ]


class EntryCopy(StrictModel):
    title: str
    plain_summary: str
    detail: str


class EnglishEntryCopy(EntryCopy):
    title: Text
    detail: Text


class Entry(StrictModel):
    id: Annotated[str, Field(pattern=rf"^{DATE_PATTERN}_{SLUG_PATTERN}$")]
    date: ISODate
    date_display: Text
    date_precision: Literal["exact", "month", "before", "period"]
    source_type: Literal[
        "paper",
        "preprint",
        "trial_registry",
        "conference",
        "announcement",
        "review",
        "report",
        "guideline",
    ]
    study_design: Text | None = None
    sources: list[Source] = Field(min_length=1)
    en: EnglishEntryCopy
    de: EntryCopy

    @model_validator(mode="after")
    def check_date_metadata(self):
        if not self.id.startswith(f"{self.date}_"):
            raise ValueError("id must start with the ISO sort date")
        expected = {
            "exact": self.date,
            "month": self.date[:7],
        }
        if self.date_precision == "before":
            cutoff = date.fromisoformat(self.date) + timedelta(days=1)
            expected["before"] = f"Before {cutoff.isoformat()}"
        if (
            self.date_precision in expected
            and self.date_display != expected[self.date_precision]
        ):
            raise ValueError(
                "date_display is inconsistent with date and date_precision"
            )
        if self.date_precision == "month" and not self.date.endswith("-01"):
            raise ValueError("month precision must use the first day as its sort date")
        return self


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    missing_translations: list[str] = field(default_factory=list)
    newest_dates: dict[str, str] = field(default_factory=dict)
    thread_count: int = 0
    entry_count: int = 0

    def load(self, path: Path, schema: type[BaseModel]):
        try:
            return schema.model_validate(read_yaml(path))
        except (OSError, ValueError, yaml.YAMLError) as exc:
            if isinstance(exc, ValidationError):
                for issue in exc.errors():
                    location = ".".join(map(str, issue["loc"]))
                    self.errors.append(f"{path} {location}: {issue['msg']}")
            else:
                self.errors.append(f"{path}: {exc}")
            return None

    def check_links(
        self, path: Path, data, slugs: set[str], location: str = ""
    ) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                self.check_links(path, value, slugs, f"{location}.{key}".lstrip("."))
        elif isinstance(data, list):
            for index, value in enumerate(data):
                self.check_links(path, value, slugs, f"{location}[{index}]")
        elif isinstance(data, str):
            if LEGACY_LINK.search(data):
                self.errors.append(f"{path} {location}: legacy link")
            for slug in THREAD_LINK.findall(data):
                if slug not in slugs:
                    self.errors.append(
                        f"{path} {location}: unknown thread link {slug!r}"
                    )

    def check_translations(self, path: Path, en, de) -> None:
        missing = ["en.plain_summary"] if not en.plain_summary.strip() else []
        en_data = en.model_dump()
        for name, value in de.model_dump().items():
            en_value = en_data.get(name)
            if name == "open_questions":
                if en_value and not value:
                    missing.append(f"de.{name}")
                elif len(en_value or []) != len(value or []):
                    self.errors.append(
                        f"{path}: open_questions count mismatch (en={len(en_value or [])}, de={len(value or [])})"
                    )
                continue
            if not (value.strip() if isinstance(value, str) else value):
                missing.append(f"de.{name}")
        if missing:
            self.missing_translations.append(f"{path}: {', '.join(missing)}")


def validate(content_dir: Path) -> ValidationResult:
    result = ValidationResult()
    directories = thread_directories(content_dir)
    slugs = {directory.name for directory in directories}
    if not directories:
        result.errors.append(f"{content_dir / 'threads'}: no thread directories found")
    for filename, schema in (("groups.yaml", Groups), ("glossary.yaml", Glossary)):
        path = content_dir / filename
        if model := result.load(path, schema):
            result.check_links(path, model.model_dump(), slugs)

    for directory in directories:
        path = directory / "thread.yaml"
        result.thread_count += 1
        if thread := result.load(path, Thread):
            if thread.slug != directory.name:
                result.errors.append(
                    f"{path}: slug {thread.slug!r} does not match directory"
                )
            for slug in thread.related_threads:
                if slug not in slugs:
                    result.errors.append(f"{path}: unknown related thread {slug!r}")
            result.check_links(path, thread.model_dump(), slugs)
            result.check_translations(path, thread.en, thread.de)

        paths = entry_paths(directory)
        if not paths:
            result.errors.append(f"{directory / 'entries'}: no entry files found")
        ids = set()
        dates = []
        for path in paths:
            result.entry_count += 1
            if entry := result.load(path, Entry):
                if entry.id != path.stem:
                    result.errors.append(
                        f"{path}: entry id {entry.id!r} does not match filename"
                    )
                if entry.id in ids:
                    result.errors.append(f"{path}: duplicate entry id {entry.id!r}")
                ids.add(entry.id)
                dates.append(entry.date)
                result.check_links(path, entry.model_dump(), slugs)
                result.check_translations(path, entry.en, entry.de)
        if dates:
            result.newest_dates[directory.name] = max(dates)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-dir", type=Path, default=CONTENT_DIR)
    parser.add_argument("--require-bilingual", action="store_true")
    args = parser.parse_args()
    result = validate(args.content_dir)
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.missing_translations:
        if args.require_bilingual:
            for error in result.missing_translations:
                print(f"ERROR: missing translation or plain summary: {error}")
        else:
            print(
                f"WARNING: {len(result.missing_translations)} files have unfinished translations or plain summaries."
            )
    print(f"Checked {result.thread_count} threads and {result.entry_count} entries.")
    return int(
        bool(result.errors or (args.require_bilingual and result.missing_translations))
    )


if __name__ == "__main__":
    raise SystemExit(main())

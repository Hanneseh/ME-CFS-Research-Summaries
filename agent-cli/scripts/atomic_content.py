"""Shared readers and schema constants for the atomic content files."""

from pathlib import Path
import re

import yaml
from yaml.constructor import ConstructorError

BASE_DIR = Path(__file__).resolve().parents[2]
CONTENT_DIR = BASE_DIR / "content"
GROUPS = (
    "treatments-interventions",
    "disease-models-mechanisms",
    "diagnostics-symptoms-care",
)
EVIDENCE_TIERS = (
    "established",
    "active_trials",
    "early_clinical",
    "mechanistic",
    "hypothesis",
)

# Markdown destinations can be angle-wrapped or contain balanced parentheses.
MARKDOWN_LINK = re.compile(
    r"\[(?P<label>[^\[\]\n]+)\]\("
    r"(?:<(?P<angle>[^<>\n]+)>|(?P<bare>(?:[^\s()<>]|\([^\s()<>]*\))+))\)"
)


class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in mapping:
                raise ConstructorError(
                    "while constructing a content mapping",
                    node.start_mark,
                    f"expected a unique string key, found {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def read_yaml(path: Path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def thread_directories(content_dir: Path) -> list[Path]:
    return sorted(path for path in (content_dir / "threads").glob("*") if path.is_dir())


def entry_paths(thread_dir: Path) -> list[Path]:
    return sorted((thread_dir / "entries").glob("*.yaml"))


def link_destination(match: re.Match) -> str:
    return match["angle"] or match["bare"]


def external_markdown_links(text: str):
    for match in MARKDOWN_LINK.finditer(text):
        url = link_destination(match)
        if url.startswith(("https://", "http://")):
            yield match["label"], url

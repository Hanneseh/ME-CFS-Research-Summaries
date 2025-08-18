import os
import re
from pathlib import Path
import hashlib


# Configuration for file structure
BASE_DIR = Path(__file__).parent.parent
PIECES_DIR = BASE_DIR / "pieces"
INTRO_DIR = PIECES_DIR / "intros"
ROUNDUP_DIRS = {
    "english": PIECES_DIR / "roundups" / "english",
    "german": PIECES_DIR / "roundups" / "german",
}
SUMMARY_DIRS = {
    "english": PIECES_DIR / "summaries" / "english",
    "german": PIECES_DIR / "summaries" / "german",
}

README_PATHS = {"english": BASE_DIR / "README.md", "german": BASE_DIR / "README-de.md"}


def safe_filename(name, max_length=100):
    # Replace spaces and special chars, keep emoji
    name = name.strip()
    name = re.sub(r'[\\/:"*?<>|]', "", name)
    name = name.replace(" ", "_")
    # Truncate if too long, add hash for uniqueness
    if len(name) > max_length:
        hash_part = hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]
        name = name[: max_length - 9] + "_" + hash_part
    return name


def ensure_dirs():
    for d in [INTRO_DIR, *ROUNDUP_DIRS.values(), *SUMMARY_DIRS.values()]:
        d.mkdir(parents=True, exist_ok=True)


def split_readme(readme_path, lang):
    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    # Find intro: everything before the first "###"
    intro_match = re.search(r"^(.*?)(?=^### )", content, re.DOTALL | re.MULTILINE)
    intro = intro_match.group(1).strip() if intro_match else ""
    # Remove trailing markdown comments
    intro = re.sub(r"<!--.*?-->", "", intro, flags=re.DOTALL).strip()

    # Save intro
    intro_filename = "introduction.md" if lang == "english" else "einleitung.md"
    with open(INTRO_DIR / intro_filename, "w", encoding="utf-8") as f:
        f.write(intro.strip() + "\n")

    # Split into sections by "###"
    sections = re.split(r"^(### .+)", content, flags=re.MULTILINE)
    # sections[0] is intro, then pairs of (headline, content)
    for i in range(1, len(sections), 2):
        headline = sections[i].strip()
        body = sections[i + 1].strip() if i + 1 < len(sections) else ""
        # Remove trailing --- delimiter if present
        body = re.sub(r"^---\s*", "", body, flags=re.MULTILINE).strip()
        # Remove trailing markdown comments
        body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()

        # Determine if roundup or summary
        if headline.startswith("### 🎯"):
            # Roundup
            name = headline.replace("### ", "")
            outdir = ROUNDUP_DIRS[lang]
        else:
            # Summary
            name = headline.replace("### ", "")
            outdir = SUMMARY_DIRS[lang]

        filename = safe_filename(name) + ".md"
        with open(outdir / filename, "w", encoding="utf-8") as f:
            f.write(f"{headline}\n\n{body}\n")


if __name__ == "__main__":
    ensure_dirs()
    split_readme(README_PATHS["english"], "english")
    split_readme(README_PATHS["german"], "german")
    print("Splitting complete. Files saved in 'pieces/'.")

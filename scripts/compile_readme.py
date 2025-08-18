from pathlib import Path
import re
import hashlib


# --- New helper for safe filenames (from split_readme.py) ---
def safe_filename(name, max_length=100):
    name = name.strip()
    name = re.sub(r'[\\/:"*?<>|]', "", name)
    name = name.replace(" ", "_")
    if len(name) > max_length:
        hash_part = hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]
        name = name[: max_length - 9] + "_" + hash_part
    return name


# --- New: Rename new/placeholder summary files based on their title ---
def rename_new_summaries(summaries_dir):
    for file in summaries_dir.glob("*.md"):
        # Detect placeholder names (e.g., new_1.md, untitled.md, etc.)
        if re.match(
            r"^(new_\d+|untitled|new|temp|placeholder).*\.md$", file.name, re.IGNORECASE
        ):
            with open(file, encoding="utf-8") as f:
                content = f.read()
            headline, _ = get_headline_and_anchor(content)
            if headline:
                new_name = safe_filename(headline.replace("### ", "")) + ".md"
                new_path = file.parent / new_name
                # Avoid overwriting existing files
                if not new_path.exists():
                    file.rename(new_path)


def get_headline_and_anchor(md_text):
    """
    Extract the first headline (### ...) and generate an anchor for TOC linking.
    """
    match = re.search(r"^(### .+)", md_text, re.MULTILINE)
    if match:
        headline = match.group(1).strip()
        # Anchor: GitHub style (lowercase, spaces and special chars to dash, remove non-alphanum except dash)
        anchor = headline.replace("### ", "").strip()
        anchor = anchor.lower()
        anchor = re.sub(r"[^\w\s\-🎯💊]", "", anchor)
        anchor = anchor.replace(" ", "-")
        return headline, anchor
    return None, None


def get_intro(intro_dir, lang):
    filename = "introduction.md" if lang == "english" else "einleitung.md"
    with open(intro_dir / filename, encoding="utf-8") as f:
        return f.read().strip()


def collect_entries(dir_path):
    # Return list of (filename, content)
    entries = []
    for file in sorted(dir_path.glob("*.md")):
        with open(file, encoding="utf-8") as f:
            entries.append((file.name, f.read().strip()))
    return entries


def compile_readme(lang, out_path, pieces_dir):
    intro_dir = pieces_dir / "intros"
    roundups_dir = pieces_dir / "roundups" / lang
    summaries_dir = pieces_dir / "summaries" / lang

    # --- New: Rename new/placeholder summary files before compiling ---
    rename_new_summaries(summaries_dir)

    # Compose intro
    intro = get_intro(intro_dir, lang)

    # Collect and merge roundups and summaries, then sort all by filename (reverse chronological)
    roundups = collect_entries(roundups_dir)
    summaries = collect_entries(summaries_dir)
    all_entries = roundups + summaries
    all_entries = sorted(all_entries, key=lambda x: x[0], reverse=True)

    # Table of Contents
    toc = []
    for filename, content in all_entries:
        headline, anchor = get_headline_and_anchor(content)
        if headline and anchor:
            toc.append(f"- [{headline.replace('### ', '')}](#{anchor})")

    # Compose full README
    lines = []
    lines.append(intro)
    lines.append(
        "\n## Inhaltsverzeichnis" if lang == "german" else "\n## Table of Contents"
    )
    # Only add TOC entries for roundups and summaries, not intro or TOC itself
    lines.extend(toc)
    lines.append("")
    for filename, content in all_entries:
        lines.append("---")
        lines.append(content)
        lines.append("")
    # Write to output
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    PIECES_DIR = BASE_DIR / "pieces"
    compile_readme("english", BASE_DIR / "README.md", PIECES_DIR)
    compile_readme("german", BASE_DIR / "README-de.md", PIECES_DIR)
    print("Compilation complete. Readmes updated.")

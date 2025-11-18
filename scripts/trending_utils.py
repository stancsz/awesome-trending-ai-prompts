import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_HEADER = ["prompt", "contributor", "comment"]
README_PATH = BASE_DIR / "README.md"
TRENDING_HEADING = "## Trending Prompts Today"
STRUCTURE_HEADING = "## Structure"
DEFAULT_CONTRIBUTOR = "@trend-bot"


def _sanitize_cell(value: str) -> str:
    return (
        value.replace("\n", " ")
        .replace("\r", " ")
        .replace("|", "\\|")
        .strip()
    )


def discover_prompt_dirs(base: Path = BASE_DIR) -> List[Path]:
    """
    Discover provider directories by scanning only the first-level children
    of the repository base directory. This enforces the flattened layout where
    each provider lives at the top level (e.g. `chatgpt-text`, `gemini-image`).
    Exclude any directory whose path parts include 'scripts'.
    """
    dirs: List[Path] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        if "scripts" in child.parts:
            continue
        csv_path = child / "prompts.csv"
        if csv_path.exists():
            dirs.append(child)
    return dirs


def collect_recent_prompts(max_rows: int = 5) -> List[Tuple[str, List[Dict[str, str]]]]:
    trending_data: List[Tuple[str, List[Dict[str, str]]]] = []
    for directory in discover_prompt_dirs():
        csv_path = directory / "prompts.csv"
        if not csv_path.exists():
            continue
        with csv_path.open(encoding="utf-8", newline="") as fh:
            reader = csv.reader(fh)
            next(reader, None)
            rows = [row for row in reader if row]
        entries: List[Dict[str, str]] = []
        for row in rows[-max_rows:]:
            padded = (row + [""] * len(CSV_HEADER))[: len(CSV_HEADER)]
            prompt_value = padded[0].strip()
            if not prompt_value:
                continue
            entries.append(
                {
                    "prompt": prompt_value,
                    "contributor": padded[1].strip() or DEFAULT_CONTRIBUTOR,
                    "comment": padded[2].strip(),
                }
            )
        label = str(directory.relative_to(BASE_DIR)).replace("\\", "/")
        trending_data.append((label, entries))
    return trending_data


def build_readme_section(trending_data: List[Tuple[str, List[Dict[str, str]]]]) -> str:
    lines = [TRENDING_HEADING, "", f"Last refreshed: {datetime.utcnow():%Y-%m-%d %H:%M UTC}", ""]
    lines.append("Each category below lists the most recent prompts stored in its `prompts.csv` (up to five entries).")
    if not trending_data:
        lines.append("No prompts are available yet. Run `python scripts/trend_ingestion.py` to fetch trends and `python scripts/publish_daily_trend.py` to update this section.")
        return "\n".join(lines).rstrip() + "\n"

    lines.append("")
    lines.append("| Provider | Prompt | Contributor | Notes |")
    lines.append("| --- | --- | --- | --- |")
    rows_emitted = False
    for label, entries in trending_data:
        if not entries:
            continue
        provider = _sanitize_cell(label)
        for entry in entries:
            rows_emitted = True
            prompt_cell = _sanitize_cell(entry["prompt"])
            contributor_cell = _sanitize_cell(entry["contributor"])
            comment_cell = _sanitize_cell(entry["comment"])
            lines.append(f"| {provider} | {prompt_cell} | {contributor_cell} | {comment_cell} |")
    if not rows_emitted:
        lines.append("| (no recent prompts) |  |  |  |")

    lines.append("")
    lines.append("To refresh this list:")
    lines.append("")
    lines.append("1. `pip install -r requirements.txt`")
    lines.append("2. Add `PERPLEXITY_API_KEY` and `OPENAI_API_KEY` to `.env`.")
    lines.append("3. Run `python scripts/trend_ingestion.py` to append new prompts to the CSVs.")
    lines.append("4. Run `python scripts/publish_daily_trend.py` to rebuild this section from the latest entries.")
    lines.append("")
    lines.append("Tweak or rerun `python scripts/publish_daily_trend.py` after you update any `prompts.csv` to refresh this list.")
    return "\n".join(lines).rstrip() + "\n"


def update_readme(trending_section: str) -> None:
    if not README_PATH.exists():
        raise FileNotFoundError("README.md not found in repository root.")

    content = README_PATH.read_text(encoding="utf-8")
    start = content.find(TRENDING_HEADING)
    if start == -1:
        raise RuntimeError(f"{TRENDING_HEADING} not found in README.md")

    end = content.find(STRUCTURE_HEADING, start)
    if end == -1:
        raise RuntimeError(f"{STRUCTURE_HEADING} not found; cannot replace trending section.")

    new_content = content[:start] + trending_section + "\n" + content[end:]
    README_PATH.write_text(new_content, encoding="utf-8")

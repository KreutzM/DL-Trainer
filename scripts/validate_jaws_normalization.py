from __future__ import annotations

import re
from pathlib import Path

from common import make_parser, read_json

RAW_DIR = Path("data/raw/JAWS/DE/Converted-Help-Files")
OUTPUT_DIR = Path("data/normalized/JAWS/DE")
HEADING_PROSE_RE = re.compile(r"^#{1,6}\s+.+?[.!?:]\s+\S")


def validate_markdown_structure(md_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    for idx, line in enumerate(lines, start=1):
        prev_line = lines[idx - 2] if idx >= 2 else ""
        next_line = lines[idx] if idx < len(lines) else ""

        if line.strip() == ">":
            raise SystemExit(f"Stray blockquote marker in {md_path}:{idx}")

        if line.startswith("#") and re.search(r"\s#{1,6}\s", line):
            raise SystemExit(f"Multiple headings on one line in {md_path}:{idx}")

        if line.startswith("#") and prev_line != "":
            raise SystemExit(f"Heading not separated from previous block in {md_path}:{idx}")

        if line.startswith("#") and next_line and not next_line.startswith(("#", "-", "*", ">", "```", "|")) and not next_line[:2].isdigit():
            raise SystemExit(f"Heading not separated from following block in {md_path}:{idx}")

        if line.startswith("#") and len(line) > 120 and re.search(r"[.!?]\s+\w+\s+\w+\s+\w+", line):
            raise SystemExit(f"Heading appears merged with prose in {md_path}:{idx}")

        if HEADING_PROSE_RE.search(line):
            raise SystemExit(f"Heading appears merged with trailing prose in {md_path}:{idx}")

        if line.startswith("Quelle:") and prev_line != "":
            raise SystemExit(f"Source marker not separated from previous block in {md_path}:{idx}")

        if line.startswith("Quelle:") and next_line != "":
            raise SystemExit(f"Source marker not separated from following block in {md_path}:{idx}")

        if re.search(r"Quelle:\s+#+\s", line) or (line.startswith("Quelle:") and re.search(r"\s#{1,6}\s", line)):
            raise SystemExit(f"Source marker merged with heading in {md_path}:{idx}")

        if not line.startswith("#") and re.search(r"\s#{1,6}\s", line):
            raise SystemExit(f"Heading merged into prose/list line in {md_path}:{idx}")

        if not line.startswith("Quelle:") and " Quelle:" in line:
            raise SystemExit(f"Source marker merged into prose/list line in {md_path}:{idx}")

        if re.search(r"^(?:- |\d+\.) .+ (?:- |\d+\.) ", line) or re.search(r"^\d+\..+\s\d+\.\s", line):
            raise SystemExit(f"Suspicious merged list items in {md_path}:{idx}")

        if re.search(r"^(?:- |\d+\.) .+ Quelle:", line):
            raise SystemExit(f"List item merged with source marker in {md_path}:{idx}")

        if re.search(r"^(?:- |\d+\.) .+\s#{1,6}\s", line):
            raise SystemExit(f"List item merged with heading in {md_path}:{idx}")


def main() -> None:
    parser = make_parser("Validate the normalized JAWS DE output set against the raw HTML input set.")
    parser.add_argument("--raw-dir", default=str(RAW_DIR))
    parser.add_argument("--normalized-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    repo_root = Path.cwd().resolve()
    raw_dir = (repo_root / args.raw_dir).resolve()
    normalized_dir = (repo_root / args.normalized_dir).resolve()

    raw_files = sorted(raw_dir.glob("*.html"))
    normalized_dirs = sorted(path for path in normalized_dir.iterdir() if path.is_dir())

    if len(raw_files) != len(normalized_dirs):
        raise SystemExit(
            f"Expected {len(raw_files)} normalized directories in {normalized_dir}, found {len(normalized_dirs)}"
        )

    seen_doc_ids: set[str] = set()
    legacy_path_marker = "_".join(["original", "manuals"])

    for raw_file in raw_files:
        stem = raw_file.stem.removeprefix("JAWS_DE_").lower().replace("-", "_")
        target_dir = normalized_dir / stem
        md_path = target_dir / "index.md"
        meta_path = target_dir / "index.meta.json"

        if not md_path.exists() or not meta_path.exists():
            raise SystemExit(f"Missing output pair for {raw_file.name}")

        meta = read_json(meta_path)
        if meta["source_file"] != str(raw_file.relative_to(repo_root)).replace("\\", "/"):
            raise SystemExit(f"source_file mismatch in {meta_path}")
        if meta["normalized_path"] != str(md_path.relative_to(repo_root)).replace("\\", "/"):
            raise SystemExit(f"normalized_path mismatch in {meta_path}")
        if meta["product"] != "JAWS" or meta["language"] != "de":
            raise SystemExit(f"product/language mismatch in {meta_path}")
        if meta["conversion_stage"] != "raw_html_to_normalized_markdown":
            raise SystemExit(f"conversion_stage mismatch in {meta_path}")
        if legacy_path_marker in str(meta):
            raise SystemExit(f"legacy path reference found in {meta_path}")

        validate_markdown_structure(md_path)

        doc_id = meta["doc_id"]
        if doc_id in seen_doc_ids:
            raise SystemExit(f"Duplicate doc_id {doc_id}")
        seen_doc_ids.add(doc_id)

    print(f"OK: {len(raw_files)} JAWS DE sources mapped to normalized markdown+metadata pairs")


if __name__ == "__main__":
    main()

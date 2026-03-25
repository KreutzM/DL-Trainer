from __future__ import annotations

from pathlib import Path

from common import make_parser, read_json

RAW_DIR = Path("data/raw/JAWS/DE/Converted-Help-Files")
OUTPUT_DIR = Path("data/normalized/JAWS/DE")


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

        doc_id = meta["doc_id"]
        if doc_id in seen_doc_ids:
            raise SystemExit(f"Duplicate doc_id {doc_id}")
        seen_doc_ids.add(doc_id)

    print(f"OK: {len(raw_files)} JAWS DE sources mapped to normalized markdown+metadata pairs")


if __name__ == "__main__":
    main()

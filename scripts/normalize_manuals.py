from __future__ import annotations

from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from common import make_parser, read_json, sha256_file, write_json


def html_to_markdown(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav"]):
        tag.decompose()
    return md(str(soup), heading_style="ATX")


def txt_to_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> None:
    parser = make_parser("Normalize a raw HTML/TXT source into markdown and metadata.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--source-meta", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--pipeline-version", default="0.1.0")
    args = parser.parse_args()

    source = Path(args.source)
    output_md = Path(args.output_md)
    output_meta = output_md.with_suffix(".meta.json")

    if source.suffix.lower() in {".html", ".htm"}:
        content = html_to_markdown(source)
    else:
        content = txt_to_markdown(source)

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(content.strip() + "\n", encoding="utf-8")

    meta = read_json(Path(args.source_meta))
    meta["normalized_from"] = str(source)
    meta["normalized_file"] = str(output_md)
    meta["normalized_checksum"] = sha256_file(output_md)
    meta["transform_pipeline_version"] = args.pipeline_version
    write_json(output_meta, meta)
    print(f"Normalized: {output_md}")


if __name__ == "__main__":
    main()

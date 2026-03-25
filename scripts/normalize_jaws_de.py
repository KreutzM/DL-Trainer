from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup, NavigableString, Tag

from common import make_parser, read_json, sha256_file, write_json

PIPELINE_VERSION = "0.1.0"
PRODUCT = "JAWS"
LANGUAGE = "de"
RAW_DIR = Path("data/raw/JAWS/DE/Converted-Help-Files")
OUTPUT_DIR = Path("data/normalized/JAWS/DE")
MANIFEST_PATH = RAW_DIR / "collection_manifest.json"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"^jaws_de_", "", value)
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def relative_path(path: Path, repo_root: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")


def iter_significant_siblings(tag: Tag) -> Iterable[Tag]:
    sibling = tag.next_sibling
    while sibling is not None:
        if isinstance(sibling, Tag):
            yield sibling
        elif isinstance(sibling, NavigableString) and sibling.strip():
            break
        sibling = sibling.next_sibling


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def collapse_inline(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def format_table(table: Tag) -> str:
    rows: list[list[str]] = []
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if not cells:
            continue
        rows.append([collapse_inline(cell.get_text(" ", strip=True)) for cell in cells])

    if not rows:
        return ""

    column_count = max(len(row) for row in rows)
    normalized_rows = [row + [""] * (column_count - len(row)) for row in rows]
    header = normalized_rows[0]
    separator = ["---"] * column_count
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in normalized_rows[1:]:
        lines.append("| " + " | ".join(row) + " |")

    summary = collapse_inline(table.get("summary", ""))
    if summary:
        return f"Tabelle: {summary}\n\n" + "\n".join(lines)
    return "\n".join(lines)


def render_node(node: Tag | NavigableString, level: int = 0) -> str:
    if isinstance(node, NavigableString):
        return collapse_inline(str(node))

    name = node.name.lower()
    if name in {"script", "style", "nav"}:
        return ""
    if name == "br":
        return "\n"
    if name in {"strong", "b"}:
        return f"**{collapse_inline(node.get_text(' ', strip=True))}**"
    if name in {"em", "i"}:
        return f"*{collapse_inline(node.get_text(' ', strip=True))}*"
    if name == "code" and node.parent and node.parent.name != "pre":
        return f"`{collapse_inline(node.get_text(' ', strip=True))}`"
    if name == "a":
        text = collapse_inline(node.get_text(" ", strip=True))
        href = node.get("href")
        if href and text:
            return f"[{text}]({href})"
        return text
    if name == "pre":
        code = node.get_text("\n", strip=False).strip("\n")
        if not code:
            return ""
        return f"```\n{code}\n```"
    if name == "blockquote":
        lines = [collapse_inline(line) for line in node.get_text("\n", strip=True).splitlines() if collapse_inline(line)]
        return "\n".join(f"> {line}" for line in lines)
    if name in {"ul", "ol"}:
        items = []
        for idx, li in enumerate(node.find_all("li", recursive=False), start=1):
            prefix = f"{idx}." if name == "ol" else "-"
            rendered = render_node(li, level + 1).strip()
            if not rendered:
                continue
            item_lines = rendered.splitlines()
            items.append(f"{prefix} {item_lines[0]}")
            items.extend(("  " * (level + 1)) + line for line in item_lines[1:] if line.strip())
        return "\n".join(items)
    if name == "li":
        block_children = {"ul", "ol", "table", "pre", "blockquote", "p"}
        inline_parts = []
        block_parts = []
        for child in node.children:
            rendered = render_node(child, level + 1).strip()
            if rendered:
                if isinstance(child, Tag) and child.name.lower() in block_children:
                    block_parts.append(rendered)
                else:
                    inline_parts.append(rendered)
        parts = []
        if inline_parts:
            parts.append(collapse_inline(" ".join(inline_parts)))
        parts.extend(block_parts)
        return "\n".join(parts)
    if name == "table":
        return format_table(node)
    if name and re.fullmatch(r"h[1-6]", name):
        heading_level = int(name[1])
        text = collapse_inline(node.get_text(" ", strip=True))
        return f"{'#' * heading_level} {text}" if text else ""
    if name == "p":
        return collapse_inline(" ".join(render_node(child, level) for child in node.children))

    parts = []
    for child in node.children:
        rendered = render_node(child, level).strip()
        if rendered:
            parts.append(rendered)
    return "\n\n".join(parts)


def clean_html(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "nav"]):
        tag.decompose()

    body = soup.body or soup
    title_tag = body.find("h1")
    title = title_tag.get_text(" ", strip=True) if title_tag else ""

    for selector in ["div.toc", "div.meta"]:
        for tag in body.select(selector):
            tag.decompose()

    for tag in body.find_all("hr"):
        tag.decompose()

    for src_tag in body.select("div.src"):
        source_text = src_tag.get_text(" ", strip=True)
        src_tag.name = "p"
        src_tag.attrs = {}
        src_tag.string = source_text

    for text_node in list(body.find_all(string=True)):
        if text_node.strip() in {">", "Â"}:
            text_node.extract()

    headings = body.find_all(["h2", "h3", "h4", "h5", "h6"])
    for heading in headings:
        siblings = iter_significant_siblings(heading)
        next_tag = next(siblings, None)
        if next_tag and next_tag.name == "h1":
            current = heading.get_text(" ", strip=True)
            following = next_tag.get_text(" ", strip=True)
            if current == following:
                next_tag.decompose()

    blocks = []
    for child in body.children:
        if isinstance(child, NavigableString) and not child.strip():
            continue
        rendered = render_node(child).strip()
        if rendered:
            blocks.append(rendered)

    markdown = "\n\n".join(blocks)
    return title, normalize_text(markdown)


def build_metadata(
    *,
    repo_root: Path,
    source_file: Path,
    output_md: Path,
    manifest: dict,
    title: str,
    pipeline_version: str,
) -> dict:
    stem = slugify(source_file.stem)
    source_rel = relative_path(source_file, repo_root)
    normalized_rel = relative_path(output_md, repo_root)
    source_dir_rel = relative_path(source_file.parent, repo_root)
    import_date_iso = datetime.fromtimestamp(source_file.stat().st_mtime, tz=timezone.utc).date().isoformat()

    return {
        "doc_id": f"jaws_de_{stem}",
        "product": PRODUCT,
        "language": LANGUAGE,
        "version": manifest["collection_id"],
        "source_type": "html",
        "source_file": source_rel,
        "source_path": source_dir_rel,
        "normalized_path": normalized_rel,
        "checksum": sha256_file(source_file),
        "import_date": import_date_iso,
        "conversion_stage": "raw_html_to_normalized_markdown",
        "transform_pipeline_version": pipeline_version,
        "provenance": {
            "raw_collection_id": manifest["collection_id"],
            "raw_collection_manifest": relative_path(MANIFEST_PATH, repo_root),
            "source_of_truth_path": manifest["source_of_truth_path"],
            "source_checksum": sha256_file(source_file),
        },
        "notes": (
            "Normalized from imported or conversion-derived JAWS DE help HTML without "
            "aggressive semantic reordering; TOC and presentation-only wrappers were removed."
        ),
        "title": title,
    }


def main() -> None:
    parser = make_parser("Normalize JAWS DE help HTML files into markdown plus metadata.")
    parser.add_argument("--source-dir", default=str(RAW_DIR))
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--pipeline-version", default=PIPELINE_VERSION)
    args = parser.parse_args()

    repo_root = Path.cwd().resolve()
    source_dir = (repo_root / args.source_dir).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    manifest = read_json(repo_root / MANIFEST_PATH)

    sources = sorted(source_dir.glob("*.html"))
    if not sources:
        raise SystemExit(f"No HTML sources found in {source_dir}")

    for source_file in sources:
        stem = slugify(source_file.stem)
        target_dir = output_dir / stem
        output_md = target_dir / "index.md"
        output_meta = target_dir / "index.meta.json"

        title, markdown = clean_html(source_file.read_text(encoding="utf-8", errors="ignore"))

        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(markdown, encoding="utf-8")

        meta = build_metadata(
            repo_root=repo_root,
            source_file=source_file,
            output_md=output_md,
            manifest=manifest,
            title=title,
            pipeline_version=args.pipeline_version,
        )
        write_json(output_meta, meta)
        print(f"Normalized: {relative_path(output_md, repo_root)}")


if __name__ == "__main__":
    main()

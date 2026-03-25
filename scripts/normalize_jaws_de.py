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
HEADING_PROSE_RE = re.compile(r"^(#{1,6}\s+.+?[.!?:])[ \t]+(\S.*)$")


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


def tighten_inline_spacing(text: str) -> str:
    text = collapse_inline(text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([(\[]) +", r"\1", text)
    text = re.sub(r" +([)\]])", r"\1", text)
    text = re.sub(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)\s+([,.;:!?])", r"\1\2", text)
    text = re.sub(r"([(\[])\s+(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", r"\1\2", text)
    text = re.sub(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)\s+([)\]])", r"\1\2", text)
    return text.strip()


def render_inline(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return str(node).replace("\xa0", " ")

    name = node.name.lower()
    if name == "br":
        return "\n"
    if name in {"strong", "b"}:
        return f" **{tighten_inline_spacing(node.get_text(' ', strip=True))}** "
    if name in {"em", "i"}:
        return f" *{tighten_inline_spacing(node.get_text(' ', strip=True))}* "
    if name == "code" and node.parent and node.parent.name != "pre":
        return f" `{tighten_inline_spacing(node.get_text(' ', strip=True))}` "
    if name == "a":
        text = tighten_inline_spacing("".join(render_inline(child) for child in node.children))
        href = node.get("href")
        if href and text:
            return f"[{text}]({href})"
        return text
    if name == "img":
        return tighten_inline_spacing(node.get("alt", ""))
    if name in {"script", "style", "nav"}:
        return ""
    return "".join(render_inline(child) for child in node.children)


def render_paragraph(node: Tag) -> str:
    raw = "".join(render_inline(child) for child in node.children).replace("\r\n", "\n")
    lines = raw.split("\n")
    normalized_lines: list[str] = []
    blank_pending = False

    for line in lines:
        cleaned = tighten_inline_spacing(line) if line.strip() else ""
        if cleaned:
            if blank_pending and normalized_lines:
                normalized_lines.append("")
            normalized_lines.append(cleaned)
            blank_pending = False
        elif normalized_lines:
            blank_pending = True

    return "\n".join(normalized_lines).strip()


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


def blockify_text(text: str) -> list[str]:
    normalized = normalize_text(text).strip()
    if not normalized:
        return []
    return normalized.split("\n\n")


def normalize_markdown_inline_spacing(text: str) -> str:
    return text


def blockify_inline_fragments(fragments: list[str]) -> list[str]:
    merged: list[str] = []
    for fragment in fragments:
        if not fragment:
            continue
        if not merged:
            merged.append(fragment)
            continue

        previous = merged[-1]
        if (
            previous.endswith((" ", "\n"))
            or fragment.startswith((" ", "\n", ",", ".", ";", ":", "!", "?", ")", "]"))
        ):
            merged.append(fragment)
        else:
            merged.append(f" {fragment}")

    raw = "".join(merged).replace("\r\n", "\n")
    lines = raw.split("\n")
    blocks: list[str] = []
    current_lines: list[str] = []

    for line in lines:
        cleaned = tighten_inline_spacing(line) if line.strip() else ""
        if cleaned:
            current_lines.append(cleaned)
            continue
        if current_lines:
            blocks.append("\n".join(current_lines))
            current_lines = []

    if current_lines:
        blocks.append("\n".join(current_lines))

    return blocks


def format_list(items: list[tuple[str, list[str]]], level: int = 0) -> str:
    lines: list[str] = []
    indent = "  " * level
    child_indent = "  " * (level + 1)

    for prefix, blocks in items:
        if not blocks:
            continue
        first, *rest = blocks
        first_lines = first.splitlines()
        lines.append(f"{indent}{prefix} {first_lines[0]}")
        for continuation in first_lines[1:]:
            lines.append(f"{child_indent}{continuation}")
        for block in rest:
            lines.append("")
            for block_line in block.splitlines():
                lines.append(f"{child_indent}{block_line}")

    return "\n".join(lines)


def split_structural_line(line: str) -> list[str]:
    raw = line.rstrip()
    stripped = raw.strip()
    if not stripped or stripped == ">":
        return []
    if stripped.startswith("|"):
        return [raw]

    parts: list[str] = []
    remaining = raw

    while remaining:
        if remaining.lstrip() == remaining and remaining.startswith("Quelle:"):
            source_match = re.match(r"Quelle:\s*[^\n#]+", remaining)
            if source_match:
                parts.append(tighten_inline_spacing(source_match.group(0)))
                remaining = remaining[source_match.end() :].lstrip()
                continue

        heading_match = re.search(r"(?<!\S)(#{1,6}\s+)", remaining)
        source_match = re.search(r"(?<!\S)(Quelle:\s+)", remaining)

        structural_match = None
        if heading_match and source_match:
            structural_match = heading_match if heading_match.start() < source_match.start() else source_match
        else:
            structural_match = heading_match or source_match

        if structural_match is None:
            parts.append(remaining)
            break
        if structural_match.start() == 0:
            parts.append(remaining.lstrip())
            break

        prefix = remaining[: structural_match.start()].rstrip()
        if prefix.strip():
            parts.append(prefix)
        remaining = remaining[structural_match.start() :].lstrip()

    return [part for part in parts if part]


def split_heading_prose_line(line: str) -> list[str]:
    match = HEADING_PROSE_RE.match(line.strip())
    if not match:
        return [line]
    heading, prose = match.groups()
    if len(prose.split()) < 3:
        return [line]
    return [heading, prose]


def repair_markdown_blocks(markdown: str) -> str:
    repaired_blocks: list[str] = []

    for block in blockify_text(markdown):
        split_lines: list[str] = []
        for line in block.splitlines():
            for structural_line in split_structural_line(line):
                split_lines.extend(split_heading_prose_line(structural_line))

        if not split_lines:
            continue

        current_block: list[str] = []
        for line in split_lines:
            is_structural = line.startswith("#") or line.startswith("Quelle:")
            if is_structural and current_block:
                repaired_blocks.append("\n".join(current_block).strip())
                current_block = []
            current_block.append(line)
            if is_structural:
                repaired_blocks.append("\n".join(current_block).strip())
                current_block = []

        if current_block:
            repaired_blocks.append("\n".join(current_block).strip())

    normalized = normalize_text("\n\n".join(block for block in repaired_blocks if block))
    return normalize_text(normalize_markdown_inline_spacing(normalized))


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
        start_index = 1
        if name == "ol":
            start_attr = node.get("start")
            if isinstance(start_attr, str) and start_attr.isdigit():
                start_index = int(start_attr)
        items = []
        for idx, li in enumerate(node.find_all("li", recursive=False), start=start_index):
            prefix = f"{idx}." if name == "ol" else "-"
            blocks = render_list_item(li, level + 1)
            if not blocks:
                continue
            items.append((prefix, blocks))
        return format_list(items, level)
    if name == "li":
        return "\n\n".join(render_list_item(node, level))
    if name == "table":
        return format_table(node)
    if name and re.fullmatch(r"h[1-6]", name):
        heading_level = int(name[1])
        text = collapse_inline(node.get_text(" ", strip=True))
        return f"{'#' * heading_level} {text}" if text else ""
    if name == "p":
        return render_paragraph(node)

    parts = []
    for child in node.children:
        rendered = render_node(child, level).strip()
        if rendered:
            parts.append(rendered)
    return "\n\n".join(parts)


def render_list_item(node: Tag, level: int) -> list[str]:
    blocks: list[str] = []
    inline_parts: list[str] = []
    block_tags = {"p", "ul", "ol", "table", "pre", "blockquote"}

    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child).replace("\xa0", " ")
            if text:
                inline_parts.append(text)
            continue

        child_name = child.name.lower()
        if child_name in block_tags:
            if inline_parts:
                blocks.extend(blockify_inline_fragments(inline_parts))
                inline_parts = []

            if child_name == "p":
                paragraph = render_paragraph(child)
                if paragraph:
                    blocks.extend(blockify_text(paragraph))
            else:
                rendered = render_node(child, level).strip()
                if rendered:
                    blocks.extend(blockify_text(rendered))
            continue

        rendered_inline = render_inline(child)
        if rendered_inline:
            inline_parts.append(rendered_inline)

    if inline_parts:
        blocks.extend(blockify_inline_fragments(inline_parts))

    return blocks


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
    return title, repair_markdown_blocks(markdown)


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

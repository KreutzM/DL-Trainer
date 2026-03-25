from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from common import read_json, write_jsonl


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+)")
NUMBERED_STEP_RE = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)
SOURCE_MARKER_RE = re.compile(r"^\s*Quelle:\s*", re.IGNORECASE)
WARNING_RE = re.compile(r"\b(?:Hinweis|Achtung|Warnung|Wichtig)\b", re.IGNORECASE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ0-9])")


@dataclass
class Section:
    section_id: str
    section_title: str
    section_path: list[str]
    heading_level: int
    heading_line: int
    lines: list[tuple[int, str]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build section-aware chunk artifacts for normalized JAWS DE manuals."
    )
    parser.add_argument("--normalized-root", default="data/normalized/JAWS/DE")
    parser.add_argument("--output-root", default="data/derived/chunks/JAWS/DE")
    parser.add_argument("--max-chars", type=int, default=2200)
    parser.add_argument("--target-chars", type=int, default=1500)
    parser.add_argument("--min-chars", type=int, default=450)
    parser.add_argument("--min-meaningful-chars", type=int, default=80)
    parser.add_argument("--transform-pipeline-version", default="0.2.0")
    return parser.parse_args()


def slugify(text: str) -> str:
    normalized = text.casefold()
    normalized = (
        normalized.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return normalized or "section"


def summarize_text(text: str, limit: int = 180) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def parse_sections(markdown_text: str, doc_id: str) -> list[Section]:
    sections: list[Section] = []
    stack: list[dict] = []
    slug_counts: defaultdict[tuple[str, ...], int] = defaultdict(int)
    current: dict | None = None

    for line_no, line in enumerate(markdown_text.splitlines(), start=1):
        match = HEADING_RE.match(line)
        if not match:
            if current is not None:
                current["lines"].append((line_no, line))
            continue

        if current is not None and any(text.strip() for _, text in current["lines"]):
            sections.append(
                Section(
                    section_id=current["section_id"],
                    section_title=current["section_title"],
                    section_path=current["section_path"],
                    heading_level=current["heading_level"],
                    heading_line=current["heading_line"],
                    lines=current["lines"],
                )
            )

        level = len(match.group(1))
        title = match.group(2).strip()

        while stack and stack[-1]["heading_level"] >= level:
            stack.pop()

        base_slug = slugify(title)
        path_key = tuple([part["slug_token"] for part in stack] + [base_slug])
        slug_counts[path_key] += 1
        occurrence = slug_counts[path_key]
        slug_token = base_slug if occurrence == 1 else f"{base_slug}_{occurrence:02d}"

        current = {
            "section_id": f"{doc_id}::sec_" + "__".join([part["slug_token"] for part in stack] + [slug_token]),
            "section_title": title,
            "section_path": [part["section_title"] for part in stack] + [title],
            "heading_level": level,
            "heading_line": line_no,
            "lines": [],
        }
        stack.append(
            {
                "section_title": title,
                "heading_level": level,
                "slug_token": slug_token,
            }
        )

    if current is not None and any(text.strip() for _, text in current["lines"]):
        sections.append(
            Section(
                section_id=current["section_id"],
                section_title=current["section_title"],
                section_path=current["section_path"],
                heading_level=current["heading_level"],
                heading_line=current["heading_line"],
                lines=current["lines"],
            )
        )

    return sections


def make_blocks(lines: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    blocks: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []

    for line_no, line in lines:
        if line.strip():
            current.append((line_no, line))
            continue
        if current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)

    merged: list[list[tuple[int, str]]] = []
    idx = 0
    while idx < len(blocks):
        block = blocks[idx]
        block_text = "\n".join(line for _, line in block).strip()
        next_block = blocks[idx + 1] if idx + 1 < len(blocks) else None
        if (
            next_block
            and len(block_text) < 220
            and not any(LIST_RE.match(line) for _, line in block)
            and any(LIST_RE.match(line) for _, line in next_block)
        ):
            merged.append(block + [(0, "")] + next_block)
            idx += 2
            continue
        merged.append(block)
        idx += 1
    return merged


def pack_text_units(
    units: list[dict],
    *,
    max_chars: int,
    target_chars: int,
    min_chars: int,
) -> list[list[dict]]:
    groups: list[list[dict]] = []
    current: list[dict] = []
    current_size = 0

    for unit in units:
        unit_size = len(unit["text"])
        join_cost = 2 if current else 0

        if (
            current
            and current_size + join_cost + unit_size > max_chars
            and (
                current_size >= min_chars
                or unit_size >= target_chars
                or current_size >= max(160, min_chars // 2)
            )
        ):
            groups.append(current)
            current = []
            current_size = 0

        if current and current_size >= target_chars and unit_size > max(160, max_chars // 4):
            groups.append(current)
            current = []
            current_size = 0

        current.append(unit)
        current_size = current_size + join_cost + unit_size

    if current:
        groups.append(current)

    return groups


def refine_oversized_units(units: list[dict], max_chars: int, target_chars: int) -> list[dict]:
    refined: list[dict] = []
    for unit in units:
        if len(unit["text"]) <= max_chars:
            refined.append(unit)
            continue

        paragraph = re.sub(r"\s+", " ", unit["text"]).strip()
        sentences = [part.strip() for part in SENTENCE_SPLIT_RE.split(paragraph) if part.strip()]
        if len(sentences) > 1:
            sentence_units = [{"text": sentence} for sentence in sentences]
            packed = pack_text_units(sentence_units, max_chars=max_chars, target_chars=target_chars, min_chars=0)
            for group in packed:
                refined.append(
                    {
                        "text": " ".join(part["text"] for part in group).strip(),
                        "line_start": unit["line_start"],
                        "line_end": unit["line_end"],
                    }
                )
            continue

        start = 0
        while start < len(paragraph):
            end = min(len(paragraph), start + target_chars)
            if end < len(paragraph):
                split_at = paragraph.rfind(" ", start, end)
                if split_at > start:
                    end = split_at
            piece = paragraph[start:end].strip()
            if piece:
                refined.append(
                    {
                        "text": piece,
                        "line_start": unit["line_start"],
                        "line_end": unit["line_end"],
                    }
                )
            start = end + 1
    return refined


def split_large_block(block: list[tuple[int, str]], max_chars: int, target_chars: int) -> list[dict]:
    text = "\n".join(line for _, line in block).strip()
    if len(text) <= max_chars:
        return [
            {
                "text": text,
                "line_start": min(line_no for line_no, _ in block if line_no > 0),
                "line_end": max(line_no for line_no, _ in block if line_no > 0),
            }
        ]

    list_groups: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    seen_list = False
    for line_no, line in block:
        if line_no == 0:
            continue
        if LIST_RE.match(line) and current and seen_list:
            list_groups.append(current)
            current = [(line_no, line)]
            continue
        if LIST_RE.match(line):
            seen_list = True
        current.append((line_no, line))
    if current:
        list_groups.append(current)

    if len(list_groups) > 1:
        list_units = [
            {
                "text": "\n".join(line for _, line in group).strip(),
                "line_start": min(line_no for line_no, _ in group),
                "line_end": max(line_no for line_no, _ in group),
            }
            for group in list_groups
        ]
        packed = pack_text_units(list_units, max_chars=max_chars, target_chars=target_chars, min_chars=0)
        return refine_oversized_units([
            {
                "text": "\n\n".join(unit["text"] for unit in group).strip(),
                "line_start": min(unit["line_start"] for unit in group),
                "line_end": max(unit["line_end"] for unit in group),
            }
            for group in packed
        ], max_chars=max_chars, target_chars=target_chars)

    paragraph = re.sub(r"\s+", " ", text).strip()
    sentences = [part.strip() for part in SENTENCE_SPLIT_RE.split(paragraph) if part.strip()]
    if len(sentences) > 1:
        sentence_units = [{"text": sentence} for sentence in sentences]
        packed = pack_text_units(sentence_units, max_chars=max_chars, target_chars=target_chars, min_chars=0)
        line_start = min(line_no for line_no, _ in block if line_no > 0)
        line_end = max(line_no for line_no, _ in block if line_no > 0)
        return refine_oversized_units([
            {
                "text": " ".join(unit["text"] for unit in group).strip(),
                "line_start": line_start,
                "line_end": line_end,
            }
            for group in packed
        ], max_chars=max_chars, target_chars=target_chars)

    pieces: list[dict] = []
    start = 0
    line_start = min(line_no for line_no, _ in block if line_no > 0)
    line_end = max(line_no for line_no, _ in block if line_no > 0)
    while start < len(paragraph):
        end = min(len(paragraph), start + target_chars)
        if end < len(paragraph):
            split_at = paragraph.rfind(" ", start, end)
            if split_at > start:
                end = split_at
        piece = paragraph[start:end].strip()
        if piece:
            pieces.append({"text": piece, "line_start": line_start, "line_end": line_end})
        start = end + 1
    return refine_oversized_units(pieces, max_chars=max_chars, target_chars=target_chars)


def split_section(section: Section, *, max_chars: int, target_chars: int, min_chars: int, min_meaningful_chars: int) -> list[dict]:
    units: list[dict] = []
    for block in make_blocks(section.lines):
        units.extend(split_large_block(block, max_chars=max_chars, target_chars=target_chars))

    packed = pack_text_units(units, max_chars=max_chars, target_chars=target_chars, min_chars=min_chars)
    chunks: list[dict] = []
    for group in packed:
        text = "\n\n".join(unit["text"] for unit in group).strip()
        if len(text) < min_meaningful_chars:
            continue
        chunks.append(
            {
                "text": text,
                "line_start": min(unit["line_start"] for unit in group),
                "line_end": max(unit["line_end"] for unit in group),
            }
        )
    return chunks


def infer_chunk_type(section_title: str, content: str) -> str:
    if WARNING_RE.search(content):
        return "warning"
    if re.search(r"\bFAQ\b", section_title, re.IGNORECASE):
        return "faq"
    if "|" in content and re.search(r"\b(?:Tabelle|Spalte|Spalten)\b", section_title, re.IGNORECASE):
        return "table"
    if NUMBERED_STEP_RE.search(content):
        return "procedure"
    if LIST_RE.search(content):
        return "reference"
    return "concept"


def build_doc_chunks(
    normalized_md: Path,
    output_root: Path,
    *,
    max_chars: int,
    target_chars: int,
    min_chars: int,
    min_meaningful_chars: int,
    transform_pipeline_version: str,
) -> tuple[Path, list[dict]]:
    meta_path = normalized_md.with_suffix(".meta.json")
    meta = read_json(meta_path)
    markdown_text = normalized_md.read_text(encoding="utf-8")
    sections = parse_sections(markdown_text, meta["doc_id"])

    doc_folder = output_root / normalized_md.parent.name
    chunk_path = doc_folder / "chunks.jsonl"
    chunk_path_str = chunk_path.as_posix()
    rows: list[dict] = []
    doc_chunk_index = 0

    for section in sections:
        section_chunks = split_section(
            section,
            max_chars=max_chars,
            target_chars=target_chars,
            min_chars=min_chars,
            min_meaningful_chars=min_meaningful_chars,
        )
        for section_chunk_index, chunk in enumerate(section_chunks, start=1):
            doc_chunk_index += 1
            content = chunk["text"]
            source_span = f"{meta['normalized_path']}#L{chunk['line_start']}-L{chunk['line_end']}"
            rows.append(
                {
                    "chunk_id": f"{section.section_id}::chunk_{section_chunk_index:02d}",
                    "doc_id": meta["doc_id"],
                    "product": meta["product"],
                    "language": meta["language"],
                    "version": meta["version"],
                    "source_path": meta["source_path"],
                    "source_file": meta["source_file"],
                    "normalized_path": meta["normalized_path"],
                    "chunk_path": chunk_path_str,
                    "section_id": section.section_id,
                    "section_title": section.section_title,
                    "section_path": section.section_path,
                    "section_path_text": " > ".join(section.section_path),
                    "heading_level": section.heading_level,
                    "chunk_index": doc_chunk_index,
                    "chunk_index_in_section": section_chunk_index,
                    "char_count": len(content),
                    "conversion_stage": "normalized_markdown_to_section_aware_chunks",
                    "transform_pipeline_version": transform_pipeline_version,
                    "contains_list": bool(LIST_RE.search(content)),
                    "contains_steps": bool(NUMBERED_STEP_RE.search(content)),
                    "contains_source_marker": bool(SOURCE_MARKER_RE.search(content)),
                    "chunk_type": infer_chunk_type(section.section_title, content),
                    "title": section.section_title,
                    "summary": summarize_text(content),
                    "content": content,
                    "source_spans": [source_span],
                    "review_status": "auto_generated",
                    "provenance": {
                        "doc_id": meta["doc_id"],
                        "section_id": section.section_id,
                        "normalized_path": meta["normalized_path"],
                        "raw_source_file": meta["source_file"],
                        "raw_source_root": meta["source_path"],
                        "raw_collection_manifest": meta["provenance"]["raw_collection_manifest"],
                        "transform_pipeline_version": transform_pipeline_version,
                        "upstream_conversion_stage": meta["conversion_stage"],
                        "source_spans": [
                            {
                                "path": meta["normalized_path"],
                                "line_start": chunk["line_start"],
                                "line_end": chunk["line_end"],
                                "heading_line": section.heading_line,
                                "section_path": section.section_path,
                            }
                        ],
                    },
                }
            )

    for row in rows:
        row["chunk_count_in_doc"] = len(rows)
        section_chunk_count = sum(1 for other in rows if other["section_id"] == row["section_id"])
        row["section_chunk_count"] = section_chunk_count

    write_jsonl(chunk_path, rows)
    return chunk_path, rows


def main() -> None:
    args = parse_args()
    normalized_root = Path(args.normalized_root)
    output_root = Path(args.output_root)
    md_paths = sorted(normalized_root.glob("*/index.md"))
    if not md_paths:
        raise SystemExit(f"No normalized JAWS DE manuals found under {normalized_root}")

    for normalized_md in md_paths:
        chunk_path, rows = build_doc_chunks(
            normalized_md,
            output_root,
            max_chars=args.max_chars,
            target_chars=args.target_chars,
            min_chars=args.min_chars,
            min_meaningful_chars=args.min_meaningful_chars,
            transform_pipeline_version=args.transform_pipeline_version,
        )
        print(f"Wrote {len(rows):4d} chunks -> {chunk_path.as_posix()}")


if __name__ == "__main__":
    main()

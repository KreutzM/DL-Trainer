from __future__ import annotations

import argparse
from pathlib import Path

from jsonschema import Draft202012Validator

from common import read_json, read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate JAWS DE chunk artifacts.")
    parser.add_argument("--normalized-root", default="data/normalized/JAWS/DE")
    parser.add_argument("--chunks-root", default="data/derived/chunks/JAWS/DE")
    parser.add_argument("--schema", default="schemas/chunk.schema.json")
    parser.add_argument("--min-char-count", type=int, default=80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    normalized_root = Path(args.normalized_root)
    chunks_root = Path(args.chunks_root)
    validator = Draft202012Validator(read_json(Path(args.schema)))

    failures: list[str] = []
    summaries: list[str] = []

    for meta_path in sorted(normalized_root.glob("*/index.meta.json")):
        meta = read_json(meta_path)
        chunk_file = chunks_root / meta_path.parent.name / "chunks.jsonl"
        if not chunk_file.exists():
            failures.append(f"{meta['doc_id']}: missing {chunk_file.as_posix()}")
            continue

        rows = read_jsonl(chunk_file)
        if not rows:
            failures.append(f"{meta['doc_id']}: no chunks generated")
            continue

        expected_indices = list(range(1, len(rows) + 1))
        actual_indices = [row.get("chunk_index") for row in rows]
        if actual_indices != expected_indices:
            failures.append(f"{meta['doc_id']}: chunk_index sequence broken")

        if {row.get("chunk_count_in_doc") for row in rows} != {len(rows)}:
            failures.append(f"{meta['doc_id']}: chunk_count_in_doc mismatch")

        for idx, row in enumerate(rows, start=1):
            for error in validator.iter_errors(row):
                failures.append(f"{meta['doc_id']} row {idx}: {error.message}")

            if row.get("doc_id") != meta["doc_id"]:
                failures.append(f"{meta['doc_id']} row {idx}: doc_id mismatch")
            if row.get("product") != meta["product"] or row.get("language") != meta["language"]:
                failures.append(f"{meta['doc_id']} row {idx}: product/language mismatch")
            if row.get("source_path") != meta["source_path"]:
                failures.append(f"{meta['doc_id']} row {idx}: source_path mismatch")
            if row.get("source_file") != meta["source_file"]:
                failures.append(f"{meta['doc_id']} row {idx}: source_file mismatch")
            if row.get("normalized_path") != meta["normalized_path"]:
                failures.append(f"{meta['doc_id']} row {idx}: normalized_path mismatch")
            if row.get("chunk_path") != chunk_file.as_posix():
                failures.append(f"{meta['doc_id']} row {idx}: chunk_path mismatch")
            if row.get("char_count") != len(row.get("content", "")):
                failures.append(f"{meta['doc_id']} row {idx}: char_count mismatch")
            if row.get("char_count", 0) < args.min_char_count:
                failures.append(f"{meta['doc_id']} row {idx}: chunk too small ({row.get('char_count')})")
            if not isinstance(row.get("section_path"), list) or not row["section_path"]:
                failures.append(f"{meta['doc_id']} row {idx}: empty section_path")
            if not row.get("source_spans"):
                failures.append(f"{meta['doc_id']} row {idx}: missing source_spans")

            provenance = row.get("provenance", {})
            spans = provenance.get("source_spans", [])
            if provenance.get("doc_id") != meta["doc_id"]:
                failures.append(f"{meta['doc_id']} row {idx}: provenance.doc_id mismatch")
            if provenance.get("section_id") != row.get("section_id"):
                failures.append(f"{meta['doc_id']} row {idx}: provenance.section_id mismatch")
            if provenance.get("normalized_path") != meta["normalized_path"]:
                failures.append(f"{meta['doc_id']} row {idx}: provenance.normalized_path mismatch")
            if provenance.get("raw_source_file") != meta["source_file"]:
                failures.append(f"{meta['doc_id']} row {idx}: provenance.raw_source_file mismatch")
            if provenance.get("transform_pipeline_version") != row.get("transform_pipeline_version"):
                failures.append(f"{meta['doc_id']} row {idx}: provenance pipeline version mismatch")
            if not spans:
                failures.append(f"{meta['doc_id']} row {idx}: missing provenance.source_spans")
            else:
                first_span = spans[0]
                line_start = first_span.get("line_start")
                line_end = first_span.get("line_end")
                if first_span.get("path") != meta["normalized_path"]:
                    failures.append(f"{meta['doc_id']} row {idx}: span path mismatch")
                if not isinstance(line_start, int) or not isinstance(line_end, int) or line_start > line_end:
                    failures.append(f"{meta['doc_id']} row {idx}: invalid line range")

        summaries.append(f"{meta['doc_id']}: {len(rows)} chunks")

    if failures:
        print("\n".join(failures))
        raise SystemExit(1)

    for summary in summaries:
        print(summary)
    print("OK: JAWS DE chunk artifacts validated")


if __name__ == "__main__":
    main()

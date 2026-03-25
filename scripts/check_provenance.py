from __future__ import annotations

from pathlib import Path

from common import make_parser, read_jsonl


def has_source_records(row: dict) -> bool:
    return bool(row.get("provenance", {}).get("source_records"))


def main() -> None:
    parser = make_parser("Check JSONL rows for minimal provenance fields.")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    rows = read_jsonl(Path(args.input))
    failures = []
    for idx, row in enumerate(rows, start=1):
        if "messages" in row and "meta" in row:
            meta = row["meta"]
            if not meta.get("source_doc_ids"):
                failures.append(f"Row {idx}: missing meta.source_doc_ids")
            if not meta.get("review_status"):
                failures.append(f"Row {idx}: missing meta.review_status")
            if not has_source_records(row):
                failures.append(f"Row {idx}: missing provenance.source_records")
            continue

        if "prompt" in row and "source_doc_ids" in row:
            if not row.get("source_doc_ids"):
                failures.append(f"Row {idx}: missing source_doc_ids")
            if not row.get("review_status"):
                failures.append(f"Row {idx}: missing review_status")
            if not has_source_records(row):
                failures.append(f"Row {idx}: missing provenance.source_records")
            continue

        if "source_doc_ids" in row and "gold_source_path" in row:
            if not row.get("source_doc_ids"):
                failures.append(f"Row {idx}: missing source_doc_ids")
            if not row.get("review_status"):
                failures.append(f"Row {idx}: missing review_status")
            if not row.get("gold_source_path"):
                failures.append(f"Row {idx}: missing gold_source_path")
            if not has_source_records(row):
                failures.append(f"Row {idx}: missing provenance.source_records")
            continue

        if "output_id" in row and "candidate" in row:
            if not row.get("source_doc_ids"):
                failures.append(f"Row {idx}: missing source_doc_ids")
            if not row.get("source_chunk_ids"):
                failures.append(f"Row {idx}: missing source_chunk_ids")
            if not row.get("review_status"):
                failures.append(f"Row {idx}: missing review_status")
            if not has_source_records(row):
                failures.append(f"Row {idx}: missing provenance.source_records")
            continue

        if "output_id" in row and "parsed_response" in row:
            if not row.get("source_doc_ids"):
                failures.append(f"Row {idx}: missing source_doc_ids")
            if not row.get("source_chunk_ids"):
                failures.append(f"Row {idx}: missing source_chunk_ids")
            if not row.get("response_status"):
                failures.append(f"Row {idx}: missing response_status")
            if not has_source_records(row):
                failures.append(f"Row {idx}: missing provenance.source_records")
            continue

        for key in ["doc_id", "source_spans", "review_status"]:
            if key not in row or row.get(key) in (None, "", []):
                failures.append(f"Row {idx}: missing {key}")

    if failures:
        print("\\n".join(failures))
        raise SystemExit(1)

    print(f"OK: provenance present in {len(rows)} rows")
    raise SystemExit(0)


if __name__ == "__main__":
    main()

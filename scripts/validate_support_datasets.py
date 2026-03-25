from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from common import make_parser, read_json, read_jsonl


def load_chunks(chunks_root: Path) -> dict[str, dict]:
    chunk_index: dict[str, dict] = {}
    for path in sorted(chunks_root.glob("*/chunks.jsonl")):
        for row in read_jsonl(path):
            chunk_index[row["chunk_id"]] = row
    if not chunk_index:
        raise SystemExit(f"No chunk files found under {chunks_root}")
    return chunk_index


def validate_sft(rows: list[dict], validator: Draft202012Validator, chunk_index: dict[str, dict]) -> list[str]:
    failures: list[str] = []
    for idx, row in enumerate(rows, start=1):
        for error in validator.iter_errors(row):
            failures.append(f"SFT row {idx}: {error.message}")

        messages = row.get("messages", [])
        if len(messages) < 3:
            failures.append(f"SFT row {idx}: requires at least system, user, assistant")
        else:
            if messages[0].get("role") != "system":
                failures.append(f"SFT row {idx}: first message must be system")
            if not any(msg.get("role") == "user" for msg in messages):
                failures.append(f"SFT row {idx}: missing user message")
            if messages[-1].get("role") != "assistant":
                failures.append(f"SFT row {idx}: last message must be assistant")
            if not messages[-1].get("content", "").strip():
                failures.append(f"SFT row {idx}: empty assistant output")

        meta = row.get("meta", {})
        if row.get("source_chunk_ids") != meta.get("source_chunk_ids"):
            failures.append(f"SFT row {idx}: source_chunk_ids mismatch between top level and meta")
        if row.get("source_doc_ids") != meta.get("source_doc_ids"):
            failures.append(f"SFT row {idx}: source_doc_ids mismatch between top level and meta")

        for chunk_id in row.get("source_chunk_ids", []):
            if chunk_id not in chunk_index:
                failures.append(f"SFT row {idx}: unknown chunk_id {chunk_id}")
                continue
            chunk = chunk_index[chunk_id]
            if chunk["doc_id"] not in row.get("source_doc_ids", []):
                failures.append(f"SFT row {idx}: doc/chunk mismatch for {chunk_id}")

        source_records = row.get("provenance", {}).get("source_records", [])
        if len(source_records) != len(row.get("source_chunk_ids", [])):
            failures.append(f"SFT row {idx}: provenance.source_records count mismatch")
    return failures


def validate_eval(rows: list[dict], validator: Draft202012Validator, chunk_index: dict[str, dict]) -> list[str]:
    failures: list[str] = []
    for idx, row in enumerate(rows, start=1):
        for error in validator.iter_errors(row):
            failures.append(f"Eval row {idx}: {error.message}")

        if not row.get("prompt", "").strip():
            failures.append(f"Eval row {idx}: empty prompt")
        if not row.get("expected_behavior", "").strip():
            failures.append(f"Eval row {idx}: empty expected_behavior")

        for chunk_id in row.get("source_chunk_ids", []):
            if chunk_id not in chunk_index:
                failures.append(f"Eval row {idx}: unknown chunk_id {chunk_id}")
                continue
            chunk = chunk_index[chunk_id]
            if chunk["doc_id"] not in row.get("source_doc_ids", []):
                failures.append(f"Eval row {idx}: doc/chunk mismatch for {chunk_id}")

        source_records = row.get("provenance", {}).get("source_records", [])
        if len(source_records) != len(row.get("source_chunk_ids", [])):
            failures.append(f"Eval row {idx}: provenance.source_records count mismatch")
    return failures


def main() -> None:
    parser = make_parser("Validate SFT and eval support artifacts against schemas and chunk references.")
    parser.add_argument("--sft", required=True)
    parser.add_argument("--eval", required=True)
    parser.add_argument("--chunks-root", default="data/derived/chunks/JAWS/DE")
    parser.add_argument("--sft-schema", default="schemas/sft_sample.schema.json")
    parser.add_argument("--eval-schema", default="schemas/eval_case.schema.json")
    args = parser.parse_args()

    chunk_index = load_chunks(Path(args.chunks_root))
    sft_rows = read_jsonl(Path(args.sft))
    eval_rows = read_jsonl(Path(args.eval))

    failures: list[str] = []
    failures.extend(validate_sft(sft_rows, Draft202012Validator(read_json(Path(args.sft_schema))), chunk_index))
    failures.extend(validate_eval(eval_rows, Draft202012Validator(read_json(Path(args.eval_schema))), chunk_index))

    sft_chunk_ids = {chunk_id for row in sft_rows for chunk_id in row.get("source_chunk_ids", [])}
    eval_chunk_ids = {chunk_id for row in eval_rows for chunk_id in row.get("source_chunk_ids", [])}
    overlap = sorted(sft_chunk_ids & eval_chunk_ids)
    if overlap:
        failures.append("Train/eval chunk overlap detected: " + ", ".join(overlap[:10]))

    if failures:
        print("\n".join(failures))
        raise SystemExit(1)

    print(f"OK: {len(sft_rows)} SFT rows, {len(eval_rows)} eval rows, no chunk overlap")


if __name__ == "__main__":
    main()

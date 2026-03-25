from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from common import make_parser, read_json, read_jsonl


def _validate_rows(rows: list[dict], schema_path: Path, label: str) -> None:
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for idx, row in enumerate(rows, start=1):
        for err in validator.iter_errors(row):
            errors.append(f"{label} row {idx}: {err.message}")
    if errors:
        raise ValueError("\n".join(errors))


def _assistant_message(row: dict) -> str:
    messages = row["messages"]
    return messages[-1]["content"].strip()


def main() -> None:
    parser = make_parser("Validate a Qwen SFT export directory.")
    parser.add_argument("--input-dir", required=True)
    args = parser.parse_args()

    root = Path(args.input_dir)
    train_path = root / "train.jsonl"
    eval_path = root / "eval.jsonl"
    train_meta_path = root / "train.metadata.jsonl"
    eval_meta_path = root / "eval.metadata.jsonl"
    manifest_path = root / "manifest.json"

    required_paths = [train_path, eval_path, train_meta_path, eval_meta_path, manifest_path]
    missing = [path.as_posix() for path in required_paths if not path.exists()]
    if missing:
        raise SystemExit(f"Missing export files: {', '.join(missing)}")

    train_rows = read_jsonl(train_path)
    eval_rows = read_jsonl(eval_path)
    train_meta_rows = read_jsonl(train_meta_path)
    eval_meta_rows = read_jsonl(eval_meta_path)
    manifest = read_json(manifest_path)

    repo_root = Path(__file__).resolve().parents[1]
    _validate_rows(train_rows, repo_root / "schemas" / "qwen_sft_record.schema.json", "train")
    _validate_rows(eval_rows, repo_root / "schemas" / "qwen_sft_record.schema.json", "eval")
    _validate_rows(train_meta_rows, repo_root / "schemas" / "qwen_sft_metadata.schema.json", "train metadata")
    _validate_rows(eval_meta_rows, repo_root / "schemas" / "qwen_sft_metadata.schema.json", "eval metadata")

    if len(train_rows) != len(train_meta_rows):
        raise SystemExit("Train export and train metadata row count differ")
    if len(eval_rows) != len(eval_meta_rows):
        raise SystemExit("Eval export and eval metadata row count differ")

    train_ids = {row["id"] for row in train_rows}
    eval_ids = {row["id"] for row in eval_rows}
    if train_ids & eval_ids:
        raise SystemExit(f"Train/eval id overlap detected: {sorted(train_ids & eval_ids)}")

    if any(not _assistant_message(row) for row in [*train_rows, *eval_rows]):
        raise SystemExit("Found empty assistant message in export")

    train_meta_ids = {row["id"] for row in train_meta_rows}
    eval_meta_ids = {row["id"] for row in eval_meta_rows}
    if train_ids != train_meta_ids:
        raise SystemExit("Train metadata ids do not match train export ids")
    if eval_ids != eval_meta_ids:
        raise SystemExit("Eval metadata ids do not match eval export ids")

    train_chunks = {chunk_id for row in train_meta_rows for chunk_id in row["source_chunk_ids"]}
    eval_chunks = {chunk_id for row in eval_meta_rows for chunk_id in row["source_chunk_ids"]}
    if train_chunks & eval_chunks:
        raise SystemExit(f"Train/eval chunk overlap detected: {sorted(train_chunks & eval_chunks)}")

    if manifest.get("train_records") != len(train_rows):
        raise SystemExit("Manifest train_records mismatch")
    if manifest.get("eval_records") != len(eval_rows):
        raise SystemExit("Manifest eval_records mismatch")
    if manifest.get("split_chunk_overlap") != []:
        raise SystemExit("Manifest split_chunk_overlap must be empty")

    print(
        f"OK: {root.as_posix()} ({len(train_rows)} train, {len(eval_rows)} eval, no split collisions)"
    )


if __name__ == "__main__":
    main()

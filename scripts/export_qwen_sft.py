from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from common import find_repo_root, make_parser, read_jsonl, sha256_file, write_json, write_jsonl

EXPORT_PIPELINE_VERSION = "0.2.0"


def _load_behavior_spec(repo_root: Path, path_str: str | None) -> str:
    if not path_str:
        return ""
    path = Path(path_str)
    if not path.is_absolute():
        path = repo_root / path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load_rows(paths: list[Path]) -> list[tuple[Path, dict]]:
    loaded: list[tuple[Path, dict]] = []
    for path in paths:
        for row in read_jsonl(path):
            loaded.append((path, row))
    return loaded


def _validate_split_rows(rows: list[tuple[Path, dict]], split: str) -> None:
    ids: set[str] = set()
    for source_path, row in rows:
        row_id = row.get("id") or row.get("eval_id")
        _require(isinstance(row_id, str) and row_id, f"Missing id in {source_path}")
        _require(row_id not in ids, f"Duplicate id {row_id} in {split} rows")
        ids.add(row_id)
        _require(row.get("split") == split, f"{row_id} has split {row.get('split')} instead of {split}")
        _require(
            row.get("review_status") == "promoted",
            f"{row_id} in {source_path} is not promoted",
        )
        chunk_ids = row.get("source_chunk_ids")
        _require(isinstance(chunk_ids, list) and chunk_ids, f"{row_id} is missing source_chunk_ids")


def _chunk_ids(rows: list[tuple[Path, dict]]) -> set[str]:
    ids: set[str] = set()
    for _, row in rows:
        ids.update(row.get("source_chunk_ids", []))
    return ids


def _export_train_row(row: dict) -> dict:
    messages = row["messages"]
    _require(isinstance(messages, list) and messages, f"{row['id']} has no messages")
    _require(messages[-1]["role"] == "assistant", f"{row['id']} does not end with assistant")
    _require(messages[-1]["content"].strip(), f"{row['id']} has empty assistant message")
    return {"id": row["id"], "messages": messages}


def _export_eval_row(repo_root: Path, row: dict) -> dict:
    behavior_spec_path = row.get("provenance", {}).get("behavior_spec_path")
    behavior_spec = _load_behavior_spec(repo_root, behavior_spec_path)
    messages = []
    if behavior_spec:
        messages.append({"role": "system", "content": behavior_spec})
    messages.append({"role": "user", "content": row["prompt"]})
    messages.append({"role": "assistant", "content": row["reference_answer"]})
    _require(messages[-1]["content"].strip(), f"{row['eval_id']} has empty reference answer")
    return {"id": row["eval_id"], "messages": messages}


def _metadata_row(row: dict, source_path: Path, split: str, record_type: str, exported_id: str) -> dict:
    return {
        "id": exported_id,
        "split": split,
        "record_type": record_type,
        "product": row.get("product"),
        "language": row.get("language"),
        "task_type": row.get("task_type"),
        "case_type": row.get("case_type"),
        "source_doc_ids": row.get("source_doc_ids", []),
        "source_chunk_ids": row.get("source_chunk_ids", []),
        "teacher_model": row.get("teacher_model"),
        "teacher_run_id": row.get("teacher_run_id"),
        "teacher_prompt_version": row.get("teacher_prompt_version"),
        "generation_mode": row.get("generation_mode"),
        "review_status": row.get("review_status"),
        "approved_by": row.get("approved_by"),
        "gold_source_path": source_path.as_posix(),
        "promoted_from": row.get("promoted_from"),
        "provenance": row.get("provenance", {}),
        "expected_behavior": row.get("expected_behavior"),
        "reference_answer": row.get("reference_answer"),
        "rubric": row.get("rubric"),
    }


def _file_info(path: Path) -> dict[str, str | int]:
    return {
        "path": path.as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def export_qwen_sft(
    train_inputs: list[Path],
    eval_inputs: list[Path],
    output_dir: Path,
    export_id: str,
) -> None:
    repo_root = find_repo_root(Path.cwd())
    train_rows = _load_rows(train_inputs)
    eval_rows = _load_rows(eval_inputs)
    _require(train_rows, "No train rows loaded")
    _require(eval_rows, "No eval rows loaded")
    _validate_split_rows(train_rows, "train")
    _validate_split_rows(eval_rows, "eval")

    overlap = _chunk_ids(train_rows) & _chunk_ids(eval_rows)
    _require(not overlap, f"Train/eval chunk overlap detected: {sorted(overlap)}")

    export_train_rows = [_export_train_row(row) for _, row in train_rows]
    export_eval_rows = [_export_eval_row(repo_root, row) for _, row in eval_rows]
    train_metadata_rows = [
        _metadata_row(row, source_path, "train", "sft_train", row["id"])
        for source_path, row in train_rows
    ]
    eval_metadata_rows = [
        _metadata_row(row, source_path, "eval", "sft_eval", row["eval_id"])
        for source_path, row in eval_rows
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    train_path = output_dir / "train.jsonl"
    eval_path = output_dir / "eval.jsonl"
    train_meta_path = output_dir / "train.metadata.jsonl"
    eval_meta_path = output_dir / "eval.metadata.jsonl"
    manifest_path = output_dir / "manifest.json"

    write_jsonl(train_path, export_train_rows)
    write_jsonl(eval_path, export_eval_rows)
    write_jsonl(train_meta_path, train_metadata_rows)
    write_jsonl(eval_meta_path, eval_metadata_rows)

    source_counts = Counter()
    for meta_row in [*train_metadata_rows, *eval_metadata_rows]:
        for source_doc_id in meta_row["source_doc_ids"]:
            source_counts[source_doc_id] += 1

    manifest = {
        "export_id": export_id,
        "export_generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "format": "qwen_openai_messages",
        "export_pipeline_version": EXPORT_PIPELINE_VERSION,
        "output_dir": output_dir.as_posix(),
        "train_records": len(export_train_rows),
        "eval_records": len(export_eval_rows),
        "train_metadata_records": len(train_metadata_rows),
        "eval_metadata_records": len(eval_metadata_rows),
        "train_file": train_path.as_posix(),
        "eval_file": eval_path.as_posix(),
        "train_metadata_file": train_meta_path.as_posix(),
        "eval_metadata_file": eval_meta_path.as_posix(),
        "source_train_files": [path.as_posix() for path in train_inputs],
        "source_eval_files": [path.as_posix() for path in eval_inputs],
        "source_inputs": {
            "train": [_file_info(path) for path in train_inputs],
            "eval": [_file_info(path) for path in eval_inputs],
        },
        "hashes": {
            "train_file_sha256": sha256_file(train_path),
            "eval_file_sha256": sha256_file(eval_path),
            "train_metadata_file_sha256": sha256_file(train_meta_path),
            "eval_metadata_file_sha256": sha256_file(eval_meta_path),
        },
        "file_sizes_bytes": {
            "train_file": train_path.stat().st_size,
            "eval_file": eval_path.stat().st_size,
            "train_metadata_file": train_meta_path.stat().st_size,
            "eval_metadata_file": eval_meta_path.stat().st_size,
        },
        "source_doc_distribution": dict(sorted(source_counts.items())),
        "split_chunk_overlap": [],
    }
    previous_manifest_size: int | None = None
    while True:
        write_json(manifest_path, manifest)
        current_manifest_size = manifest_path.stat().st_size
        if previous_manifest_size == current_manifest_size:
            break
        manifest["file_sizes_bytes"]["manifest_file"] = current_manifest_size
        previous_manifest_size = current_manifest_size

    print(
        f"Exported {len(export_train_rows)} train and {len(export_eval_rows)} eval rows to {output_dir.as_posix()}"
    )


def main() -> None:
    parser = make_parser("Export promoted gold rows into Qwen-compatible OpenAI-messages JSONL files.")
    parser.add_argument("--train-input", action="append", required=True, dest="train_inputs")
    parser.add_argument("--eval-input", action="append", required=True, dest="eval_inputs")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--export-id", default="qwen_sft_export_v1")
    args = parser.parse_args()

    export_qwen_sft(
        train_inputs=[Path(path) for path in args.train_inputs],
        eval_inputs=[Path(path) for path in args.eval_inputs],
        output_dir=Path(args.output_dir),
        export_id=args.export_id,
    )


if __name__ == "__main__":
    main()

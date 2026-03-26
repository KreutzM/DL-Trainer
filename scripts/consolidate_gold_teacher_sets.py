from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json, write_jsonl


RUN_PRIORITY = {
    "jaws_de_wave2_codex_gpt54_run_v1": 60,
    "jaws_de_wave1_codex_gpt54_run_v2": 50,
    "jaws_de_wave1_codex_gpt54_run_v1": 45,
}
PROVIDER_PRIORITY = {"codex": 3, "openai": 2, "local": 1, None: 0}
MODEL_PRIORITY = {"gpt-5.4": 3, "teacher-stub-no-llm": 1, "template-seed-no-llm": 0}


def load_rows(directory: Path, kind: str, ignored_names: set[str]) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(directory.glob("*.jsonl")):
        if path.name in ignored_names:
            continue
        for row in read_jsonl(path):
            copied = dict(row)
            copied["_source_file"] = path.name
            copied["_kind"] = kind
            rows.append(copied)
    return rows


def row_rank(row: dict) -> tuple[int, int, int, int, int]:
    return (
        MODEL_PRIORITY.get(row.get("teacher_model"), 0),
        PROVIDER_PRIORITY.get(row.get("teacher_provider"), 0),
        RUN_PRIORITY.get(row.get("teacher_run_id"), 0),
        1 if row.get("_kind") == "eval" else 0,
        1 if row.get("promoted_from", {}).get("teacher_output_path", "").find("scaleup") >= 0 else 0,
    )


def better_row(left: dict, right: dict) -> dict:
    if row_rank(left) != row_rank(right):
        return left if row_rank(left) > row_rank(right) else right
    left_id = left.get("id") or left.get("eval_id") or ""
    right_id = right.get("id") or right.get("eval_id") or ""
    return left if left_id <= right_id else right


def parse_args() -> Any:
    parser = make_parser("Consolidate promoted gold train/eval datasets into de-duplicated files.")
    parser.add_argument("--train-dir", required=True)
    parser.add_argument("--eval-dir", required=True)
    parser.add_argument("--train-output", required=True)
    parser.add_argument("--eval-output", required=True)
    parser.add_argument("--report-output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ignored_names = {Path(args.train_output).name, Path(args.eval_output).name}
    train_rows = load_rows(Path(args.train_dir), "train", ignored_names)
    eval_rows = load_rows(Path(args.eval_dir), "eval", ignored_names)

    best_by_chunk: dict[str, dict] = {}
    candidates_by_chunk: dict[str, list[dict]] = defaultdict(list)
    for row in train_rows + eval_rows:
        chunk_id = row["source_chunk_ids"][0]
        candidates_by_chunk[chunk_id].append(row)
        current = best_by_chunk.get(chunk_id)
        if current is None:
            best_by_chunk[chunk_id] = row
        else:
            best_by_chunk[chunk_id] = better_row(current, row)

    consolidated_train: list[dict] = []
    consolidated_eval: list[dict] = []
    dropped_rows: list[dict] = []

    for chunk_id, candidates in sorted(candidates_by_chunk.items()):
        winner = best_by_chunk[chunk_id]
        for candidate in candidates:
            if candidate is winner:
                continue
            dropped_rows.append(
                {
                    "chunk_id": chunk_id,
                    "dropped_split": candidate["_kind"],
                    "dropped_file": candidate["_source_file"],
                    "kept_split": winner["_kind"],
                    "kept_file": winner["_source_file"],
                    "kept_teacher_model": winner.get("teacher_model"),
                    "dropped_teacher_model": candidate.get("teacher_model"),
                }
            )
        clean_row = {key: value for key, value in winner.items() if not key.startswith("_")}
        if winner["_kind"] == "train":
            consolidated_train.append(clean_row)
        else:
            consolidated_eval.append(clean_row)

    write_jsonl(Path(args.train_output), consolidated_train)
    write_jsonl(Path(args.eval_output), consolidated_eval)
    report = {
        "input_train_rows": len(train_rows),
        "input_eval_rows": len(eval_rows),
        "consolidated_train_rows": len(consolidated_train),
        "consolidated_eval_rows": len(consolidated_eval),
        "dropped_rows": len(dropped_rows),
        "dropped_by_kept_split": dict(Counter(row["kept_split"] for row in dropped_rows)),
        "consolidated_train_by_task_type": dict(Counter(row["task_type"] for row in consolidated_train)),
        "consolidated_eval_by_task_type": dict(Counter(row["case_type"] for row in consolidated_eval)),
        "consolidated_train_by_doc": dict(Counter(row["source_doc_ids"][0] for row in consolidated_train)),
        "consolidated_eval_by_doc": dict(Counter(row["source_doc_ids"][0] for row in consolidated_eval)),
        "drop_examples": dropped_rows[:20],
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote consolidated train -> {args.train_output}")
    print(f"Wrote consolidated eval -> {args.eval_output}")
    print(f"Wrote report -> {args.report_output}")


if __name__ == "__main__":
    main()

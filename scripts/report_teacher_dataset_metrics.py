from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json


TASK_ORDER = [
    "faq_direct_answer",
    "troubleshooting",
    "step_by_step",
    "clarification",
    "uncertainty_escalation",
]


def load_dir_rows(directory: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(directory.glob("*.jsonl")):
        rows.extend(read_jsonl(path))
    return rows


def normalize_task(row: dict, kind: str) -> str:
    return row["task_type"] if kind == "train" else row["case_type"]


def message_preview(row: dict) -> str:
    if "messages" in row:
        for message in row["messages"]:
            if message.get("role") == "assistant":
                return str(message.get("content", "")).strip()
    return str(row.get("reference_answer", "")).strip()


def build_samples(rows: list[dict], kind: str, limit: int) -> list[dict]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        buckets[normalize_task(row, kind)].append(row)
    samples: list[dict] = []
    for task in TASK_ORDER:
        if len(samples) >= limit:
            break
        for row in buckets.get(task, [])[:2]:
            promoted_from = row.get("promoted_from") or {}
            samples.append(
                {
                    "split": kind,
                    "task_type": normalize_task(row, kind),
                    "doc_id": row["source_doc_ids"][0],
                    "chunk_id": row["source_chunk_ids"][0],
                    "preview": message_preview(row),
                    "provenance": {
                        "teacher_run_id": row.get("teacher_run_id"),
                        "teacher_model": row.get("teacher_model"),
                        "teacher_provider": row.get("teacher_provider"),
                        "promoted_from_output_id": promoted_from.get("output_id"),
                        "source_spans": row["provenance"]["source_records"][0].get("source_spans", []),
                    },
                }
            )
            if len(samples) >= limit:
                break
    return samples


def parse_args() -> Any:
    parser = make_parser("Summarize teacher outputs and promoted gold datasets.")
    parser.add_argument("--teacher-outputs-dir", required=True)
    parser.add_argument("--gold-train-dir", required=True)
    parser.add_argument("--gold-eval-dir", required=True)
    parser.add_argument("--output")
    parser.add_argument("--sample-limit", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    teacher_rows = load_dir_rows(Path(args.teacher_outputs_dir))
    train_rows = load_dir_rows(Path(args.gold_train_dir))
    eval_rows = load_dir_rows(Path(args.gold_eval_dir))

    train_chunk_ids = {chunk_id for row in train_rows for chunk_id in row.get("source_chunk_ids", [])}
    eval_chunk_ids = {chunk_id for row in eval_rows for chunk_id in row.get("source_chunk_ids", [])}
    split_collisions = sorted(train_chunk_ids & eval_chunk_ids)

    report = {
        "teacher_outputs_total": len(teacher_rows),
        "teacher_outputs_gpt54": sum(1 for row in teacher_rows if row.get("teacher_model") == "gpt-5.4"),
        "reviewed_outputs": sum(1 for row in teacher_rows if row.get("review_status") == "human_reviewed"),
        "gold_train_total": len(train_rows),
        "gold_eval_total": len(eval_rows),
        "gold_train_by_task_type": dict(Counter(row["task_type"] for row in train_rows)),
        "gold_eval_by_task_type": dict(Counter(row["case_type"] for row in eval_rows)),
        "gold_train_by_doc": dict(Counter(row["source_doc_ids"][0] for row in train_rows)),
        "gold_eval_by_doc": dict(Counter(row["source_doc_ids"][0] for row in eval_rows)),
        "split_collision_count": len(split_collisions),
        "split_collision_examples": split_collisions[:10],
        "train_duplicate_chunk_count": sum(count - 1 for count in Counter(chunk_id for row in train_rows for chunk_id in row.get("source_chunk_ids", [])).values() if count > 1),
        "eval_duplicate_chunk_count": sum(count - 1 for count in Counter(chunk_id for row in eval_rows for chunk_id in row.get("source_chunk_ids", [])).values() if count > 1),
        "samples": build_samples(train_rows, "train", args.sample_limit // 2) + build_samples(eval_rows, "eval", args.sample_limit - args.sample_limit // 2),
    }

    if args.output:
        write_json(Path(args.output), report)
        print(f"Wrote report -> {args.output}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json


DEFAULT_TRAIN_APPROVAL_TARGETS = {
    "clarification": 10,
    "uncertainty_escalation": 10,
    "step_by_step": 18,
    "troubleshooting": 18,
    "faq_direct_answer": 24,
}
DEFAULT_EVAL_APPROVAL_TARGETS = {
    "clarification": 4,
    "uncertainty_escalation": 4,
    "step_by_step": 4,
    "troubleshooting": 4,
    "faq_direct_answer": 6,
}
TASK_ORDER = [
    "clarification",
    "step_by_step",
    "uncertainty_escalation",
    "troubleshooting",
    "faq_direct_answer",
]


def parse_target_args(values: list[str], defaults: dict[str, int]) -> dict[str, int]:
    targets = dict(defaults)
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid target override '{value}', expected task=count")
        task_type, count_text = value.split("=", 1)
        if task_type not in targets:
            raise SystemExit(f"Unknown task type in override: {task_type}")
        try:
            count = int(count_text)
        except ValueError as exc:
            raise SystemExit(f"Invalid count in override '{value}'") from exc
        if count < 0:
            raise SystemExit(f"Target count must be non-negative: {value}")
        targets[task_type] = count
    return targets


def load_chunk_exclusions(paths: list[str], directories: list[str]) -> set[str]:
    chunk_ids: set[str] = set()
    for path_str in paths:
        for row in read_jsonl(Path(path_str)):
            chunk_ids.update(row.get("source_chunk_ids", []))
    for directory_str in directories:
        directory = Path(directory_str)
        for path in sorted(directory.glob("*.jsonl")):
            for row in read_jsonl(path):
                chunk_ids.update(row.get("source_chunk_ids", []))
    return chunk_ids


def round_robin_ids(grouped: dict[str, list[dict]], target: int, selected: list[str], used_chunks: set[str]) -> None:
    for doc_id, rows in grouped.items():
        rows.sort(key=lambda row: (-int(row.get("quality_score", 0)), row["output_id"]))
        grouped[doc_id] = rows
    ordered_docs = sorted(grouped)
    while len(selected) < target:
        progressed = False
        for doc_id in ordered_docs:
            bucket = grouped.get(doc_id)
            if not bucket:
                continue
            while bucket and set(bucket[0].get("source_chunk_ids", [])) & used_chunks:
                bucket.pop(0)
            if not bucket:
                continue
            row = bucket.pop(0)
            used_chunks.update(row.get("source_chunk_ids", []))
            selected.append(row["output_id"])
            progressed = True
            if len(selected) >= target:
                break
        if not progressed:
            break


def parse_args() -> Any:
    parser = make_parser("Select a deterministic high-confidence review subset from a teacher wave.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--approve-output", required=True)
    parser.add_argument("--reject-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--train-target", action="append", default=[])
    parser.add_argument("--eval-target", action="append", default=[])
    parser.add_argument("--min-quality-score", type=int, default=42)
    parser.add_argument("--reject-limit", type=int, default=24)
    parser.add_argument("--exclude-jsonl", action="append", default=[])
    parser.add_argument("--exclude-dir", action="append", default=[])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(Path(args.input))
    train_targets = parse_target_args(args.train_target, DEFAULT_TRAIN_APPROVAL_TARGETS)
    eval_targets = parse_target_args(args.eval_target, DEFAULT_EVAL_APPROVAL_TARGETS)
    excluded_chunk_ids = load_chunk_exclusions(args.exclude_jsonl, args.exclude_dir)

    train_grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    eval_grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    low_confidence: list[dict] = []
    excluded_rows = 0

    for row in rows:
        if row.get("review_status") != "teacher_generated":
            continue
        source_chunk_ids = set(row.get("source_chunk_ids", []))
        if source_chunk_ids & excluded_chunk_ids:
            excluded_rows += 1
            continue
        split = row["target_split"]
        task_type = row["task_type"]
        doc_id = row["source_doc_ids"][0]
        if int(row.get("quality_score", 0)) < args.min_quality_score:
            low_confidence.append(row)
            continue
        if split == "train":
            train_grouped[task_type][doc_id].append(row)
        else:
            eval_grouped[task_type][doc_id].append(row)

    approve_ids: list[str] = []
    shortages: dict[str, dict[str, int]] = {"train": {}, "eval": {}}
    used_chunks = set(excluded_chunk_ids)

    for task_type in TASK_ORDER:
        selected_ids: list[str] = []
        round_robin_ids(train_grouped[task_type], train_targets[task_type], selected_ids, used_chunks)
        shortages["train"][task_type] = max(0, train_targets[task_type] - len(selected_ids))
        approve_ids.extend(selected_ids)
    for task_type in TASK_ORDER:
        selected_ids = []
        round_robin_ids(eval_grouped[task_type], eval_targets[task_type], selected_ids, used_chunks)
        shortages["eval"][task_type] = max(0, eval_targets[task_type] - len(selected_ids))
        approve_ids.extend(selected_ids)

    approve_set = set(approve_ids)
    reject_ids = [
        row["output_id"]
        for row in sorted(low_confidence, key=lambda row: (int(row.get("quality_score", 0)), row["output_id"]))[: args.reject_limit]
        if row["output_id"] not in approve_set
    ]

    Path(args.approve_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.approve_output).write_text("\n".join(approve_ids) + ("\n" if approve_ids else ""), encoding="utf-8")
    Path(args.reject_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.reject_output).write_text("\n".join(reject_ids) + ("\n" if reject_ids else ""), encoding="utf-8")

    approved_rows = [row for row in rows if row["output_id"] in approve_set]
    report = {
        "approved": len(approve_ids),
        "rejected": len(reject_ids),
        "excluded_rows": excluded_rows,
        "min_quality_score": args.min_quality_score,
        "train_targets": train_targets,
        "eval_targets": eval_targets,
        "shortages": shortages,
        "approved_by_split": dict(Counter(row["target_split"] for row in approved_rows)),
        "approved_by_task_type": dict(Counter(row["task_type"] for row in approved_rows)),
        "approved_by_doc": dict(Counter(row["source_doc_ids"][0] for row in approved_rows)),
        "rejected_ids": reject_ids,
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(approve_ids)} approved ids -> {args.approve_output}")
    print(f"Wrote {len(reject_ids)} rejected ids -> {args.reject_output}")
    print(f"Wrote review selection report -> {args.report_output}")


if __name__ == "__main__":
    main()

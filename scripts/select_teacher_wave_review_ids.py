from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json


TRAIN_APPROVAL_TARGETS = {
    "clarification": 10,
    "uncertainty_escalation": 10,
    "step_by_step": 18,
    "troubleshooting": 18,
    "faq_direct_answer": 24,
}
EVAL_APPROVAL_TARGETS = {
    "clarification": 4,
    "uncertainty_escalation": 4,
    "step_by_step": 4,
    "troubleshooting": 4,
    "faq_direct_answer": 6,
}


def round_robin_ids(
    grouped: dict[str, list[dict]],
    target: int,
    selected: list[str],
) -> None:
    for doc_id, rows in grouped.items():
        rows.sort(
            key=lambda row: (
                -int(row.get("quality_score", 0)),
                row["output_id"],
            )
        )
        grouped[doc_id] = rows
    ordered_docs = sorted(grouped)
    used: set[str] = set()
    while len(selected) < target:
        progressed = False
        for doc_id in ordered_docs:
            bucket = grouped.get(doc_id)
            if not bucket:
                continue
            while bucket and bucket[0]["output_id"] in used:
                bucket.pop(0)
            if not bucket:
                continue
            row = bucket.pop(0)
            used.add(row["output_id"])
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(Path(args.input))

    train_grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    eval_grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    low_confidence: list[dict] = []

    for row in rows:
        if row.get("review_status") != "teacher_generated":
            continue
        split = row["target_split"]
        task_type = row["task_type"]
        doc_id = row["source_doc_ids"][0]
        if int(row.get("quality_score", 0)) < 42:
            low_confidence.append(row)
            continue
        if split == "train":
            train_grouped[task_type][doc_id].append(row)
        else:
            eval_grouped[task_type][doc_id].append(row)

    approve_ids: list[str] = []
    for task_type, target in TRAIN_APPROVAL_TARGETS.items():
        selected_ids: list[str] = []
        round_robin_ids(train_grouped[task_type], target, selected_ids)
        approve_ids.extend(selected_ids)
    for task_type, target in EVAL_APPROVAL_TARGETS.items():
        selected_ids = []
        round_robin_ids(eval_grouped[task_type], target, selected_ids)
        approve_ids.extend(selected_ids)

    approve_set = set(approve_ids)
    reject_ids = [
        row["output_id"]
        for row in sorted(low_confidence, key=lambda row: (int(row.get("quality_score", 0)), row["output_id"]))[:12]
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

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json


def parse_args() -> Any:
    parser = make_parser(
        "Build a deterministic Codex GPT-5.4 Wave1 batch from the approved reviewed Wave1 outputs."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--job-ids-output", required=True)
    parser.add_argument("--approve-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--teacher-run-id", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(Path(args.input))
    approved_rows = [
        row
        for row in rows
        if row.get("review_status") == "human_reviewed" and row.get("approved_by")
    ]
    approved_rows.sort(
        key=lambda row: (
            row["target_split"],
            row["task_type"],
            row["source_doc_ids"][0],
            row["job_id"],
        )
    )
    if not approved_rows:
        raise SystemExit("No human_reviewed rows found in input")

    job_ids = [row["job_id"] for row in approved_rows]
    approve_ids = [f"{args.teacher_run_id}::{row['job_id']}" for row in approved_rows]

    job_ids_path = Path(args.job_ids_output)
    job_ids_path.parent.mkdir(parents=True, exist_ok=True)
    job_ids_path.write_text("\n".join(job_ids) + "\n", encoding="utf-8")

    approve_path = Path(args.approve_output)
    approve_path.parent.mkdir(parents=True, exist_ok=True)
    approve_path.write_text("\n".join(approve_ids) + "\n", encoding="utf-8")

    report = {
        "batch_name": "wave1_codex_gpt54_real_batch_v1",
        "source_reviewed_outputs": args.input.replace("\\", "/"),
        "teacher_run_id": args.teacher_run_id,
        "selected_jobs": len(job_ids),
        "selected_outputs": len(approve_ids),
        "selected_by_split": dict(Counter(row["target_split"] for row in approved_rows)),
        "selected_by_task_type": dict(Counter(row["task_type"] for row in approved_rows)),
        "selected_by_doc": dict(Counter(row["source_doc_ids"][0] for row in approved_rows)),
        "job_ids_path": args.job_ids_output.replace("\\", "/"),
        "approve_ids_path": args.approve_output.replace("\\", "/"),
    }
    write_json(Path(args.report_output), report)

    print(f"Wrote {len(job_ids)} job ids -> {args.job_ids_output}")
    print(f"Wrote {len(approve_ids)} approve ids -> {args.approve_output}")
    print(f"Wrote report -> {args.report_output}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json


TARGETS = {
    ("train", "faq_direct_answer"): 1,
    ("train", "troubleshooting"): 1,
    ("train", "step_by_step"): 1,
    ("train", "clarification"): 1,
    ("train", "uncertainty_escalation"): 1,
    ("eval", "faq_direct_answer"): 1,
    ("eval", "clarification"): 1,
    ("eval", "step_by_step"): 1,
}


def parse_args() -> Any:
    parser = make_parser("Build a small deterministic Wave1 subset for GPT-5.4 teacher replay/import runs.")
    parser.add_argument("--jobs", default="data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl")
    parser.add_argument("--output", default="data/derived/teacher_jobs/JAWS/DE/wave1_gpt54_subset_job_ids.txt")
    parser.add_argument("--report", default="data/derived/teacher_jobs/JAWS/DE/wave1_gpt54_subset_report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(Path(args.jobs))

    selected: list[dict] = []
    seen_chunk_ids: set[str] = set()
    doc_counts: Counter[str] = Counter()

    for split, task_type in TARGETS:
        candidates = [
            row for row in rows
            if row["target_split"] == split
            and row["task_type"] == task_type
            and not set(row["source_chunk_ids"]) & seen_chunk_ids
        ]
        candidates.sort(
            key=lambda row: (
                doc_counts[row["source_doc_ids"][0]],
                row["source_doc_ids"][0],
                -int(row.get("quality_score") or 0),
                row["job_id"],
            )
        )
        if not candidates:
            raise SystemExit(f"No candidate found for {split}/{task_type}")
        row = candidates[0]
        selected.append(row)
        doc_counts[row["source_doc_ids"][0]] += 1
        seen_chunk_ids.update(row["source_chunk_ids"])

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(row["job_id"] for row in selected) + "\n", encoding="utf-8")

    report = {
        "subset_name": "wave1_gpt54_subset",
        "jobs_path": str(Path(args.jobs)).replace("\\", "/"),
        "selected_jobs": len(selected),
        "selected_by_split": dict(Counter(row["target_split"] for row in selected)),
        "selected_by_task_type": dict(Counter(row["task_type"] for row in selected)),
        "selected_by_doc": dict(Counter(row["source_doc_ids"][0] for row in selected)),
        "job_ids": [row["job_id"] for row in selected],
    }
    write_json(Path(args.report), report)
    print(f"Wrote {len(selected)} job IDs -> {args.output}")
    print(f"Wrote subset report -> {args.report}")


if __name__ == "__main__":
    main()

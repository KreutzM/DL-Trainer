from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json


TASKS = [
    "faq_direct_answer",
    "troubleshooting",
    "step_by_step",
    "clarification",
    "uncertainty_escalation",
]

SPLITS = ["train", "eval"]


def parse_args() -> Any:
    parser = make_parser("Build a balanced JAWS-DE quality validation wave from existing teacher jobs.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--job-ids-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--per-task-train", type=int, default=2)
    parser.add_argument("--per-task-eval", type=int, default=2)
    return parser.parse_args()


def chunk_rank(job: dict[str, Any]) -> int:
    task_type = job["task_type"]
    chunk_type = str(job.get("chunk_type") or "")
    if task_type == "step_by_step":
        return 0 if chunk_type == "procedure" else 3
    if task_type == "troubleshooting":
        return {"warning": 0, "procedure": 1}.get(chunk_type, 4)
    if task_type == "clarification":
        return {"reference": 0, "warning": 1, "procedure": 2}.get(chunk_type, 5)
    if task_type == "uncertainty_escalation":
        return 0 if chunk_type == "warning" else 4
    if task_type == "faq_direct_answer":
        return 0 if chunk_type == "concept" else 2
    return 9


def base_filter(job: dict[str, Any]) -> bool:
    task_type = job["task_type"]
    chunk_type = str(job.get("chunk_type") or "")
    quality = int(job.get("quality_score") or 0)
    if task_type == "step_by_step":
        return chunk_type == "procedure" and quality >= 80
    if task_type == "troubleshooting":
        return chunk_type in {"warning", "procedure"} and quality >= 70
    if task_type == "clarification":
        return chunk_type in {"reference", "warning", "procedure"} and quality >= 52
    if task_type == "uncertainty_escalation":
        return chunk_type == "warning" and quality >= 72
    if task_type == "faq_direct_answer":
        return quality >= 71
    return True


def relaxed_filter(job: dict[str, Any]) -> bool:
    task_type = job["task_type"]
    quality = int(job.get("quality_score") or 0)
    if task_type == "clarification":
        return quality >= 42
    if task_type == "troubleshooting":
        return quality >= 56
    if task_type == "uncertainty_escalation":
        return quality >= 54
    return quality >= 60


def pick_jobs(pool: list[dict[str, Any]], count: int, global_doc_counter: Counter[str]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    local_doc_counter: Counter[str] = Counter()
    candidates = list(pool)
    while candidates and len(selected) < count:
        candidates.sort(
            key=lambda job: (
                global_doc_counter[job["source_doc_ids"][0]],
                local_doc_counter[job["source_doc_ids"][0]],
                chunk_rank(job),
                -int(job.get("quality_score") or 0),
                job["job_id"],
            )
        )
        job = candidates.pop(0)
        selected.append(job)
        doc_id = job["source_doc_ids"][0]
        global_doc_counter[doc_id] += 1
        local_doc_counter[doc_id] += 1
    return selected


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_task = Counter(row["task_type"] for row in rows)
    by_split = Counter(row["target_split"] for row in rows)
    by_doc = Counter(row["source_doc_ids"][0] for row in rows)
    by_task_split: dict[str, dict[str, int]] = defaultdict(dict)
    for row in rows:
        by_task_split[row["task_type"]][row["target_split"]] = (
            by_task_split[row["task_type"]].get(row["target_split"], 0) + 1
        )
    return {
        "count": len(rows),
        "by_task": dict(sorted(by_task.items())),
        "by_split": dict(sorted(by_split.items())),
        "by_doc": dict(sorted(by_doc.items())),
        "by_task_split": {task: dict(sorted(counts.items())) for task, counts in sorted(by_task_split.items())},
    }


def main() -> None:
    args = parse_args()
    jobs = read_jsonl(Path(args.jobs))
    global_doc_counter: Counter[str] = Counter()
    selected: list[dict[str, Any]] = []
    selection_notes: list[dict[str, Any]] = []

    quotas = {
        ("train", task): args.per_task_train for task in TASKS
    }
    quotas.update({("eval", task): args.per_task_eval for task in TASKS})

    for split in SPLITS:
        for task in TASKS:
            quota = quotas[(split, task)]
            pool = [
                job
                for job in jobs
                if job["target_split"] == split and job["task_type"] == task and base_filter(job)
            ]
            if len(pool) < quota:
                pool.extend(
                    job
                    for job in jobs
                    if job["target_split"] == split
                    and job["task_type"] == task
                    and relaxed_filter(job)
                    and job not in pool
                )
            picked = pick_jobs(pool, quota, global_doc_counter)
            if len(picked) < quota:
                raise SystemExit(f"Not enough candidate jobs for {split}/{task}: need {quota}, found {len(picked)}")
            selected.extend(picked)
            selection_notes.append(
                {
                    "task_type": task,
                    "target_split": split,
                    "selected_job_ids": [job["job_id"] for job in picked],
                }
            )

    selected.sort(key=lambda row: (row["target_split"], row["task_type"], row["job_id"]))
    output_path = Path(args.job_ids_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(row["job_id"] for row in selected) + "\n", encoding="utf-8")

    report = {
        "source_jobs_path": str(Path(args.jobs)).replace("\\", "/"),
        "selection_version": "jaws_de_quality_validation_wave_v1",
        "rules": {
            "per_task_train": args.per_task_train,
            "per_task_eval": args.per_task_eval,
            "task_types": TASKS,
            "heuristics": {
                "faq_direct_answer": "quality_score>=71",
                "troubleshooting": "prefer warning/procedure and quality_score>=70; relax to quality_score>=56",
                "step_by_step": "procedure and quality_score>=80",
                "clarification": "prefer reference/warning/procedure and quality_score>=52; relax to quality_score>=42",
                "uncertainty_escalation": "prefer warning and quality_score>=72; relax to quality_score>=54",
            },
        },
        "summary": summarize(selected),
        "selection_notes": selection_notes,
        "selected_jobs": [
            {
                "job_id": row["job_id"],
                "target_split": row["target_split"],
                "task_type": row["task_type"],
                "source_doc_id": row["source_doc_ids"][0],
                "source_chunk_id": row["source_chunk_ids"][0],
                "quality_score": row.get("quality_score"),
                "chunk_type": row.get("chunk_type"),
                "section_path_text": row.get("section_path_text"),
            }
            for row in selected
        ],
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(selected)} job IDs -> {output_path}")
    print(f"Wrote selection report -> {args.report_output}")


if __name__ == "__main__":
    main()

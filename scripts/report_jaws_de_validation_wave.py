from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json


def parse_args() -> Any:
    parser = make_parser("Summarize a JAWS-DE Codex CLI validation wave.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--user-simulations", required=True)
    parser.add_argument("--raw-output", required=True)
    parser.add_argument("--judge-output", required=True)
    parser.add_argument("--reviewed-output", required=True)
    parser.add_argument("--train-output", required=True)
    parser.add_argument("--eval-output", required=True)
    parser.add_argument("--report-output", required=True)
    return parser.parse_args()


def assistant_text(output: dict[str, Any]) -> str:
    candidate = output["candidate"]
    if output["record_type"] == "sft_sample":
        for message in reversed(candidate.get("messages", [])):
            if message.get("role") == "assistant":
                return str(message.get("content") or "")
        return ""
    return str(candidate.get("reference_answer") or "")


def main() -> None:
    args = parse_args()
    jobs = {row["job_id"]: row for row in read_jsonl(Path(args.jobs))}
    sims = {row["job_id"]: row for row in read_jsonl(Path(args.user_simulations))}
    judges = {row["job_id"]: row for row in read_jsonl(Path(args.judge_output))}
    reviewed = {row["job_id"]: row for row in read_jsonl(Path(args.reviewed_output))}
    train_rows = read_jsonl(Path(args.train_output))
    eval_rows = read_jsonl(Path(args.eval_output))

    selected_ids = sorted(judges)
    selected_jobs = [jobs[job_id] for job_id in selected_ids]
    approvals = [row for row in judges.values() if row["decision"] == "approve"]
    rejects = [row for row in judges.values() if row["decision"] == "reject"]

    by_task = Counter(job["task_type"] for job in selected_jobs)
    by_doc = Counter(job["source_doc_ids"][0] for job in selected_jobs)
    by_split = Counter(job["target_split"] for job in selected_jobs)
    by_task_decision: dict[str, dict[str, int]] = defaultdict(lambda: {"approve": 0, "reject": 0})
    by_doc_decision: dict[str, dict[str, int]] = defaultdict(lambda: {"approve": 0, "reject": 0})
    fail_reasons = Counter()
    for judge in judges.values():
        task = jobs[judge["job_id"]]["task_type"]
        doc = jobs[judge["job_id"]]["source_doc_ids"][0]
        by_task_decision[task][judge["decision"]] += 1
        by_doc_decision[doc][judge["decision"]] += 1
        for reason in judge.get("blocking_reasons", []):
            fail_reasons[reason] += 1

    best_approved = max(approvals, key=lambda row: (row["quality_score"], row["job_id"])) if approvals else None
    representative_reject = max(
        rejects, key=lambda row: (len(row.get("blocking_reasons", [])), row["quality_score"], row["job_id"])
    ) if rejects else None

    report = {
        "wave_size": len(selected_ids),
        "selection_summary": {
            "by_task": dict(sorted(by_task.items())),
            "by_doc": dict(sorted(by_doc.items())),
            "by_split": dict(sorted(by_split.items())),
        },
        "judge_summary": {
            "approvals": len(approvals),
            "rejects": len(rejects),
            "by_task_decision": {task: counts for task, counts in sorted(by_task_decision.items())},
            "by_doc_decision": {doc: counts for doc, counts in sorted(by_doc_decision.items())},
            "top_blocking_reasons": dict(fail_reasons.most_common(10)),
        },
        "promotion_summary": {
            "gold_train_rows": len(train_rows),
            "gold_eval_rows": len(eval_rows),
        },
        "examples": {
            "strong_user_request": None,
            "strong_support_answer": None,
            "rejected_case": None,
            "gold_train_example": train_rows[0] if train_rows else None,
            "gold_eval_example": eval_rows[0] if eval_rows else None,
        },
    }

    if best_approved:
        report["examples"]["strong_user_request"] = {
            "job_id": best_approved["job_id"],
            "task_type": jobs[best_approved["job_id"]]["task_type"],
            "source_doc_id": jobs[best_approved["job_id"]]["source_doc_ids"][0],
            "request_text": sims[best_approved["job_id"]]["request_text"],
            "judge_quality_score": best_approved["quality_score"],
        }
        report["examples"]["strong_support_answer"] = {
            "job_id": best_approved["job_id"],
            "task_type": jobs[best_approved["job_id"]]["task_type"],
            "answer_text": assistant_text(reviewed[best_approved["job_id"]]),
            "judge_summary": best_approved["summary"],
        }
    if representative_reject:
        report["examples"]["rejected_case"] = {
            "job_id": representative_reject["job_id"],
            "task_type": jobs[representative_reject["job_id"]]["task_type"],
            "request_text": sims[representative_reject["job_id"]]["request_text"],
            "answer_text": assistant_text(reviewed[representative_reject["job_id"]]),
            "blocking_reasons": representative_reject["blocking_reasons"],
            "judge_summary": representative_reject["summary"],
        }

    write_json(Path(args.report_output), report)
    print(f"Wrote validation report -> {args.report_output}")


if __name__ == "__main__":
    main()

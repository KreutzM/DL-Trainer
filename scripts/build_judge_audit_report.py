from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import compare_support_mvp_benchmarks as benchmark_compare
from common import find_repo_root, make_parser, read_jsonl, write_json


def normalized_path(path: str | Path | None) -> str | None:
    if path is None:
        return None
    return str(path).replace("\\", "/")


def index_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["job_id"]): row for row in rows}


def extract_answer_text(row: dict[str, Any]) -> str | None:
    candidate = row.get("candidate") or {}
    reference_answer = candidate.get("reference_answer")
    if isinstance(reference_answer, str) and reference_answer.strip():
        return reference_answer.strip()
    messages = candidate.get("messages")
    if isinstance(messages, list):
        assistant_messages = [
            str(message.get("content") or "").strip()
            for message in messages
            if isinstance(message, dict) and message.get("role") == "assistant"
        ]
        assistant_messages = [message for message in assistant_messages if message]
        if assistant_messages:
            return assistant_messages[-1]
    return None


def selection_tags(
    *,
    task_type: str,
    reference_decision: str,
    candidate_decision: str,
    quality_score_delta: int | None,
    focus_task_types: set[str],
    score_delta_threshold: int,
) -> list[str]:
    tags: list[str] = []
    if task_type in focus_task_types:
        tags.append(f"focus_task_type:{task_type}")
    if reference_decision != candidate_decision:
        tags.append("decision_disagreement")
    if quality_score_delta is not None and abs(quality_score_delta) >= score_delta_threshold:
        tags.append(f"high_score_delta>={score_delta_threshold}")
    return tags


def build_judge_audit_summary(
    repo_root: Path,
    reference_report_path: Path,
    candidate_report_path: Path,
    *,
    focus_task_types: list[str],
    score_delta_threshold: int,
) -> dict[str, Any]:
    reference_summary = benchmark_compare.build_run_summary(repo_root, reference_report_path)
    candidate_summary = benchmark_compare.build_run_summary(repo_root, candidate_report_path)
    benchmark_name = benchmark_compare.validate_benchmark_pair(reference_summary, candidate_summary)

    reference_reviewed_rows = index_rows(
        read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, reference_summary["paths"]["reviewed_outputs"]))
    )
    candidate_reviewed_rows = index_rows(
        read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, candidate_summary["paths"]["reviewed_outputs"]))
    )
    reference_judge_rows = index_rows(
        read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, reference_summary["paths"]["judge_results"]))
    )
    candidate_judge_rows = index_rows(
        read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, candidate_summary["paths"]["judge_results"]))
    )

    focus_task_type_set = set(focus_task_types)
    common_job_ids = sorted(
        set(reference_reviewed_rows)
        & set(candidate_reviewed_rows)
        & set(reference_judge_rows)
        & set(candidate_judge_rows)
    )

    cases: list[dict[str, Any]] = []
    for job_id in common_job_ids:
        reference_reviewed = reference_reviewed_rows[job_id]
        candidate_reviewed = candidate_reviewed_rows[job_id]
        reference_judge = reference_judge_rows[job_id]
        candidate_judge = candidate_judge_rows[job_id]

        task_type = str(reference_judge.get("task_type") or candidate_judge.get("task_type") or "unknown")
        reference_decision = str(reference_judge.get("decision") or "missing")
        candidate_decision = str(candidate_judge.get("decision") or "missing")
        reference_quality_score = reference_judge.get("quality_score")
        candidate_quality_score = candidate_judge.get("quality_score")
        quality_score_delta: int | None = None
        if reference_quality_score is not None and candidate_quality_score is not None:
            quality_score_delta = int(candidate_quality_score) - int(reference_quality_score)

        tags = selection_tags(
            task_type=task_type,
            reference_decision=reference_decision,
            candidate_decision=candidate_decision,
            quality_score_delta=quality_score_delta,
            focus_task_types=focus_task_type_set,
            score_delta_threshold=score_delta_threshold,
        )
        if not tags:
            continue

        cases.append(
            {
                "job_id": job_id,
                "target_split": reference_judge.get("target_split") or candidate_judge.get("target_split"),
                "task_type": task_type,
                "selection_tags": tags,
                "quality_score_delta": quality_score_delta,
                "reference": {
                    "decision": reference_decision,
                    "quality_score": reference_quality_score,
                    "review_status": reference_reviewed.get("review_status"),
                    "summary": reference_judge.get("summary"),
                    "blocking_reasons": reference_judge.get("blocking_reasons") or [],
                    "answer_text": extract_answer_text(reference_reviewed),
                    "source_spans": (
                        reference_reviewed.get("provenance", {}).get("source_records", [{}])[0].get("source_spans", [])
                    ),
                },
                "candidate": {
                    "decision": candidate_decision,
                    "quality_score": candidate_quality_score,
                    "review_status": candidate_reviewed.get("review_status"),
                    "summary": candidate_judge.get("summary"),
                    "blocking_reasons": candidate_judge.get("blocking_reasons") or [],
                    "answer_text": extract_answer_text(candidate_reviewed),
                    "source_spans": (
                        candidate_reviewed.get("provenance", {}).get("source_records", [{}])[0].get("source_spans", [])
                    ),
                },
            }
        )

    tag_counts = Counter(tag for case in cases for tag in case["selection_tags"])
    task_type_counts = Counter(case["task_type"] for case in cases)
    decision_pair_counts = Counter(
        f"{case['reference']['decision']}->{case['candidate']['decision']}" for case in cases
    )

    return {
        "benchmark_name": benchmark_name,
        "reference_run": reference_summary["run_name"],
        "candidate_run": candidate_summary["run_name"],
        "reference_report": normalized_path(reference_report_path),
        "candidate_report": normalized_path(candidate_report_path),
        "focus_task_types": focus_task_types,
        "score_delta_threshold": score_delta_threshold,
        "selected_case_count": len(cases),
        "selection_tag_counts": dict(sorted(tag_counts.items())),
        "task_type_counts": dict(sorted(task_type_counts.items())),
        "decision_pair_counts": dict(sorted(decision_pair_counts.items())),
        "cases": cases,
    }


def parse_args() -> Any:
    parser = make_parser("Build a focused Judge-Audit report from existing benchmark artifacts.")
    parser.add_argument("--reference-run")
    parser.add_argument("--reference-report")
    parser.add_argument("--candidate-run")
    parser.add_argument("--candidate-report")
    parser.add_argument(
        "--focus-task-type",
        action="append",
        dest="focus_task_types",
        default=["step_by_step", "faq_direct_answer"],
    )
    parser.add_argument("--score-delta-threshold", type=int, default=20)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    reference_report = benchmark_compare.resolve_report_path(
        repo_root,
        run_name=args.reference_run,
        report_path=args.reference_report,
    )
    candidate_report = benchmark_compare.resolve_report_path(
        repo_root,
        run_name=args.candidate_run,
        report_path=args.candidate_report,
    )
    summary = build_judge_audit_summary(
        repo_root,
        reference_report,
        candidate_report,
        focus_task_types=args.focus_task_types,
        score_delta_threshold=args.score_delta_threshold,
    )
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    write_json(output_path, summary)
    print(f"Wrote judge audit report -> {output_path}")


if __name__ == "__main__":
    main()

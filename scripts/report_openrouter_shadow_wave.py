from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

import compare_support_mvp_benchmarks as benchmark_compare
from build_judge_audit_report import extract_answer_text, normalized_path
from common import find_repo_root, make_parser, read_json, read_jsonl, write_json


def parse_args() -> Any:
    parser = make_parser("Build a structured repo-internal report for an OpenRouter shadow wave.")
    parser.add_argument("--run-name")
    parser.add_argument("--report-path")
    parser.add_argument("--jobs")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def resolve_jobs_path(repo_root: Path, pipeline_report: dict[str, Any], explicit_jobs: str | None) -> Path:
    if explicit_jobs:
        path = Path(explicit_jobs)
    else:
        path = Path(str(pipeline_report["jobs_path"]))
    return path if path.is_absolute() else repo_root / path


def load_rows(repo_root: Path, run_summary: dict[str, Any], pipeline_report: dict[str, Any], explicit_jobs: str | None) -> dict[str, dict[str, Any]]:
    jobs = {
        str(row["job_id"]): row
        for row in read_jsonl(resolve_jobs_path(repo_root, pipeline_report, explicit_jobs))
    }
    user_simulations = {
        str(row["job_id"]): row
        for row in read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, run_summary["paths"]["user_simulations"]))
    }
    teacher_outputs = {
        str(row["job_id"]): row
        for row in read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, run_summary["paths"]["teacher_outputs"]))
    }
    raw_responses = {
        str(row["job_id"]): row
        for row in read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, run_summary["paths"]["raw_responses"]))
    }
    reviewed_outputs = {
        str(row["job_id"]): row
        for row in read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, run_summary["paths"]["reviewed_outputs"]))
    }
    judge_results = {
        str(row["job_id"]): row
        for row in read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, run_summary["paths"]["judge_results"]))
    }
    return {
        "jobs": jobs,
        "user_simulations": user_simulations,
        "raw_responses": raw_responses,
        "teacher_outputs": teacher_outputs,
        "reviewed_outputs": reviewed_outputs,
        "judge_results": judge_results,
    }


def score_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = sorted(int(row["quality_score"]) for row in rows if row.get("quality_score") is not None)
    if not scores:
        return {"count": 0}
    return {
        "count": len(scores),
        "min": scores[0],
        "median": median(scores),
        "max": scores[-1],
        "score_bands": {
            "<60": sum(score < 60 for score in scores),
            "60-69": sum(60 <= score <= 69 for score in scores),
            "70-79": sum(70 <= score <= 79 for score in scores),
            "80-89": sum(80 <= score <= 89 for score in scores),
            "90+": sum(score >= 90 for score in scores),
        },
    }


def attempt_histogram(rows: dict[str, dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows.values():
        attempt_count = int((row.get("usage") or {}).get("attempt_count") or 1)
        counter[str(attempt_count)] += 1
    return dict(sorted(counter.items(), key=lambda item: int(item[0])))


def response_usage_summary(rows: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    reported_cost = 0.0
    coverage = 0
    for row in rows.values():
        response_path = (row.get("openrouter") or {}).get("response_path")
        if not response_path:
            continue
        response = read_json(Path(response_path))
        usage = response.get("usage") or {}
        if not usage:
            continue
        coverage += 1
        prompt_tokens += int(usage.get("prompt_tokens") or 0)
        completion_tokens += int(usage.get("completion_tokens") or 0)
        total_tokens += int(usage.get("total_tokens") or 0)
        reported_cost += float(usage.get("cost") or 0.0)
    if coverage == 0:
        return None
    return {
        "rows_with_provider_usage": coverage,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "reported_cost_usd_estimate": round(reported_cost, 4),
        "note": "Approximate sum of provider-reported usage fields from saved OpenRouter responses; not a billing-grade value.",
    }


def stage_health(pipeline_report: dict[str, Any]) -> dict[str, Any]:
    health: dict[str, Any] = {}
    for stage_name, stage_payload in pipeline_report["stages"].items():
        runtime = stage_payload.get("runtime") or {}
        health[stage_name] = {
            "selected_jobs": stage_payload.get("selected_jobs"),
            "completed_jobs": stage_payload.get("completed_jobs"),
            "failed_jobs": stage_payload.get("failed_jobs"),
            "total_retry_attempts": runtime.get("total_retry_attempts"),
            "executed_batches": runtime.get("executed_batches"),
            "completed_batches": runtime.get("completed_batches"),
            "avg_elapsed_ms_per_processed_job": runtime.get("avg_elapsed_ms_per_processed_job"),
        }
    return health


def per_task_decisions(judge_rows: dict[str, dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"approve": 0, "reject": 0})
    for row in judge_rows.values():
        counts[str(row["task_type"])][str(row["decision"])] += 1
    return {task: counts[task] for task in sorted(counts)}


def qualitative_focus(
    rows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    jobs = rows["jobs"]
    sims = rows["user_simulations"]
    reviewed = rows["reviewed_outputs"]
    judges = rows["judge_results"]
    focus_cases: list[dict[str, Any]] = []
    for job_id, judge_row in judges.items():
        score = int(judge_row.get("quality_score") or 0)
        tags: list[str] = []
        if judge_row.get("task_type") == "step_by_step":
            tags.append("priority_step_by_step")
        if judge_row.get("decision") == "reject":
            tags.append("reject")
        if score <= 85:
            tags.append("borderline_score")
        if judge_row.get("blocking_reasons"):
            tags.append("blocking_reasons_present")
        if not tags:
            continue
        answer_row = reviewed.get(job_id)
        focus_cases.append(
            {
                "job_id": job_id,
                "task_type": judge_row.get("task_type"),
                "target_split": jobs[job_id].get("target_split"),
                "decision": judge_row.get("decision"),
                "quality_score": score,
                "selection_tags": tags,
                "judge_summary": judge_row.get("summary"),
                "blocking_reasons": judge_row.get("blocking_reasons") or [],
                "request_text": sims.get(job_id, {}).get("request_text"),
                "answer_text": extract_answer_text(answer_row) if answer_row else "",
                "source_spans": [
                    str(span)
                    for record in (judge_row.get("provenance", {}).get("source_records") or [])[:1]
                    for span in (record.get("source_spans") or [])
                ],
            }
        )
    focus_cases.sort(
        key=lambda case: (
            "reject" not in case["selection_tags"],
            "priority_step_by_step" not in case["selection_tags"],
            case["quality_score"],
            case["job_id"],
        )
    )
    return focus_cases[:12]


def judge_role_statement(pipeline_report: dict[str, Any]) -> dict[str, Any]:
    judge_stage = pipeline_report["stages"]["judge"]
    return {
        "intended_role": "secondary_audit_judge",
        "shadow_only": True,
        "statement": (
            "This wave treats the GPT-5.4 OpenRouter judge as a secondary audit signal only. "
            "The primary observation target is OpenRouter user_simulation plus answer quality; judge outputs are "
            "reported for calibration and triage, not for promotion or rollout gating."
        ),
        "judge_profile": judge_stage.get("llm_profile"),
    }


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    report_path = benchmark_compare.resolve_report_path(
        repo_root,
        run_name=args.run_name,
        report_path=args.report_path,
    )
    pipeline_report = read_json(report_path)
    run_summary = benchmark_compare.build_run_summary(repo_root, report_path)
    rows = load_rows(repo_root, run_summary, pipeline_report, args.jobs)

    judge_rows = rows["judge_results"]
    jobs = rows["jobs"]

    report = {
        "run_name": run_summary["run_name"],
        "report_path": normalized_path(report_path),
        "llm_profile_set": run_summary.get("llm_profile_set"),
        "selection_manifest": pipeline_report.get("selection_manifest"),
        "judge_role": judge_role_statement(pipeline_report),
        "processing": {
            "jobs_total": len(judge_rows),
            "task_type_distribution": dict(sorted(Counter(jobs[job_id]["task_type"] for job_id in judge_rows).items())),
            "split_distribution": dict(sorted(Counter(jobs[job_id]["target_split"] for job_id in judge_rows).items())),
        },
        "approval_distribution": dict(sorted(Counter(str(row["decision"]) for row in judge_rows.values()).items())),
        "score_distribution": score_summary(list(judge_rows.values())),
        "task_type_decisions": per_task_decisions(judge_rows),
        "stage_health": stage_health(pipeline_report),
        "attempt_histograms": {
            "user_simulation": attempt_histogram(rows["user_simulations"]),
            "answer": attempt_histogram(rows["raw_responses"]),
            "judge": attempt_histogram(rows["judge_results"]),
        },
        "provider_usage": {
            "user_simulation": response_usage_summary(rows["user_simulations"]),
            "answer": response_usage_summary(rows["raw_responses"]),
            "judge": response_usage_summary(rows["judge_results"]),
        },
        "qualitative_focus_cases": qualitative_focus(rows),
    }
    write_json(Path(args.output), report)
    print(f"Wrote shadow wave report -> {args.output}")


if __name__ == "__main__":
    main()

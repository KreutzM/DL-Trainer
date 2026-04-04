from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from common import find_repo_root, make_parser, read_json, read_jsonl, write_json

PIPELINE_REPORT_DIR = Path("data/derived/teacher_reviews/JAWS/DE")
PIPELINE_STAGE_TO_PROFILE_STAGE = {
    "user_simulation": "user_simulation",
    "answering": "answer",
    "judge": "judge",
}
ARTIFACT_SCHEMA_PATHS = {
    "teacher_outputs": "schemas/teacher_output.schema.json",
    "reviewed_outputs": "schemas/teacher_output.schema.json",
    "judge_results": "schemas/teacher_judge_result.schema.json",
}


def normalized_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def resolve_report_path(repo_root: Path, *, run_name: str | None, report_path: str | None) -> Path:
    if report_path:
        path = Path(report_path)
        return path if path.is_absolute() else repo_root / path
    if not run_name:
        raise SystemExit("Either a run name or a report path is required")
    return repo_root / PIPELINE_REPORT_DIR / f"{run_name}_pipeline_report.json"


def resolve_artifact_path(repo_root: Path, path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else repo_root / path


def count_values(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter = Counter(str(row.get(key) or "missing") for row in rows)
    return dict(sorted(counter.items()))


def average_int(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [int(row[key]) for row in rows if row.get(key) is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def schema_validation_summary(rows: list[dict[str, Any]], schema_path: Path) -> dict[str, Any]:
    validator = Draft202012Validator(read_json(schema_path))
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        row_errors = list(validator.iter_errors(row))
        for error in row_errors[:3]:
            errors.append(f"Row {index}: {error.message}")
    return {
        "ok": not errors,
        "error_count": len(errors),
        "sample_errors": errors[:3],
    }


def source_record_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    missing_indices = [
        index
        for index, row in enumerate(rows, start=1)
        if not row.get("provenance", {}).get("source_records")
    ]
    return {
        "ok": not missing_indices,
        "missing_rows": missing_indices[:10],
        "missing_count": len(missing_indices),
    }


def artifact_summary(repo_root: Path, artifact_name: str, path_value: str) -> dict[str, Any]:
    path = resolve_artifact_path(repo_root, path_value)
    rows = read_jsonl(path)
    summary: dict[str, Any] = {
        "path": normalized_path(path),
        "rows": len(rows),
        "schema": schema_validation_summary(rows, repo_root / ARTIFACT_SCHEMA_PATHS[artifact_name]),
        "source_records": source_record_summary(rows),
    }
    if artifact_name in {"teacher_outputs", "reviewed_outputs"}:
        summary["review_status_counts"] = count_values(rows, "review_status")
        summary["record_type_counts"] = count_values(rows, "record_type")
    if artifact_name == "judge_results":
        summary["decision_counts"] = count_values(rows, "decision")
        summary["average_quality_score"] = average_int(rows, "quality_score")
    return summary


def stage_summary(
    stage_name: str,
    stage_report: dict[str, Any],
    stage_defaults: dict[str, Any] | None,
    stage_profile: dict[str, Any] | None,
) -> dict[str, Any]:
    runtime = stage_report.get("runtime", {})
    provider = (
        stage_report.get("simulator_provider")
        or stage_report.get("teacher_provider")
        or stage_report.get("reviewer_provider")
    )
    model = (
        stage_report.get("simulator_model")
        or stage_report.get("teacher_model")
        or stage_report.get("reviewer_model")
    )
    failed_jobs = stage_report.get("failed_jobs", [])
    return {
        "stage": stage_name,
        "provider": provider,
        "model": model,
        "generation_mode": stage_report.get("generation_mode"),
        "selected_jobs": stage_report.get("selected_jobs"),
        "completed_jobs": stage_report.get("completed_jobs"),
        "failed_jobs": len(failed_jobs) if isinstance(failed_jobs, list) else failed_jobs,
        "executed_batches": runtime.get("executed_batches"),
        "completed_batches": runtime.get("completed_batches"),
        "total_elapsed_ms": runtime.get("total_elapsed_ms"),
        "total_retry_attempts": runtime.get("total_retry_attempts"),
        "profile": stage_profile,
        "configured_defaults": stage_defaults,
    }


def approval_metrics(reviewed_summary: dict[str, Any]) -> dict[str, Any]:
    review_counts = reviewed_summary.get("review_status_counts", {})
    rows = int(reviewed_summary.get("rows") or 0)
    approved = int(review_counts.get("codex_reviewed", 0))
    rejected = int(review_counts.get("rejected", 0))
    return {
        "approved_jobs": approved,
        "rejected_jobs": rejected,
        "approval_rate": round(approved / rows, 4) if rows else None,
    }


def delta_int(left: int | None, right: int | None) -> int | None:
    if left is None or right is None:
        return None
    return right - left


def delta_float(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return round(right - left, 4)


def build_run_summary(repo_root: Path, report_path: Path) -> dict[str, Any]:
    pipeline_report = read_json(report_path)
    stage_profiles = pipeline_report.get("llm_profiles", {})
    stage_defaults = pipeline_report.get("defaults", {})
    stages = {
        stage_name: stage_summary(
            stage_name,
            stage_report,
            stage_defaults.get(stage_name),
            stage_profiles.get(PIPELINE_STAGE_TO_PROFILE_STAGE[stage_name]),
        )
        for stage_name, stage_report in pipeline_report.get("stages", {}).items()
    }
    artifacts = {
        artifact_name: artifact_summary(repo_root, artifact_name, pipeline_report["paths"][artifact_name])
        for artifact_name in ("teacher_outputs", "reviewed_outputs", "judge_results")
    }
    return {
        "run_name": pipeline_report["run_name"],
        "report_path": normalized_path(report_path),
        "benchmark": pipeline_report.get("benchmark"),
        "llm_profile_set": pipeline_report.get("llm_profile_set"),
        "paths": pipeline_report["paths"],
        "stages": stages,
        "artifacts": artifacts,
        "approval": approval_metrics(artifacts["reviewed_outputs"]),
    }


def require_benchmark_metadata(run_summary: dict[str, Any], *, expected_role: str) -> dict[str, str]:
    benchmark = run_summary.get("benchmark")
    run_name = run_summary["run_name"]
    if not isinstance(benchmark, dict):
        raise SystemExit(
            f"Run {run_name} is missing benchmark metadata. "
            "Only benchmark-marked pipeline reports can be compared."
        )
    benchmark_name = str(benchmark.get("name") or "").strip()
    benchmark_role = str(benchmark.get("role") or "").strip()
    if not benchmark_name:
        raise SystemExit(f"Run {run_name} is missing benchmark.name in its pipeline report.")
    if benchmark_role != expected_role:
        raise SystemExit(
            f"Run {run_name} has benchmark.role={benchmark_role or '<missing>'}, expected {expected_role}."
        )
    return {
        "name": benchmark_name,
        "role": benchmark_role,
    }


def validate_benchmark_pair(reference: dict[str, Any], candidate: dict[str, Any]) -> str:
    reference_benchmark = require_benchmark_metadata(reference, expected_role="reference")
    candidate_benchmark = require_benchmark_metadata(candidate, expected_role="candidate")
    if reference_benchmark["name"] != candidate_benchmark["name"]:
        raise SystemExit(
            "Benchmark names do not match: "
            f"{reference['run_name']} -> {reference_benchmark['name']}, "
            f"{candidate['run_name']} -> {candidate_benchmark['name']}."
        )
    return reference_benchmark["name"]


def build_comparison(reference: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    reference_judge = reference["artifacts"]["judge_results"]
    candidate_judge = candidate["artifacts"]["judge_results"]
    comparison_stages: dict[str, Any] = {}
    for stage_name in reference["stages"]:
        reference_stage = reference["stages"][stage_name]
        candidate_stage = candidate["stages"].get(stage_name, {})
        reference_profile = reference_stage.get("profile") or {}
        candidate_profile = candidate_stage.get("profile") or {}
        reference_defaults = reference_stage.get("configured_defaults") or {}
        candidate_defaults = candidate_stage.get("configured_defaults") or {}
        comparison_stages[stage_name] = {
            "reference_backend": reference_profile.get("backend") or reference_defaults.get("backend"),
            "candidate_backend": candidate_profile.get("backend") or candidate_defaults.get("backend"),
            "reference_model": reference_stage.get("model"),
            "candidate_model": candidate_stage.get("model"),
            "completed_jobs_delta": delta_int(reference_stage.get("completed_jobs"), candidate_stage.get("completed_jobs")),
            "failed_jobs_delta": delta_int(reference_stage.get("failed_jobs"), candidate_stage.get("failed_jobs")),
            "total_elapsed_ms_delta": delta_int(
                reference_stage.get("total_elapsed_ms"),
                candidate_stage.get("total_elapsed_ms"),
            ),
            "total_retry_attempts_delta": delta_int(
                reference_stage.get("total_retry_attempts"),
                candidate_stage.get("total_retry_attempts"),
            ),
        }
    return {
        "reference_run": reference["run_name"],
        "candidate_run": candidate["run_name"],
        "selected_jobs_match": all(
            reference["stages"][stage_name].get("selected_jobs") == candidate["stages"][stage_name].get("selected_jobs")
            for stage_name in reference["stages"]
        ),
        "teacher_outputs_row_delta": delta_int(
            reference["artifacts"]["teacher_outputs"]["rows"],
            candidate["artifacts"]["teacher_outputs"]["rows"],
        ),
        "reviewed_outputs_row_delta": delta_int(
            reference["artifacts"]["reviewed_outputs"]["rows"],
            candidate["artifacts"]["reviewed_outputs"]["rows"],
        ),
        "approved_jobs_delta": delta_int(
            reference["approval"]["approved_jobs"],
            candidate["approval"]["approved_jobs"],
        ),
        "rejected_jobs_delta": delta_int(
            reference["approval"]["rejected_jobs"],
            candidate["approval"]["rejected_jobs"],
        ),
        "approval_rate_delta": delta_float(
            reference["approval"]["approval_rate"],
            candidate["approval"]["approval_rate"],
        ),
        "average_quality_score_delta": delta_float(
            reference_judge.get("average_quality_score"),
            candidate_judge.get("average_quality_score"),
        ),
        "validation": {
            "reference_ok": all(
                artifact["schema"]["ok"] and artifact["source_records"]["ok"]
                for artifact in reference["artifacts"].values()
            ),
            "candidate_ok": all(
                artifact["schema"]["ok"] and artifact["source_records"]["ok"]
                for artifact in candidate["artifacts"].values()
            ),
        },
        "stages": comparison_stages,
    }


def build_benchmark_summary(repo_root: Path, reference_report_path: Path, candidate_report_path: Path) -> dict[str, Any]:
    reference_summary = build_run_summary(repo_root, reference_report_path)
    candidate_summary = build_run_summary(repo_root, candidate_report_path)
    benchmark_name = validate_benchmark_pair(reference_summary, candidate_summary)
    return {
        "benchmark_name": benchmark_name,
        "reference": reference_summary,
        "candidate": candidate_summary,
        "comparison": build_comparison(reference_summary, candidate_summary),
    }


def parse_args() -> Any:
    parser = make_parser("Compare a Codex reference run and an OpenRouter candidate run for the Support-MVP.")
    parser.add_argument("--reference-run")
    parser.add_argument("--reference-report")
    parser.add_argument("--candidate-run")
    parser.add_argument("--candidate-report")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    reference_report = resolve_report_path(
        repo_root,
        run_name=args.reference_run,
        report_path=args.reference_report,
    )
    candidate_report = resolve_report_path(
        repo_root,
        run_name=args.candidate_run,
        report_path=args.candidate_report,
    )
    summary = build_benchmark_summary(repo_root, reference_report, candidate_report)
    if args.output:
        output_path = resolve_artifact_path(repo_root, args.output)
        write_json(output_path, summary)
        print(f"Wrote benchmark comparison -> {output_path}")
    else:
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

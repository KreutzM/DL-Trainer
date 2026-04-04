from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import read_jsonl, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two judge result files for the same job set and summarize decision/score deltas."
    )
    parser.add_argument("--baseline", required=True, help="Path to the earlier judge_results JSONL file.")
    parser.add_argument("--candidate", required=True, help="Path to the later judge_results JSONL file.")
    parser.add_argument("--output", required=True, help="Path to the JSON summary output file.")
    parser.add_argument(
        "--focus-task-type",
        action="append",
        default=[],
        help="Optional task_type filter for the detailed changed-case section.",
    )
    return parser.parse_args()


def _load_rows(path: Path) -> dict[str, dict[str, Any]]:
    return {row["job_id"]: row for row in read_jsonl(path)}


def build_judge_run_delta(
    baseline_rows: dict[str, dict[str, Any]],
    candidate_rows: dict[str, dict[str, Any]],
    *,
    focus_task_types: set[str] | None = None,
) -> dict[str, Any]:
    baseline_job_ids = set(baseline_rows)
    candidate_job_ids = set(candidate_rows)
    if baseline_job_ids != candidate_job_ids:
        missing_in_candidate = sorted(baseline_job_ids - candidate_job_ids)
        missing_in_baseline = sorted(candidate_job_ids - baseline_job_ids)
        message = "judge result job_id mismatch"
        if missing_in_candidate:
            message += f"; missing_in_candidate={','.join(missing_in_candidate)}"
        if missing_in_baseline:
            message += f"; missing_in_baseline={','.join(missing_in_baseline)}"
        raise SystemExit(message)

    changed_cases: list[dict[str, Any]] = []
    total_score_delta = 0
    decision_changes = 0
    improved_scores = 0
    worsened_scores = 0
    unchanged_scores = 0

    for job_id in sorted(baseline_job_ids):
        baseline = baseline_rows[job_id]
        candidate = candidate_rows[job_id]
        task_type = str(candidate.get("task_type") or baseline.get("task_type") or "")
        baseline_score = int(baseline["quality_score"])
        candidate_score = int(candidate["quality_score"])
        score_delta = candidate_score - baseline_score
        total_score_delta += score_delta
        if score_delta > 0:
            improved_scores += 1
        elif score_delta < 0:
            worsened_scores += 1
        else:
            unchanged_scores += 1
        if baseline["decision"] != candidate["decision"]:
            decision_changes += 1

        include_detail = (
            baseline["decision"] != candidate["decision"]
            or score_delta != 0
        )
        if focus_task_types and task_type not in focus_task_types:
            include_detail = include_detail and baseline["decision"] != candidate["decision"]

        if not include_detail:
            continue

        changed_cases.append(
            {
                "job_id": job_id,
                "task_type": task_type,
                "baseline_decision": baseline["decision"],
                "candidate_decision": candidate["decision"],
                "baseline_quality_score": baseline_score,
                "candidate_quality_score": candidate_score,
                "quality_score_delta": score_delta,
                "baseline_summary": baseline.get("summary", ""),
                "candidate_summary": candidate.get("summary", ""),
                "baseline_blocking_reasons": baseline.get("blocking_reasons", []),
                "candidate_blocking_reasons": candidate.get("blocking_reasons", []),
            }
        )

    total_jobs = len(baseline_job_ids)
    return {
        "total_jobs": total_jobs,
        "decision_changes": decision_changes,
        "avg_quality_score_delta": round(total_score_delta / total_jobs, 2) if total_jobs else 0.0,
        "improved_scores": improved_scores,
        "worsened_scores": worsened_scores,
        "unchanged_scores": unchanged_scores,
        "changed_cases": changed_cases,
    }


def main() -> None:
    args = parse_args()
    baseline_path = Path(args.baseline)
    candidate_path = Path(args.candidate)
    focus_task_types = set(args.focus_task_type)
    summary = build_judge_run_delta(
        _load_rows(baseline_path),
        _load_rows(candidate_path),
        focus_task_types=focus_task_types,
    )
    payload = {
        "baseline": str(baseline_path).replace("\\", "/"),
        "candidate": str(candidate_path).replace("\\", "/"),
        "focus_task_types": sorted(focus_task_types),
        **summary,
    }
    write_json(Path(args.output), payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

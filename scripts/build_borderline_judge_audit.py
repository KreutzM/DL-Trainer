from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import compare_support_mvp_benchmarks as benchmark_compare
from build_judge_audit_report import extract_answer_text, normalized_path
from common import find_repo_root, make_parser, read_jsonl, write_json

RUN_ORDER = ["codex", "openrouter_v1", "openrouter_v2", "openrouter_v3"]


def _load_run_data(repo_root: Path, report_path: Path) -> dict[str, Any]:
    summary = benchmark_compare.build_run_summary(repo_root, report_path)
    reviewed_rows = {
        str(row["job_id"]): row
        for row in read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, summary["paths"]["reviewed_outputs"]))
    }
    judge_rows = {
        str(row["job_id"]): row
        for row in read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, summary["paths"]["judge_results"]))
    }
    return {
        "summary": summary,
        "reviewed_rows": reviewed_rows,
        "judge_rows": judge_rows,
    }


def _source_spans(*rows: dict[str, Any] | None) -> list[str]:
    for row in rows:
        if not row:
            continue
        records = row.get("provenance", {}).get("source_records") or []
        if records:
            spans = records[0].get("source_spans") or []
            return [str(span) for span in spans]
    return []


def _judge_entry(judge_row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not judge_row:
        return None
    return {
        "decision": judge_row.get("decision"),
        "quality_score": judge_row.get("quality_score"),
        "summary": judge_row.get("summary"),
        "blocking_reasons": judge_row.get("blocking_reasons") or [],
        "reviewer_prompt_version": judge_row.get("reviewer_prompt_version"),
        "reviewer_model": judge_row.get("reviewer_model"),
        "reviewer_run_id": judge_row.get("reviewer_run_id"),
    }


def _answer_entry(reviewed_row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not reviewed_row:
        return None
    return {
        "review_status": reviewed_row.get("review_status"),
        "teacher_provider": reviewed_row.get("teacher_provider"),
        "teacher_model": reviewed_row.get("teacher_model"),
        "teacher_run_id": reviewed_row.get("teacher_run_id"),
        "answer_text": extract_answer_text(reviewed_row),
    }


def _decision_value(case: dict[str, Any], run_key: str) -> str:
    judge = case["judges"].get(run_key)
    if not judge:
        return "missing"
    return str(judge.get("decision") or "missing")


def _quality_score(case: dict[str, Any], run_key: str) -> int | None:
    judge = case["judges"].get(run_key)
    if not judge or judge.get("quality_score") is None:
        return None
    return int(judge["quality_score"])


def _openrouter_decisions(case: dict[str, Any]) -> list[str]:
    return [_decision_value(case, run_key) for run_key in RUN_ORDER[1:]]


def _openrouter_answer_texts(case: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    for run_key in RUN_ORDER[1:]:
        answer = case["answers"].get(run_key)
        if not answer:
            continue
        text = str(answer.get("answer_text") or "").strip()
        if text:
            texts.append(text)
    return texts


def classify_case(case: dict[str, Any]) -> str:
    codex_decision = _decision_value(case, "codex")
    openrouter_decisions = [decision for decision in _openrouter_decisions(case) if decision != "missing"]
    distinct_openrouter = set(openrouter_decisions)
    codex_answer = str((case["answers"].get("codex") or {}).get("answer_text") or "").strip()
    openrouter_texts = _openrouter_answer_texts(case)
    openrouter_same_answer = len(set(openrouter_texts)) <= 1
    codex_vs_openrouter_answer_changed = bool(openrouter_texts) and any(text != codex_answer for text in openrouter_texts)

    if len(distinct_openrouter) > 1:
        return "same_answer_judge_instability" if openrouter_same_answer else "answer_and_judge_shift"
    if codex_decision not in {"approve", "reject"}:
        return "insufficient_codex_reference"
    if not distinct_openrouter:
        return "missing_openrouter_signal"
    openrouter_decision = next(iter(distinct_openrouter))
    if codex_decision != openrouter_decision:
        if codex_vs_openrouter_answer_changed:
            return "answer_quality_gain_or_loss"
        return "judge_calibration_conflict"
    score_values = [score for score in (_quality_score(case, run_key) for run_key in RUN_ORDER) if score is not None]
    if score_values and max(score_values) - min(score_values) >= 20:
        return "reasoning_drift_same_decision"
    return "stable_borderline"


def selection_tags(
    case: dict[str, Any],
    *,
    focus_task_types: set[str],
    score_spread_threshold: int,
    borderline_approve_max: int,
    borderline_reject_min: int,
) -> list[str]:
    task_type = str(case["task_type"])
    tags: list[str] = []
    if task_type in focus_task_types:
        tags.append(f"focus_task_type:{task_type}")

    codex_decision = _decision_value(case, "codex")
    if codex_decision in {"approve", "reject"}:
        for run_key in RUN_ORDER[1:]:
            candidate_decision = _decision_value(case, run_key)
            if candidate_decision in {"approve", "reject"} and candidate_decision != codex_decision:
                tags.append(f"decision_mismatch_vs_codex:{run_key}")

    openrouter_decisions = [decision for decision in _openrouter_decisions(case) if decision in {"approve", "reject"}]
    if len(set(openrouter_decisions)) > 1:
        tags.append("openrouter_internal_decision_disagreement")

    score_values = [score for score in (_quality_score(case, run_key) for run_key in RUN_ORDER) if score is not None]
    if score_values and max(score_values) - min(score_values) >= score_spread_threshold:
        tags.append(f"high_score_spread>={score_spread_threshold}")

    if any(
        _decision_value(case, run_key) == "approve"
        and (_quality_score(case, run_key) or 0) <= borderline_approve_max
        for run_key in RUN_ORDER
    ):
        tags.append(f"borderline_approve<={borderline_approve_max}")
    if any(
        _decision_value(case, run_key) == "reject"
        and (_quality_score(case, run_key) or 0) >= borderline_reject_min
        for run_key in RUN_ORDER
    ):
        tags.append(f"borderline_reject>={borderline_reject_min}")
    return tags


def case_priority(case: dict[str, Any], *, borderline_approve_max: int, borderline_reject_min: int) -> tuple[int, int, int]:
    decision_mismatches = sum(
        1
        for run_key in RUN_ORDER[1:]
        if _decision_value(case, "codex") in {"approve", "reject"}
        and _decision_value(case, run_key) in {"approve", "reject"}
        and _decision_value(case, run_key) != _decision_value(case, "codex")
    )
    openrouter_internal_mismatch = 1 if len(set(_openrouter_decisions(case))) > 1 else 0
    score_values = [score for score in (_quality_score(case, run_key) for run_key in RUN_ORDER) if score is not None]
    score_spread = max(score_values) - min(score_values) if score_values else 0

    distance_candidates: list[int] = []
    for run_key in RUN_ORDER:
        score = _quality_score(case, run_key)
        decision = _decision_value(case, run_key)
        if score is None:
            continue
        if decision == "approve":
            distance_candidates.append(abs(score - borderline_approve_max))
        elif decision == "reject":
            distance_candidates.append(abs(score - borderline_reject_min))
    closest_distance = min(distance_candidates) if distance_candidates else 999
    return (decision_mismatches + openrouter_internal_mismatch, score_spread, -closest_distance)


def build_borderline_judge_audit(
    repo_root: Path,
    *,
    codex_report_path: Path,
    openrouter_v1_report_path: Path,
    openrouter_v2_report_path: Path,
    openrouter_v3_report_path: Path,
    focus_task_types: list[str],
    score_spread_threshold: int,
    borderline_approve_max: int,
    borderline_reject_min: int,
    min_cases_per_task_type: int,
) -> dict[str, Any]:
    runs = {
        "codex": _load_run_data(repo_root, codex_report_path),
        "openrouter_v1": _load_run_data(repo_root, openrouter_v1_report_path),
        "openrouter_v2": _load_run_data(repo_root, openrouter_v2_report_path),
        "openrouter_v3": _load_run_data(repo_root, openrouter_v3_report_path),
    }
    focus_task_type_set = set(focus_task_types)

    common_job_ids = sorted(
        set.intersection(*(set(run["judge_rows"]) & set(run["reviewed_rows"]) for run in runs.values()))
    )
    cases: list[dict[str, Any]] = []
    for job_id in common_job_ids:
        reviewed_rows = [runs[run_key]["reviewed_rows"].get(job_id) for run_key in RUN_ORDER]
        judge_rows = [runs[run_key]["judge_rows"].get(job_id) for run_key in RUN_ORDER]
        first_judge_row = next((row for row in judge_rows if row is not None), None)
        task_type = str((first_judge_row or {}).get("task_type") or "unknown")
        case = {
            "job_id": job_id,
            "target_split": next(
                (row.get("target_split") for row in judge_rows if row is not None and row.get("target_split") is not None),
                None,
            ),
            "task_type": task_type,
            "source_spans": _source_spans(*(reviewed_rows + judge_rows)),
            "judges": {
                run_key: _judge_entry(runs[run_key]["judge_rows"].get(job_id))
                for run_key in RUN_ORDER
                if runs[run_key]["judge_rows"].get(job_id)
            },
            "answers": {
                run_key: _answer_entry(runs[run_key]["reviewed_rows"].get(job_id))
                for run_key in RUN_ORDER
                if runs[run_key]["reviewed_rows"].get(job_id)
            },
        }
        case["selection_tags"] = selection_tags(
            case,
            focus_task_types=focus_task_type_set,
            score_spread_threshold=score_spread_threshold,
            borderline_approve_max=borderline_approve_max,
            borderline_reject_min=borderline_reject_min,
        )
        score_values = [score for score in (_quality_score(case, run_key) for run_key in RUN_ORDER) if score is not None]
        case["score_spread"] = max(score_values) - min(score_values) if score_values else None
        openrouter_texts = _openrouter_answer_texts(case)
        case["same_openrouter_answer_across_versions"] = len(set(openrouter_texts)) <= 1
        codex_answer = str((case["answers"].get("codex") or {}).get("answer_text") or "").strip()
        case["codex_vs_openrouter_answer_changed"] = bool(openrouter_texts) and any(text != codex_answer for text in openrouter_texts)
        case["classification_hint"] = classify_case(case)
        case["primary_selection"] = any(not tag.startswith("focus_task_type:") for tag in case["selection_tags"])
        cases.append(case)

    selected_cases = [case for case in cases if case["task_type"] in focus_task_type_set and case["primary_selection"]]
    selected_job_ids = {case["job_id"] for case in selected_cases}
    task_counts = Counter(case["task_type"] for case in selected_cases)

    for task_type in focus_task_types:
        if task_counts[task_type] >= min_cases_per_task_type:
            continue
        remaining = [
            case
            for case in cases
            if case["task_type"] == task_type and case["job_id"] not in selected_job_ids
        ]
        remaining.sort(
            key=lambda case: case_priority(
                case,
                borderline_approve_max=borderline_approve_max,
                borderline_reject_min=borderline_reject_min,
            ),
            reverse=True,
        )
        needed = min_cases_per_task_type - task_counts[task_type]
        for case in remaining[:needed]:
            case["selection_tags"].append("task_coverage_backfill")
            selected_cases.append(case)
            selected_job_ids.add(case["job_id"])
            task_counts[task_type] += 1

    selected_cases.sort(
        key=lambda case: (
            focus_task_types.index(case["task_type"]) if case["task_type"] in focus_task_types else 999,
            case["job_id"],
        )
    )

    selection_tag_counts = Counter(tag for case in selected_cases for tag in case["selection_tags"])
    classification_hint_counts = Counter(case["classification_hint"] for case in selected_cases)

    mismatch_patterns_vs_codex: dict[str, Any] = {}
    for run_key in RUN_ORDER[1:]:
        approve_when_codex_rejects = []
        reject_when_codex_approves = []
        same_decision_high_score_delta = []
        for case in selected_cases:
            codex_decision = _decision_value(case, "codex")
            candidate_decision = _decision_value(case, run_key)
            codex_score = _quality_score(case, "codex")
            candidate_score = _quality_score(case, run_key)
            if codex_decision == "reject" and candidate_decision == "approve":
                approve_when_codex_rejects.append(case["job_id"])
            if codex_decision == "approve" and candidate_decision == "reject":
                reject_when_codex_approves.append(case["job_id"])
            if (
                codex_decision == candidate_decision
                and codex_decision in {"approve", "reject"}
                and codex_score is not None
                and candidate_score is not None
                and abs(candidate_score - codex_score) >= score_spread_threshold
            ):
                same_decision_high_score_delta.append(case["job_id"])
        mismatch_patterns_vs_codex[run_key] = {
            "approve_when_codex_rejects": approve_when_codex_rejects,
            "reject_when_codex_approves": reject_when_codex_approves,
            "same_decision_high_score_delta": same_decision_high_score_delta,
        }

    openrouter_pattern_counts = Counter()
    for case in selected_cases:
        decisions = tuple(_openrouter_decisions(case))
        if len(set(decisions)) == 1:
            openrouter_pattern_counts["stable_across_openrouter_versions"] += 1
        else:
            openrouter_pattern_counts["openrouter_internal_disagreement"] += 1
            vote_counter = Counter(decisions)
            if vote_counter["approve"] == 2 and vote_counter["reject"] == 1:
                openrouter_pattern_counts["two_approve_one_reject"] += 1
            elif vote_counter["reject"] == 2 and vote_counter["approve"] == 1:
                openrouter_pattern_counts["two_reject_one_approve"] += 1

    return {
        "audit_scope": {
            "benchmark_name": benchmark_compare.validate_benchmark_pair(
                runs["codex"]["summary"],
                runs["openrouter_v1"]["summary"],
            ),
            "included_runs": {
                run_key: {
                    "run_name": runs[run_key]["summary"]["run_name"],
                    "report_path": runs[run_key]["summary"]["report_path"],
                }
                for run_key in RUN_ORDER
            },
            "focus_task_types": focus_task_types,
            "selection_rules": {
                "score_spread_threshold": score_spread_threshold,
                "borderline_approve_max": borderline_approve_max,
                "borderline_reject_min": borderline_reject_min,
                "min_cases_per_task_type": min_cases_per_task_type,
                "primary_selection": [
                    "decision mismatch vs codex in any openrouter version",
                    "decision disagreement across openrouter v1/v2/v3 on same answer set",
                    "score spread across codex/v1/v2/v3 at or above threshold",
                    "approve score at or below borderline approve threshold",
                    "reject score at or above borderline reject threshold",
                ],
                "coverage_backfill": "If a focus task type has fewer than the requested minimum cases, add the most informative remaining cases for that task type.",
            },
            "population_size": len(common_job_ids),
        },
        "selected_case_count": len(selected_cases),
        "task_type_counts": dict(sorted(Counter(case["task_type"] for case in selected_cases).items())),
        "selection_tag_counts": dict(sorted(selection_tag_counts.items())),
        "classification_hint_counts": dict(sorted(classification_hint_counts.items())),
        "mismatch_patterns_vs_codex": mismatch_patterns_vs_codex,
        "openrouter_pattern_counts": dict(sorted(openrouter_pattern_counts.items())),
        "cases": selected_cases,
    }


def parse_args() -> Any:
    parser = make_parser("Build a broader multi-class borderline judge audit from existing Codex and OpenRouter artifacts.")
    parser.add_argument("--codex-report", required=True)
    parser.add_argument("--openrouter-v1-report", required=True)
    parser.add_argument("--openrouter-v2-report", required=True)
    parser.add_argument("--openrouter-v3-report", required=True)
    parser.add_argument(
        "--focus-task-type",
        action="append",
        dest="focus_task_types",
        default=[
            "step_by_step",
            "faq_direct_answer",
            "clarification",
            "troubleshooting",
            "uncertainty_escalation",
        ],
    )
    parser.add_argument("--score-spread-threshold", type=int, default=20)
    parser.add_argument("--borderline-approve-max", type=int, default=92)
    parser.add_argument("--borderline-reject-min", type=int, default=60)
    parser.add_argument("--min-cases-per-task-type", type=int, default=2)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def _resolve_path(repo_root: Path, path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else repo_root / path


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    summary = build_borderline_judge_audit(
        repo_root,
        codex_report_path=_resolve_path(repo_root, args.codex_report),
        openrouter_v1_report_path=_resolve_path(repo_root, args.openrouter_v1_report),
        openrouter_v2_report_path=_resolve_path(repo_root, args.openrouter_v2_report),
        openrouter_v3_report_path=_resolve_path(repo_root, args.openrouter_v3_report),
        focus_task_types=args.focus_task_types,
        score_spread_threshold=args.score_spread_threshold,
        borderline_approve_max=args.borderline_approve_max,
        borderline_reject_min=args.borderline_reject_min,
        min_cases_per_task_type=args.min_cases_per_task_type,
    )
    output_path = _resolve_path(repo_root, args.output)
    write_json(output_path, summary)
    print(f"Wrote borderline judge audit -> {normalized_path(output_path)}")


if __name__ == "__main__":
    main()

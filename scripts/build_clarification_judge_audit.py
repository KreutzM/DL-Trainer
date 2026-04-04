from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import compare_support_mvp_benchmarks as benchmark_compare
from build_judge_audit_report import extract_answer_text, normalized_path
from common import find_repo_root, make_parser, read_jsonl, write_json

RUN_ORDER = ["codex", "openrouter_v1", "openrouter_v2", "openrouter_v3"]


def _clarification_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(row["job_id"]): row
        for row in rows
        if str(row.get("task_type") or "") == "clarification"
    }


def _load_run_data(repo_root: Path, report_path: Path) -> dict[str, Any]:
    summary = benchmark_compare.build_run_summary(repo_root, report_path)
    reviewed_rows = _clarification_rows(
        read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, summary["paths"]["reviewed_outputs"]))
    )
    judge_rows = _clarification_rows(
        read_jsonl(benchmark_compare.resolve_artifact_path(repo_root, summary["paths"]["judge_results"]))
    )
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


def _classify_case(case: dict[str, Any]) -> str:
    codex_decision = _decision_value(case, "codex")
    openrouter_decisions = [_decision_value(case, run_key) for run_key in RUN_ORDER[1:] if case["judges"].get(run_key)]
    distinct_openrouter = {decision for decision in openrouter_decisions if decision != "missing"}
    if len(distinct_openrouter) <= 1 and (not distinct_openrouter or codex_decision in distinct_openrouter):
        return "stable_alignment"
    v1 = _decision_value(case, "openrouter_v1")
    v2 = _decision_value(case, "openrouter_v2")
    v3 = _decision_value(case, "openrouter_v3")
    if v1 == v2 and v3 != v2 and v3 != "missing":
        return "v3_outlier"
    if codex_decision != "missing" and codex_decision not in distinct_openrouter:
        return "systematic_openrouter_disagreement"
    return "mixed_signal"


def build_clarification_judge_audit(
    repo_root: Path,
    *,
    codex_report_path: Path,
    openrouter_v1_report_path: Path,
    openrouter_v2_report_path: Path,
    openrouter_v3_report_path: Path,
    supplemental_report_paths: list[Path],
) -> dict[str, Any]:
    runs = {
        "codex": _load_run_data(repo_root, codex_report_path),
        "openrouter_v1": _load_run_data(repo_root, openrouter_v1_report_path),
        "openrouter_v2": _load_run_data(repo_root, openrouter_v2_report_path),
        "openrouter_v3": _load_run_data(repo_root, openrouter_v3_report_path),
    }
    supplemental_runs = [_load_run_data(repo_root, path) for path in supplemental_report_paths]

    job_ids = sorted(
        set().union(*(set(run["judge_rows"]) | set(run["reviewed_rows"]) for run in runs.values()))
    )
    cases: list[dict[str, Any]] = []
    for job_id in job_ids:
        primary_rows = [
            runs[run_key]["reviewed_rows"].get(job_id) for run_key in RUN_ORDER
        ]
        primary_judge_rows = [
            runs[run_key]["judge_rows"].get(job_id) for run_key in RUN_ORDER
        ]
        judges = {
            run_key: _judge_entry(runs[run_key]["judge_rows"].get(job_id))
            for run_key in RUN_ORDER
            if runs[run_key]["judge_rows"].get(job_id)
        }
        answers = {
            run_key: _answer_entry(runs[run_key]["reviewed_rows"].get(job_id))
            for run_key in RUN_ORDER
            if runs[run_key]["reviewed_rows"].get(job_id)
        }
        supplemental: list[dict[str, Any]] = []
        for run in supplemental_runs:
            reviewed_row = run["reviewed_rows"].get(job_id)
            judge_row = run["judge_rows"].get(job_id)
            if not reviewed_row and not judge_row:
                continue
            supplemental.append(
                {
                    "run_name": run["summary"]["run_name"],
                    "report_path": run["summary"]["report_path"],
                    "answer": _answer_entry(reviewed_row),
                    "judge": _judge_entry(judge_row),
                }
            )

        case = {
            "job_id": job_id,
            "target_split": next(
                (
                    row.get("target_split")
                    for row in primary_judge_rows
                    if row is not None and row.get("target_split") is not None
                ),
                None,
            ),
            "task_type": "clarification",
            "source_spans": _source_spans(*(primary_rows + primary_judge_rows)),
            "judges": judges,
            "answers": answers,
            "supplemental_runs": supplemental,
        }
        case["classification_hint"] = _classify_case(case)
        cases.append(case)

    run_case_counts = {
        run_key: len(runs[run_key]["judge_rows"])
        for run_key in RUN_ORDER
    }
    decision_counts = {
        run_key: dict(
            sorted(
                Counter(
                    str(row.get("decision") or "missing")
                    for row in runs[run_key]["judge_rows"].values()
                ).items()
            )
        )
        for run_key in RUN_ORDER
    }
    mismatch_counts_vs_codex = {
        run_key: sum(
            1
            for case in cases
            if _decision_value(case, "codex") != "missing"
            and _decision_value(case, run_key) != "missing"
            and _decision_value(case, "codex") != _decision_value(case, run_key)
        )
        for run_key in RUN_ORDER[1:]
    }
    hint_counts = Counter(case["classification_hint"] for case in cases)

    return {
        "scope": {
            "task_type": "clarification",
            "included_runs": {
                run_key: {
                    "run_name": runs[run_key]["summary"]["run_name"],
                    "report_path": runs[run_key]["summary"]["report_path"],
                }
                for run_key in RUN_ORDER
            },
            "supplemental_runs": [
                {
                    "run_name": run["summary"]["run_name"],
                    "report_path": run["summary"]["report_path"],
                }
                for run in supplemental_runs
            ],
        },
        "selected_case_count": len(cases),
        "run_case_counts": run_case_counts,
        "decision_counts": decision_counts,
        "mismatch_counts_vs_codex": mismatch_counts_vs_codex,
        "classification_hint_counts": dict(sorted(hint_counts.items())),
        "cases": cases,
    }


def parse_args() -> Any:
    parser = make_parser("Build a clarification-focused audit from existing Codex and OpenRouter judge artifacts.")
    parser.add_argument("--codex-report", required=True)
    parser.add_argument("--openrouter-v1-report", required=True)
    parser.add_argument("--openrouter-v2-report", required=True)
    parser.add_argument("--openrouter-v3-report", required=True)
    parser.add_argument("--supplemental-report", action="append", default=[])
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def _resolve_path(repo_root: Path, path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else repo_root / path


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    summary = build_clarification_judge_audit(
        repo_root,
        codex_report_path=_resolve_path(repo_root, args.codex_report),
        openrouter_v1_report_path=_resolve_path(repo_root, args.openrouter_v1_report),
        openrouter_v2_report_path=_resolve_path(repo_root, args.openrouter_v2_report),
        openrouter_v3_report_path=_resolve_path(repo_root, args.openrouter_v3_report),
        supplemental_report_paths=[_resolve_path(repo_root, path) for path in args.supplemental_report],
    )
    output_path = _resolve_path(repo_root, args.output)
    write_json(output_path, summary)
    print(f"Wrote clarification judge audit -> {normalized_path(output_path)}")


if __name__ == "__main__":
    main()

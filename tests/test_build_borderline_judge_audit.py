from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_borderline_judge_audit as borderline_audit  # noqa: E402


def _source_record(job_id: str) -> dict[str, object]:
    return {
        "doc_id": "JAWS-DE-demo",
        "chunk_id": f"{job_id}-chunk",
        "normalized_path": "data/normalized/JAWS/DE/demo.md",
        "source_spans": [f"{job_id}:1-2"],
    }


def _reviewed_output(job_id: str, *, task_type: str, target_split: str, answer_text: str) -> dict[str, object]:
    return {
        "output_id": f"run::{job_id}",
        "job_id": job_id,
        "record_type": "eval_case",
        "target_split": target_split,
        "product": "JAWS",
        "language": "de",
        "task_type": task_type,
        "source_doc_ids": ["JAWS-DE-demo"],
        "source_chunk_ids": [f"{job_id}-chunk"],
        "teacher_provider": "openrouter",
        "teacher_model": "openai/gpt-5.4",
        "teacher_run_id": "run-answer",
        "teacher_prompt_version": "jaws_de_support_answer_mvp_v3",
        "generation_mode": "teacher_answer_openrouter_v1",
        "review_status": "codex_reviewed",
        "raw_response_path": "data/derived/teacher_outputs/JAWS/DE/run_raw_responses.jsonl",
        "candidate": {"messages": [{"role": "assistant", "content": answer_text}]},
        "provenance": {
            "transform_pipeline_version": "0.8.0",
            "source_job_path": "data/derived/teacher_jobs/JAWS/DE/demo.jsonl",
            "source_records": [_source_record(job_id)],
        },
    }


def _judge_result(
    job_id: str,
    *,
    task_type: str,
    target_split: str,
    decision: str,
    quality_score: int,
    prompt_version: str,
) -> dict[str, object]:
    return {
        "review_id": f"judge::{job_id}",
        "job_id": job_id,
        "output_id": f"run::{job_id}",
        "simulation_id": f"sim::{job_id}",
        "response_id": f"resp::{job_id}",
        "target_split": target_split,
        "record_type": "eval_case",
        "task_type": task_type,
        "product": "JAWS",
        "language": "de",
        "source_doc_ids": ["JAWS-DE-demo"],
        "source_chunk_ids": [f"{job_id}-chunk"],
        "reviewer_provider": "openrouter",
        "reviewer_model": "openai/gpt-5.4",
        "reviewer_run_id": f"run-judge-{prompt_version}",
        "reviewer_prompt_version": prompt_version,
        "generation_mode": "teacher_judge_openrouter_v1",
        "decision": decision,
        "quality_score": quality_score,
        "summary": f"{decision} {job_id}",
        "blocking_reasons": [] if decision == "approve" else ["quality"],
        "strengths": ["belegt"],
        "improvement_notes": [] if decision == "approve" else ["verbessern"],
        "source_chunk_ids_confirmed": [f"{job_id}-chunk"],
        "provenance": {
            "transform_pipeline_version": "0.8.0",
            "source_job_path": "data/derived/teacher_jobs/JAWS/DE/demo.jsonl",
            "source_records": [_source_record(job_id)],
        },
    }


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def _pipeline_report(*, run_name: str, reviewed_outputs: Path, judge_results: Path, benchmark_role: str) -> dict[str, object]:
    return {
        "run_name": run_name,
        "llm_profile_set": "support_mvp_demo",
        "defaults": {},
        "llm_profiles": {},
        "stages": {
            "user_simulation": {"selected_jobs": 6, "completed_jobs": 6, "failed_jobs": [], "runtime": {}},
            "answering": {"selected_jobs": 6, "completed_jobs": 6, "failed_jobs": [], "runtime": {}},
            "judge": {"selected_jobs": 6, "completed_jobs": 6, "failed_jobs": [], "runtime": {}},
        },
        "paths": {
            "teacher_outputs": str(reviewed_outputs),
            "reviewed_outputs": str(reviewed_outputs),
            "judge_results": str(judge_results),
        },
        "benchmark": {
            "name": "borderline-audit-demo",
            "role": benchmark_role,
            "profile_set": "support_mvp_demo",
        },
    }


def test_build_borderline_judge_audit_selects_cases_and_backfills_faq_coverage(tmp_path: Path) -> None:
    jobs = {
        "job-step-shift": ("step_by_step", "eval"),
        "job-step-stable-reject": ("step_by_step", "train"),
        "job-faq-mixed": ("faq_direct_answer", "eval"),
        "job-faq-stable": ("faq_direct_answer", "train"),
        "job-clarify-outlier": ("clarification", "eval"),
        "job-uncertainty-borderline": ("uncertainty_escalation", "eval"),
    }

    answers = {
        "codex": {
            "job-step-shift": "Codex duplicated steps",
            "job-step-stable-reject": "Codex mixed procedures",
            "job-faq-mixed": "Codex vague faq",
            "job-faq-stable": "Codex stable faq",
            "job-clarify-outlier": "Codex clarification",
            "job-uncertainty-borderline": "Codex uncertainty answer",
        },
        "openrouter_v1": {
            "job-step-shift": "OpenRouter clean steps",
            "job-step-stable-reject": "OpenRouter mixed procedures",
            "job-faq-mixed": "OpenRouter concrete faq",
            "job-faq-stable": "OpenRouter stable faq",
            "job-clarify-outlier": "OpenRouter clarification",
            "job-uncertainty-borderline": "OpenRouter uncertainty answer",
        },
        "openrouter_v2": {
            "job-step-shift": "OpenRouter clean steps",
            "job-step-stable-reject": "OpenRouter mixed procedures",
            "job-faq-mixed": "OpenRouter concrete faq",
            "job-faq-stable": "OpenRouter stable faq",
            "job-clarify-outlier": "OpenRouter clarification",
            "job-uncertainty-borderline": "OpenRouter uncertainty answer",
        },
        "openrouter_v3": {
            "job-step-shift": "OpenRouter clean steps",
            "job-step-stable-reject": "OpenRouter mixed procedures",
            "job-faq-mixed": "OpenRouter concrete faq",
            "job-faq-stable": "OpenRouter stable faq",
            "job-clarify-outlier": "OpenRouter clarification",
            "job-uncertainty-borderline": "OpenRouter uncertainty answer",
        },
    }

    judge_specs = {
        "codex": {
            "job-step-shift": ("reject", 64, "judge_v1"),
            "job-step-stable-reject": ("reject", 82, "judge_v1"),
            "job-faq-mixed": ("reject", 52, "judge_v1"),
            "job-faq-stable": ("approve", 98, "judge_v1"),
            "job-clarify-outlier": ("approve", 93, "judge_v1"),
            "job-uncertainty-borderline": ("approve", 91, "judge_v1"),
        },
        "openrouter_v1": {
            "job-step-shift": ("approve", 94, "judge_v1"),
            "job-step-stable-reject": ("reject", 56, "judge_v1"),
            "job-faq-mixed": ("approve", 90, "judge_v1"),
            "job-faq-stable": ("approve", 94, "judge_v1"),
            "job-clarify-outlier": ("approve", 88, "judge_v1"),
            "job-uncertainty-borderline": ("approve", 97, "judge_v1"),
        },
        "openrouter_v2": {
            "job-step-shift": ("approve", 95, "judge_v2"),
            "job-step-stable-reject": ("reject", 28, "judge_v2"),
            "job-faq-mixed": ("reject", 62, "judge_v2"),
            "job-faq-stable": ("approve", 96, "judge_v2"),
            "job-clarify-outlier": ("approve", 92, "judge_v2"),
            "job-uncertainty-borderline": ("approve", 97, "judge_v2"),
        },
        "openrouter_v3": {
            "job-step-shift": ("approve", 91, "judge_v3"),
            "job-step-stable-reject": ("reject", 42, "judge_v3"),
            "job-faq-mixed": ("approve", 91, "judge_v3"),
            "job-faq-stable": ("approve", 95, "judge_v3"),
            "job-clarify-outlier": ("reject", 41, "judge_v3"),
            "job-uncertainty-borderline": ("approve", 96, "judge_v3"),
        },
    }

    report_paths: dict[str, Path] = {}
    for run_key in borderline_audit.RUN_ORDER:
        reviewed_path = tmp_path / f"{run_key}_reviewed.jsonl"
        judge_path = tmp_path / f"{run_key}_judge.jsonl"
        report_path = tmp_path / f"{run_key}_report.json"
        _write_jsonl(
            reviewed_path,
            [
                _reviewed_output(job_id, task_type=task_type, target_split=target_split, answer_text=answers[run_key][job_id])
                for job_id, (task_type, target_split) in jobs.items()
            ],
        )
        _write_jsonl(
            judge_path,
            [
                _judge_result(
                    job_id,
                    task_type=task_type,
                    target_split=target_split,
                    decision=judge_specs[run_key][job_id][0],
                    quality_score=judge_specs[run_key][job_id][1],
                    prompt_version=judge_specs[run_key][job_id][2],
                )
                for job_id, (task_type, target_split) in jobs.items()
            ],
        )
        report_path.write_text(
            json.dumps(
                _pipeline_report(
                    run_name=run_key,
                    reviewed_outputs=reviewed_path,
                    judge_results=judge_path,
                    benchmark_role="reference" if run_key == "codex" else "candidate",
                )
            ),
            encoding="utf-8",
        )
        report_paths[run_key] = report_path

    summary = borderline_audit.build_borderline_judge_audit(
        ROOT,
        codex_report_path=report_paths["codex"],
        openrouter_v1_report_path=report_paths["openrouter_v1"],
        openrouter_v2_report_path=report_paths["openrouter_v2"],
        openrouter_v3_report_path=report_paths["openrouter_v3"],
        focus_task_types=["step_by_step", "faq_direct_answer", "clarification", "uncertainty_escalation"],
        score_spread_threshold=20,
        borderline_approve_max=92,
        borderline_reject_min=60,
        min_cases_per_task_type=2,
    )

    assert summary["audit_scope"]["benchmark_name"] == "borderline-audit-demo"
    assert summary["selected_case_count"] == 6
    assert summary["task_type_counts"] == {
        "clarification": 1,
        "faq_direct_answer": 2,
        "step_by_step": 2,
        "uncertainty_escalation": 1,
    }

    cases_by_job = {case["job_id"]: case for case in summary["cases"]}
    assert cases_by_job["job-step-shift"]["classification_hint"] == "answer_quality_gain_or_loss"
    assert cases_by_job["job-faq-mixed"]["classification_hint"] == "same_answer_judge_instability"
    assert cases_by_job["job-clarify-outlier"]["classification_hint"] == "same_answer_judge_instability"
    assert cases_by_job["job-step-stable-reject"]["classification_hint"] == "reasoning_drift_same_decision"
    assert cases_by_job["job-faq-stable"]["selection_tags"][-1] == "task_coverage_backfill"
    assert cases_by_job["job-step-shift"]["codex_vs_openrouter_answer_changed"] is True
    assert cases_by_job["job-faq-mixed"]["same_openrouter_answer_across_versions"] is True
    assert "borderline_approve<=92" in cases_by_job["job-uncertainty-borderline"]["selection_tags"]

    assert summary["mismatch_patterns_vs_codex"]["openrouter_v1"]["approve_when_codex_rejects"] == [
        "job-step-shift",
        "job-faq-mixed",
    ]
    assert summary["mismatch_patterns_vs_codex"]["openrouter_v3"]["reject_when_codex_approves"] == [
        "job-clarify-outlier",
    ]
    assert summary["openrouter_pattern_counts"]["openrouter_internal_disagreement"] == 2

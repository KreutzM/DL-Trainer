from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_judge_audit_report as judge_audit  # noqa: E402


def _source_record(job_id: str) -> dict[str, object]:
    return {
        "doc_id": "JAWS-DE-demo",
        "chunk_id": f"{job_id}-chunk",
        "normalized_path": "data/normalized/JAWS/DE/demo.md",
        "source_spans": ["1-2"],
    }


def _reviewed_output(
    job_id: str,
    *,
    task_type: str,
    target_split: str,
    review_status: str,
    answer_text: str,
    use_messages: bool = False,
) -> dict[str, object]:
    candidate: dict[str, object]
    if use_messages:
        candidate = {
            "messages": [
                {"role": "user", "content": "Frage"},
                {"role": "assistant", "content": answer_text},
            ]
        }
    else:
        candidate = {"reference_answer": answer_text}
    candidate.update(
        {
            "eval_id": f"{job_id}__candidate",
            "task_type": task_type,
            "split": target_split,
        }
    )
    return {
        "output_id": f"run::{job_id}",
        "job_id": job_id,
        "record_type": "sft_sample",
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
        "review_status": review_status,
        "raw_response_path": "data/derived/teacher_outputs/JAWS/DE/run_raw_responses.jsonl",
        "candidate": candidate,
        "provenance": {
            "transform_pipeline_version": "0.8.0",
            "source_job_path": "data/derived/teacher_jobs/JAWS/DE/demo.jsonl",
            "source_records": [_source_record(job_id)],
        },
    }


def _judge_result(job_id: str, *, task_type: str, target_split: str, decision: str, quality_score: int) -> dict[str, object]:
    return {
        "review_id": f"judge::{job_id}",
        "job_id": job_id,
        "output_id": f"run::{job_id}",
        "simulation_id": f"sim::{job_id}",
        "response_id": f"resp::{job_id}",
        "target_split": target_split,
        "record_type": "sft_sample",
        "task_type": task_type,
        "product": "JAWS",
        "language": "de",
        "source_doc_ids": ["JAWS-DE-demo"],
        "source_chunk_ids": [f"{job_id}-chunk"],
        "reviewer_provider": "openrouter",
        "reviewer_model": "openai/gpt-5.4",
        "reviewer_run_id": "run-judge",
        "reviewer_prompt_version": "jaws_de_support_judge_v1",
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


def _pipeline_report(
    *,
    run_name: str,
    reviewed_outputs: Path,
    judge_results: Path,
    benchmark_role: str,
) -> dict[str, object]:
    return {
        "run_name": run_name,
        "llm_profile_set": "support_mvp_demo",
        "defaults": {
            "user_simulation": {"backend": "openrouter", "model": "openai/gpt-5.4-mini"},
            "answering": {"backend": "openrouter", "model": "openai/gpt-5.4"},
            "judge": {"backend": "openrouter", "model": "openai/gpt-5.4"},
        },
        "llm_profiles": {},
        "stages": {
            "user_simulation": {
                "simulator_provider": "openrouter",
                "simulator_model": "openai/gpt-5.4-mini",
                "generation_mode": "teacher_user_simulator_openrouter_v1",
                "selected_jobs": 3,
                "completed_jobs": 3,
                "failed_jobs": [],
                "runtime": {"executed_batches": 1, "completed_batches": 1, "total_elapsed_ms": 1, "total_retry_attempts": 0},
            },
            "answering": {
                "teacher_provider": "openrouter",
                "teacher_model": "openai/gpt-5.4",
                "generation_mode": "teacher_answer_openrouter_v1",
                "selected_jobs": 3,
                "completed_jobs": 3,
                "failed_jobs": [],
                "runtime": {"executed_batches": 1, "completed_batches": 1, "total_elapsed_ms": 1, "total_retry_attempts": 0},
            },
            "judge": {
                "reviewer_provider": "openrouter",
                "reviewer_model": "openai/gpt-5.4",
                "generation_mode": "teacher_judge_openrouter_v1",
                "selected_jobs": 3,
                "completed_jobs": 3,
                "failed_jobs": [],
                "runtime": {"executed_batches": 1, "completed_batches": 1, "total_elapsed_ms": 1, "total_retry_attempts": 0},
            },
        },
        "paths": {
            "teacher_outputs": str(reviewed_outputs),
            "reviewed_outputs": str(reviewed_outputs),
            "judge_results": str(judge_results),
        },
        "benchmark": {
            "name": "judge-audit-demo",
            "role": benchmark_role,
            "profile_set": "support_mvp_demo",
        },
    }


def test_build_judge_audit_summary_selects_focus_and_disagreement_cases(tmp_path: Path) -> None:
    reference_reviewed = tmp_path / "reference_reviewed.jsonl"
    candidate_reviewed = tmp_path / "candidate_reviewed.jsonl"
    reference_judge = tmp_path / "reference_judge.jsonl"
    candidate_judge = tmp_path / "candidate_judge.jsonl"
    reference_report = tmp_path / "reference_report.json"
    candidate_report = tmp_path / "candidate_report.json"

    _write_jsonl(
        reference_reviewed,
        [
            _reviewed_output(
                "job-step",
                task_type="step_by_step",
                target_split="eval",
                review_status="rejected",
                answer_text="Codex step answer",
            ),
            _reviewed_output(
                "job-faq",
                task_type="faq_direct_answer",
                target_split="eval",
                review_status="codex_reviewed",
                answer_text="Codex faq answer",
            ),
            _reviewed_output(
                "job-trouble",
                task_type="troubleshooting",
                target_split="train",
                review_status="codex_reviewed",
                answer_text="Codex trouble answer",
                use_messages=True,
            ),
        ],
    )
    _write_jsonl(
        candidate_reviewed,
        [
            _reviewed_output(
                "job-step",
                task_type="step_by_step",
                target_split="eval",
                review_status="codex_reviewed",
                answer_text="OpenRouter step answer",
            ),
            _reviewed_output(
                "job-faq",
                task_type="faq_direct_answer",
                target_split="eval",
                review_status="codex_reviewed",
                answer_text="OpenRouter faq answer",
            ),
            _reviewed_output(
                "job-trouble",
                task_type="troubleshooting",
                target_split="train",
                review_status="codex_reviewed",
                answer_text="OpenRouter trouble answer",
                use_messages=True,
            ),
        ],
    )
    _write_jsonl(
        reference_judge,
        [
            _judge_result("job-step", task_type="step_by_step", target_split="eval", decision="reject", quality_score=60),
            _judge_result("job-faq", task_type="faq_direct_answer", target_split="eval", decision="approve", quality_score=85),
            _judge_result("job-trouble", task_type="troubleshooting", target_split="train", decision="approve", quality_score=90),
        ],
    )
    _write_jsonl(
        candidate_judge,
        [
            _judge_result("job-step", task_type="step_by_step", target_split="eval", decision="approve", quality_score=92),
            _judge_result("job-faq", task_type="faq_direct_answer", target_split="eval", decision="approve", quality_score=80),
            _judge_result("job-trouble", task_type="troubleshooting", target_split="train", decision="approve", quality_score=65),
        ],
    )

    reference_report.write_text(
        json.dumps(
            _pipeline_report(
                run_name="reference-run",
                reviewed_outputs=reference_reviewed,
                judge_results=reference_judge,
                benchmark_role="reference",
            )
        ),
        encoding="utf-8",
    )
    candidate_report.write_text(
        json.dumps(
            _pipeline_report(
                run_name="candidate-run",
                reviewed_outputs=candidate_reviewed,
                judge_results=candidate_judge,
                benchmark_role="candidate",
            )
        ),
        encoding="utf-8",
    )

    summary = judge_audit.build_judge_audit_summary(
        ROOT,
        reference_report,
        candidate_report,
        focus_task_types=["step_by_step", "faq_direct_answer"],
        score_delta_threshold=20,
    )

    assert summary["benchmark_name"] == "judge-audit-demo"
    assert summary["selected_case_count"] == 3
    assert summary["selection_tag_counts"]["focus_task_type:step_by_step"] == 1
    assert summary["selection_tag_counts"]["focus_task_type:faq_direct_answer"] == 1
    assert summary["selection_tag_counts"]["decision_disagreement"] == 1
    assert summary["selection_tag_counts"]["high_score_delta>=20"] == 2
    assert summary["decision_pair_counts"]["reject->approve"] == 1
    assert summary["decision_pair_counts"]["approve->approve"] == 2

    job_step = next(case for case in summary["cases"] if case["job_id"] == "job-step")
    assert "focus_task_type:step_by_step" in job_step["selection_tags"]
    assert "decision_disagreement" in job_step["selection_tags"]
    assert job_step["quality_score_delta"] == 32
    assert job_step["candidate"]["answer_text"] == "OpenRouter step answer"

    job_trouble = next(case for case in summary["cases"] if case["job_id"] == "job-trouble")
    assert job_trouble["candidate"]["answer_text"] == "OpenRouter trouble answer"
    assert "high_score_delta>=20" in job_trouble["selection_tags"]

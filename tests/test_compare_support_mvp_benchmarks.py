from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_support_mvp_benchmarks as benchmark_compare  # noqa: E402


def _source_record(job_id: str) -> dict[str, object]:
    return {
        "doc_id": "JAWS-DE-demo",
        "chunk_id": f"{job_id}-chunk",
        "normalized_path": "data/normalized/JAWS/DE/demo.md",
        "source_spans": ["1-2"],
    }


def _teacher_output(job_id: str, *, review_status: str) -> dict[str, object]:
    return {
        "output_id": f"run::{job_id}",
        "job_id": job_id,
        "record_type": "sft_sample",
        "target_split": "train",
        "product": "JAWS",
        "language": "DE",
        "task_type": "faq_direct_answer",
        "source_doc_ids": ["JAWS-DE-demo"],
        "source_chunk_ids": [f"{job_id}-chunk"],
        "teacher_provider": "openai",
        "teacher_model": "gpt-5.4",
        "teacher_run_id": "run-answer",
        "teacher_prompt_version": "jaws_de_support_answer_mvp_v1",
        "generation_mode": "teacher_answer_codex_cli_v1",
        "review_status": review_status,
        "approved_by": None,
        "promoted_to": None,
        "auto_review": None,
        "simulated_user": None,
        "raw_response_path": "data/derived/teacher_outputs/JAWS/DE/run_raw_responses.jsonl",
        "candidate": {
            "messages": [
                {"role": "user", "content": "Frage"},
                {"role": "assistant", "content": "Antwort"},
            ]
        },
        "provenance": {
            "transform_pipeline_version": "0.8.0",
            "source_job_path": "data/derived/teacher_jobs/JAWS/DE/demo.jsonl",
            "source_records": [_source_record(job_id)],
        },
    }


def _judge_result(job_id: str, *, decision: str, quality_score: int) -> dict[str, object]:
    return {
        "review_id": f"judge::{job_id}",
        "job_id": job_id,
        "output_id": f"run::{job_id}",
        "simulation_id": f"sim::{job_id}",
        "response_id": f"resp::{job_id}",
        "target_split": "train",
        "record_type": "sft_sample",
        "task_type": "faq_direct_answer",
        "product": "JAWS",
        "language": "DE",
        "source_doc_ids": ["JAWS-DE-demo"],
        "source_chunk_ids": [f"{job_id}-chunk"],
        "reviewer_provider": "openai",
        "reviewer_model": "gpt-5.4-mini",
        "reviewer_run_id": "run-judge",
        "reviewer_prompt_version": "jaws_de_support_judge_v1",
        "generation_mode": "teacher_judge_codex_cli_v1",
        "decision": decision,
        "quality_score": quality_score,
        "summary": "Kurzbegruendung",
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
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _pipeline_report(
    *,
    run_name: str,
    teacher_outputs: Path,
    reviewed_outputs: Path,
    judge_results: Path,
    profile_set: str,
    benchmark_role: str,
    answer_backend: str,
    answer_model: str,
    approved_jobs: int,
    rejected_jobs: int,
) -> dict[str, object]:
    return {
        "run_name": run_name,
        "llm_profile_set": profile_set,
        "llm_profiles": {
            "user_simulation": {
                "backend": answer_backend,
                "model": "gpt-5.4-mini",
                "profile_name": f"{answer_backend}_user_profile",
            },
            "answer": {
                "backend": answer_backend,
                "model": answer_model,
                "profile_name": f"{answer_backend}_answer_profile",
            },
            "judge": {
                "backend": answer_backend,
                "model": "gpt-5.4-mini",
                "profile_name": f"{answer_backend}_judge_profile",
            },
        },
        "defaults": {
            "user_simulation": {"backend": answer_backend, "model": "gpt-5.4-mini"},
            "answering": {"backend": answer_backend, "model": answer_model},
            "judge": {"backend": answer_backend, "model": "gpt-5.4-mini"},
        },
        "stages": {
            "user_simulation": {
                "simulator_provider": "openai",
                "simulator_model": "gpt-5.4-mini",
                "generation_mode": "teacher_user_simulator_codex_cli_v1",
                "selected_jobs": 2,
                "completed_jobs": 2,
                "failed_jobs": [],
                "runtime": {"executed_batches": 1, "completed_batches": 1, "total_elapsed_ms": 100, "total_retry_attempts": 0},
            },
            "answering": {
                "teacher_provider": "openai",
                "teacher_model": answer_model,
                "generation_mode": "teacher_answer_codex_cli_v1",
                "selected_jobs": 2,
                "completed_jobs": 2,
                "failed_jobs": [],
                "runtime": {"executed_batches": 1, "completed_batches": 1, "total_elapsed_ms": 200, "total_retry_attempts": 1},
            },
            "judge": {
                "reviewer_provider": "openai",
                "reviewer_model": "gpt-5.4-mini",
                "generation_mode": "teacher_judge_codex_cli_v1",
                "selected_jobs": 2,
                "completed_jobs": 2,
                "approved_jobs": approved_jobs,
                "rejected_jobs": rejected_jobs,
                "failed_jobs": [],
                "runtime": {"executed_batches": 1, "completed_batches": 1, "total_elapsed_ms": 150, "total_retry_attempts": 0},
            },
        },
        "paths": {
            "teacher_outputs": str(teacher_outputs),
            "reviewed_outputs": str(reviewed_outputs),
            "judge_results": str(judge_results),
        },
    }


def _pipeline_report_with_benchmark(**kwargs: object) -> dict[str, object]:
    report = _pipeline_report(**kwargs)
    report["benchmark"] = {
        "name": "jaws-de-shadow-apr-2026",
        "role": kwargs["benchmark_role"],
        "profile_set": kwargs["profile_set"],
    }
    return report


def test_build_benchmark_summary_compares_reference_and_candidate(tmp_path: Path) -> None:
    reference_teacher_outputs = tmp_path / "reference_teacher_outputs.jsonl"
    reference_reviewed_outputs = tmp_path / "reference_reviewed_teacher_outputs.jsonl"
    reference_judge_results = tmp_path / "reference_judge_results.jsonl"
    candidate_teacher_outputs = tmp_path / "candidate_teacher_outputs.jsonl"
    candidate_reviewed_outputs = tmp_path / "candidate_reviewed_teacher_outputs.jsonl"
    candidate_judge_results = tmp_path / "candidate_judge_results.jsonl"
    reference_report = tmp_path / "reference_pipeline_report.json"
    candidate_report = tmp_path / "candidate_pipeline_report.json"

    teacher_rows = [_teacher_output("job-1", review_status="teacher_generated"), _teacher_output("job-2", review_status="teacher_generated")]
    _write_jsonl(reference_teacher_outputs, teacher_rows)
    _write_jsonl(candidate_teacher_outputs, teacher_rows)
    _write_jsonl(
        reference_reviewed_outputs,
        [_teacher_output("job-1", review_status="codex_reviewed"), _teacher_output("job-2", review_status="rejected")],
    )
    _write_jsonl(
        candidate_reviewed_outputs,
        [_teacher_output("job-1", review_status="codex_reviewed"), _teacher_output("job-2", review_status="codex_reviewed")],
    )
    _write_jsonl(
        reference_judge_results,
        [_judge_result("job-1", decision="approve", quality_score=90), _judge_result("job-2", decision="reject", quality_score=60)],
    )
    _write_jsonl(
        candidate_judge_results,
        [_judge_result("job-1", decision="approve", quality_score=95), _judge_result("job-2", decision="approve", quality_score=85)],
    )
    reference_report.write_text(
        json.dumps(
            _pipeline_report_with_benchmark(
                run_name="reference-run",
                teacher_outputs=reference_teacher_outputs,
                reviewed_outputs=reference_reviewed_outputs,
                judge_results=reference_judge_results,
                profile_set="support_mvp_default",
                benchmark_role="reference",
                answer_backend="codex_cli",
                answer_model="gpt-5.4",
                approved_jobs=1,
                rejected_jobs=1,
            )
        ),
        encoding="utf-8",
    )
    candidate_report.write_text(
        json.dumps(
            _pipeline_report_with_benchmark(
                run_name="candidate-run",
                teacher_outputs=candidate_teacher_outputs,
                reviewed_outputs=candidate_reviewed_outputs,
                judge_results=candidate_judge_results,
                profile_set="support_mvp_openrouter_candidate",
                benchmark_role="candidate",
                answer_backend="openrouter",
                answer_model="openai/gpt-4.1",
                approved_jobs=2,
                rejected_jobs=0,
            )
        ),
        encoding="utf-8",
    )

    summary = benchmark_compare.build_benchmark_summary(ROOT, reference_report, candidate_report)

    assert summary["benchmark_name"] == "jaws-de-shadow-apr-2026"
    assert summary["reference"]["approval"]["approved_jobs"] == 1
    assert summary["candidate"]["approval"]["approved_jobs"] == 2
    assert summary["comparison"]["approved_jobs_delta"] == 1
    assert summary["comparison"]["approval_rate_delta"] == 0.5
    assert summary["comparison"]["average_quality_score_delta"] == 15.0
    assert summary["comparison"]["stages"]["answering"]["reference_backend"] == "codex_cli"
    assert summary["comparison"]["stages"]["answering"]["candidate_backend"] == "openrouter"
    assert summary["reference"]["artifacts"]["reviewed_outputs"]["schema"]["ok"] is True
    assert summary["candidate"]["artifacts"]["judge_results"]["schema"]["ok"] is True


def test_build_benchmark_summary_rejects_missing_benchmark_metadata(tmp_path: Path) -> None:
    teacher_outputs = tmp_path / "teacher_outputs.jsonl"
    reviewed_outputs = tmp_path / "reviewed_teacher_outputs.jsonl"
    judge_results = tmp_path / "judge_results.jsonl"
    report_path = tmp_path / "pipeline_report.json"

    _write_jsonl(teacher_outputs, [_teacher_output("job-1", review_status="teacher_generated")])
    _write_jsonl(reviewed_outputs, [_teacher_output("job-1", review_status="codex_reviewed")])
    _write_jsonl(judge_results, [_judge_result("job-1", decision="approve", quality_score=80)])
    report_path.write_text(
        json.dumps(
            _pipeline_report(
                run_name="legacy-run",
                teacher_outputs=teacher_outputs,
                reviewed_outputs=reviewed_outputs,
                judge_results=judge_results,
                profile_set="support_mvp_default",
                benchmark_role="reference",
                answer_backend="codex_cli",
                answer_model="gpt-5.4",
                approved_jobs=1,
                rejected_jobs=0,
            )
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as exc:
        benchmark_compare.build_benchmark_summary(ROOT, report_path, report_path)

    assert "missing benchmark metadata" in str(exc.value)


def test_build_benchmark_summary_rejects_mismatched_benchmark_names(tmp_path: Path) -> None:
    reference_report = tmp_path / "reference_pipeline_report.json"
    candidate_report = tmp_path / "candidate_pipeline_report.json"
    teacher_outputs = tmp_path / "teacher_outputs.jsonl"
    reviewed_outputs = tmp_path / "reviewed_teacher_outputs.jsonl"
    judge_results = tmp_path / "judge_results.jsonl"

    _write_jsonl(teacher_outputs, [_teacher_output("job-1", review_status="teacher_generated")])
    _write_jsonl(reviewed_outputs, [_teacher_output("job-1", review_status="codex_reviewed")])
    _write_jsonl(judge_results, [_judge_result("job-1", decision="approve", quality_score=80)])
    reference_payload = _pipeline_report_with_benchmark(
        run_name="reference-run",
        teacher_outputs=teacher_outputs,
        reviewed_outputs=reviewed_outputs,
        judge_results=judge_results,
        profile_set="support_mvp_default",
        benchmark_role="reference",
        answer_backend="codex_cli",
        answer_model="gpt-5.4",
        approved_jobs=1,
        rejected_jobs=0,
    )
    candidate_payload = _pipeline_report_with_benchmark(
        run_name="candidate-run",
        teacher_outputs=teacher_outputs,
        reviewed_outputs=reviewed_outputs,
        judge_results=judge_results,
        profile_set="support_mvp_openrouter_candidate",
        benchmark_role="candidate",
        answer_backend="openrouter",
        answer_model="openai/gpt-4.1",
        approved_jobs=1,
        rejected_jobs=0,
    )
    candidate_payload["benchmark"]["name"] = "other-benchmark"
    reference_report.write_text(json.dumps(reference_payload), encoding="utf-8")
    candidate_report.write_text(json.dumps(candidate_payload), encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        benchmark_compare.build_benchmark_summary(ROOT, reference_report, candidate_report)

    assert "Benchmark names do not match" in str(exc.value)


def test_build_benchmark_summary_rejects_empty_benchmark_name(tmp_path: Path) -> None:
    reference_report = tmp_path / "reference_pipeline_report.json"
    candidate_report = tmp_path / "candidate_pipeline_report.json"
    teacher_outputs = tmp_path / "teacher_outputs.jsonl"
    reviewed_outputs = tmp_path / "reviewed_teacher_outputs.jsonl"
    judge_results = tmp_path / "judge_results.jsonl"

    _write_jsonl(teacher_outputs, [_teacher_output("job-1", review_status="teacher_generated")])
    _write_jsonl(reviewed_outputs, [_teacher_output("job-1", review_status="codex_reviewed")])
    _write_jsonl(judge_results, [_judge_result("job-1", decision="approve", quality_score=80)])
    reference_payload = _pipeline_report_with_benchmark(
        run_name="reference-run",
        teacher_outputs=teacher_outputs,
        reviewed_outputs=reviewed_outputs,
        judge_results=judge_results,
        profile_set="support_mvp_default",
        benchmark_role="reference",
        answer_backend="codex_cli",
        answer_model="gpt-5.4",
        approved_jobs=1,
        rejected_jobs=0,
    )
    candidate_payload = _pipeline_report_with_benchmark(
        run_name="candidate-run",
        teacher_outputs=teacher_outputs,
        reviewed_outputs=reviewed_outputs,
        judge_results=judge_results,
        profile_set="support_mvp_openrouter_candidate",
        benchmark_role="candidate",
        answer_backend="openrouter",
        answer_model="openai/gpt-4.1",
        approved_jobs=1,
        rejected_jobs=0,
    )
    reference_payload["benchmark"]["name"] = "   "
    reference_report.write_text(json.dumps(reference_payload), encoding="utf-8")
    candidate_report.write_text(json.dumps(candidate_payload), encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        benchmark_compare.build_benchmark_summary(ROOT, reference_report, candidate_report)

    assert "missing benchmark.name" in str(exc.value)


def test_build_benchmark_summary_rejects_wrong_roles(tmp_path: Path) -> None:
    reference_report = tmp_path / "reference_pipeline_report.json"
    candidate_report = tmp_path / "candidate_pipeline_report.json"
    teacher_outputs = tmp_path / "teacher_outputs.jsonl"
    reviewed_outputs = tmp_path / "reviewed_teacher_outputs.jsonl"
    judge_results = tmp_path / "judge_results.jsonl"

    _write_jsonl(teacher_outputs, [_teacher_output("job-1", review_status="teacher_generated")])
    _write_jsonl(reviewed_outputs, [_teacher_output("job-1", review_status="codex_reviewed")])
    _write_jsonl(judge_results, [_judge_result("job-1", decision="approve", quality_score=80)])
    reference_payload = _pipeline_report_with_benchmark(
        run_name="reference-run",
        teacher_outputs=teacher_outputs,
        reviewed_outputs=reviewed_outputs,
        judge_results=judge_results,
        profile_set="support_mvp_default",
        benchmark_role="reference",
        answer_backend="codex_cli",
        answer_model="gpt-5.4",
        approved_jobs=1,
        rejected_jobs=0,
    )
    candidate_payload = _pipeline_report_with_benchmark(
        run_name="candidate-run",
        teacher_outputs=teacher_outputs,
        reviewed_outputs=reviewed_outputs,
        judge_results=judge_results,
        profile_set="support_mvp_openrouter_candidate",
        benchmark_role="reference",
        answer_backend="openrouter",
        answer_model="openai/gpt-4.1",
        approved_jobs=1,
        rejected_jobs=0,
    )
    reference_report.write_text(json.dumps(reference_payload), encoding="utf-8")
    candidate_report.write_text(json.dumps(candidate_payload), encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        benchmark_compare.build_benchmark_summary(ROOT, reference_report, candidate_report)

    assert "expected candidate" in str(exc.value)

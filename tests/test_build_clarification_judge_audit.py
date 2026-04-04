from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_clarification_judge_audit as clarification_audit  # noqa: E402


def _source_record(job_id: str) -> dict[str, object]:
    return {
        "doc_id": "JAWS-DE-demo",
        "chunk_id": f"{job_id}-chunk",
        "normalized_path": "data/normalized/JAWS/DE/demo.md",
        "source_spans": [f"{job_id}:1-2"],
    }


def _reviewed_output(job_id: str, answer_text: str) -> dict[str, object]:
    return {
        "output_id": f"run::{job_id}",
        "job_id": job_id,
        "record_type": "eval_case",
        "target_split": "eval",
        "product": "JAWS",
        "language": "de",
        "task_type": "clarification",
        "source_doc_ids": ["JAWS-DE-demo"],
        "source_chunk_ids": [f"{job_id}-chunk"],
        "teacher_provider": "openrouter",
        "teacher_model": "openai/gpt-5.4",
        "teacher_run_id": "run-answer",
        "teacher_prompt_version": "jaws_de_support_answer_mvp_v1",
        "generation_mode": "teacher_answer_openrouter_v1",
        "review_status": "codex_reviewed",
        "raw_response_path": "data/derived/teacher_outputs/JAWS/DE/run_raw_responses.jsonl",
        "candidate": {
            "messages": [
                {"role": "assistant", "content": answer_text},
            ]
        },
        "provenance": {
            "transform_pipeline_version": "0.8.0",
            "source_job_path": "data/derived/teacher_jobs/JAWS/DE/demo.jsonl",
            "source_records": [_source_record(job_id)],
        },
    }


def _judge_result(job_id: str, decision: str, quality_score: int, *, prompt_version: str) -> dict[str, object]:
    return {
        "review_id": f"judge::{job_id}",
        "job_id": job_id,
        "output_id": f"run::{job_id}",
        "simulation_id": f"sim::{job_id}",
        "response_id": f"resp::{job_id}",
        "target_split": "eval",
        "record_type": "eval_case",
        "task_type": "clarification",
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


def _pipeline_report(*, run_name: str, reviewed_outputs: Path, judge_results: Path) -> dict[str, object]:
    return {
        "run_name": run_name,
        "llm_profile_set": "support_mvp_demo",
        "defaults": {},
        "llm_profiles": {},
        "stages": {
            "user_simulation": {"selected_jobs": 2, "completed_jobs": 2, "failed_jobs": [], "runtime": {}},
            "answering": {"selected_jobs": 2, "completed_jobs": 2, "failed_jobs": [], "runtime": {}},
            "judge": {"selected_jobs": 2, "completed_jobs": 2, "failed_jobs": [], "runtime": {}},
        },
        "paths": {
            "teacher_outputs": str(reviewed_outputs),
            "reviewed_outputs": str(reviewed_outputs),
            "judge_results": str(judge_results),
        },
        "benchmark": {
            "name": "clarification-audit-demo",
            "role": "candidate",
            "profile_set": "support_mvp_demo",
        },
    }


def test_build_clarification_judge_audit_tracks_v3_outlier_and_supplemental_run(tmp_path: Path) -> None:
    job_stable = "job-clarify-stable"
    job_outlier = "job-clarify-outlier"
    report_paths: dict[str, Path] = {}

    run_specs = {
        "codex": {
            "answers": {job_stable: "Codex stable", job_outlier: "Codex outlier"},
            "judges": {
                job_stable: ("approve", 95, "jaws_de_support_judge_v1"),
                job_outlier: ("approve", 93, "jaws_de_support_judge_v1"),
            },
        },
        "openrouter_v1": {
            "answers": {job_stable: "Candidate stable", job_outlier: "Candidate outlier"},
            "judges": {
                job_stable: ("approve", 94, "jaws_de_support_judge_v1"),
                job_outlier: ("approve", 88, "jaws_de_support_judge_v1"),
            },
        },
        "openrouter_v2": {
            "answers": {job_stable: "Candidate stable", job_outlier: "Candidate outlier"},
            "judges": {
                job_stable: ("approve", 95, "jaws_de_support_judge_v2"),
                job_outlier: ("approve", 92, "jaws_de_support_judge_v2"),
            },
        },
        "openrouter_v3": {
            "answers": {job_stable: "Candidate stable", job_outlier: "Candidate outlier"},
            "judges": {
                job_stable: ("approve", 95, "jaws_de_support_judge_v3"),
                job_outlier: ("reject", 41, "jaws_de_support_judge_v3"),
            },
        },
        "supplemental": {
            "answers": {job_outlier: "Candidate outlier"},
            "judges": {
                job_outlier: ("approve", 88, "jaws_de_support_judge_v1"),
            },
        },
    }

    for run_key, spec in run_specs.items():
        reviewed_path = tmp_path / f"{run_key}_reviewed.jsonl"
        judge_path = tmp_path / f"{run_key}_judge.jsonl"
        report_path = tmp_path / f"{run_key}_report.json"
        _write_jsonl(
            reviewed_path,
            [_reviewed_output(job_id, answer) for job_id, answer in spec["answers"].items()],
        )
        _write_jsonl(
            judge_path,
            [
                _judge_result(job_id, decision, score, prompt_version=prompt_version)
                for job_id, (decision, score, prompt_version) in spec["judges"].items()
            ],
        )
        report_path.write_text(
            json.dumps(
                _pipeline_report(
                    run_name=run_key,
                    reviewed_outputs=reviewed_path,
                    judge_results=judge_path,
                )
            ),
            encoding="utf-8",
        )
        report_paths[run_key] = report_path

    summary = clarification_audit.build_clarification_judge_audit(
        ROOT,
        codex_report_path=report_paths["codex"],
        openrouter_v1_report_path=report_paths["openrouter_v1"],
        openrouter_v2_report_path=report_paths["openrouter_v2"],
        openrouter_v3_report_path=report_paths["openrouter_v3"],
        supplemental_report_paths=[report_paths["supplemental"]],
    )

    assert summary["selected_case_count"] == 2
    assert summary["mismatch_counts_vs_codex"] == {
        "openrouter_v1": 0,
        "openrouter_v2": 0,
        "openrouter_v3": 1,
    }
    assert summary["classification_hint_counts"] == {
        "stable_alignment": 1,
        "v3_outlier": 1,
    }

    cases_by_job = {case["job_id"]: case for case in summary["cases"]}
    assert cases_by_job[job_stable]["classification_hint"] == "stable_alignment"
    assert cases_by_job[job_outlier]["classification_hint"] == "v3_outlier"
    assert cases_by_job[job_outlier]["judges"]["openrouter_v3"]["decision"] == "reject"
    assert cases_by_job[job_outlier]["supplemental_runs"][0]["judge"]["decision"] == "approve"

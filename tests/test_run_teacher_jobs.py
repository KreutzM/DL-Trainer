from __future__ import annotations

from argparse import Namespace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_teacher_jobs  # noqa: E402


def _job() -> dict:
    return {
        "job_id": "job-1",
        "wave_id": "wave-1",
        "expected_output_kind": "sft_sample",
        "target_split": "train",
        "product": "JAWS",
        "language": "de",
        "task_type": "faq_direct_answer",
        "source_doc_ids": ["doc-1"],
        "source_chunk_ids": ["chunk-1"],
        "teacher_prompt_version": "prompt-v1",
        "behavior_spec_path": "docs/support_behavior_spec.md",
        "prompt_template_path": "prompts/teacher/jaws_de_direct_support.md",
        "runner_input": {
            "system_message": "Arbeite dokumentationsgebunden.",
            "user_message": "Wie aktiviere ich X?",
        },
        "provenance": {
            "source_records": [
                {
                    "doc_id": "doc-1",
                    "chunk_id": "chunk-1",
                    "normalized_path": "data/normalized/JAWS/DE/doc/index.md",
                    "source_spans": ["data/normalized/JAWS/DE/doc/index.md#L1-L3"],
                }
            ]
        },
        "fixture_payload": {"assistant_message": "Belegte Antwort"},
    }


def _raw_response() -> dict:
    return {
        "response_id": "run-1::job-1::response",
        "job_id": "job-1",
        "output_id": "run-1::job-1",
        "wave_id": "wave-1",
        "record_type": "sft_sample",
        "target_split": "train",
        "product": "JAWS",
        "language": "de",
        "task_type": "faq_direct_answer",
        "source_doc_ids": ["doc-1"],
        "source_chunk_ids": ["chunk-1"],
        "teacher_provider": "openrouter",
        "teacher_model": "openrouter/test-model",
        "teacher_run_id": "run-1",
        "teacher_prompt_version": "prompt-v1",
        "generation_mode": "teacher_runner_openrouter_chat_json_v1",
        "response_status": "completed",
        "response_format_version": run_teacher_jobs.RAW_RESPONSE_FORMAT_VERSION,
        "provider_response_id": "or-1",
        "raw_text": "{\"answer\":\"Belegte Antwort\"}",
        "parsed_response": {
            "answer": "Belegte Antwort",
            "task_type": "faq_direct_answer",
            "needs_clarification": False,
            "clarification_question": None,
            "escalate": False,
            "uncertainty_reason": None,
            "steps": [],
            "source_chunk_ids": ["chunk-1"],
            "notes": [],
        },
        "provenance": {
            "transform_pipeline_version": "0.7.0",
            "source_job_path": "data/derived/teacher_jobs/demo.jsonl",
            "behavior_spec_path": "docs/support_behavior_spec.md",
            "prompt_template_path": "prompts/teacher/jaws_de_direct_support.md",
            "source_records": [
                {
                    "doc_id": "doc-1",
                    "chunk_id": "chunk-1",
                    "normalized_path": "data/normalized/JAWS/DE/doc/index.md",
                    "source_spans": ["data/normalized/JAWS/DE/doc/index.md#L1-L3"],
                }
            ],
        },
        "openrouter": {"response_path": "tmp/openrouter/response.json"},
    }


def test_generated_or_imported_raw_row_modes_include_openrouter() -> None:
    assert run_teacher_jobs.mode_uses_generated_or_imported_raw_rows("codex") is True
    assert run_teacher_jobs.mode_uses_generated_or_imported_raw_rows("import") is True
    assert run_teacher_jobs.mode_uses_generated_or_imported_raw_rows("openai") is True
    assert run_teacher_jobs.mode_uses_generated_or_imported_raw_rows("openrouter") is True
    assert run_teacher_jobs.mode_uses_generated_or_imported_raw_rows("stub") is False
    assert run_teacher_jobs.mode_uses_generated_or_imported_raw_rows("replay") is False


def test_main_materializes_openrouter_raw_rows(monkeypatch, tmp_path: Path) -> None:
    jobs_path = tmp_path / "jobs.jsonl"
    output_path = tmp_path / "outputs.jsonl"
    raw_output_path = tmp_path / "raw.jsonl"

    args = Namespace(
        jobs=str(jobs_path),
        output=str(output_path),
        mode="openrouter",
        teacher_model="openrouter/test-model",
        teacher_provider="local",
        teacher_run_id="run-1",
        replay_input=None,
        import_input=None,
        raw_output=str(raw_output_path),
        artifact_dir=str(tmp_path / "artifacts"),
        api_key_env="OPENROUTER_API_KEY",
        api_base="https://openrouter.ai/api/v1",
        request_timeout_sec=30,
        job_id=[],
        job_ids_file=[],
        limit=None,
    )

    written: dict[str, list[dict]] = {}

    monkeypatch.setattr(run_teacher_jobs, "parse_args", lambda: args)
    monkeypatch.setattr(run_teacher_jobs, "find_repo_root", lambda _: tmp_path)
    monkeypatch.setattr(run_teacher_jobs, "load_jobs", lambda path: [_job()])
    monkeypatch.setattr(run_teacher_jobs, "filter_jobs", lambda jobs, explicit_job_ids, job_ids_files, limit: jobs)
    monkeypatch.setattr(
        run_teacher_jobs,
        "generate_raw_responses_via_llm",
        lambda jobs, jobs_path, backend_name, artifact_root, api_base, api_key_env, teacher_model, teacher_run_id, timeout_sec: [_raw_response()],
    )
    monkeypatch.setattr(
        run_teacher_jobs,
        "write_jsonl",
        lambda path, rows: written.__setitem__(str(path), list(rows)),
    )

    run_teacher_jobs.main()

    assert str(raw_output_path) in written
    assert str(output_path) in written
    output_row = written[str(output_path)][0]
    assert output_row["teacher_provider"] == "openrouter"
    assert output_row["generation_mode"] == "teacher_runner_openrouter_chat_json_v1"
    assert output_row["candidate"]["teacher_provider"] == "openrouter"
    assert output_row["candidate"]["generation_mode"] == "teacher_runner_openrouter_chat_json_v1"

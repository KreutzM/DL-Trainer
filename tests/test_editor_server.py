from pathlib import Path
import sys
import tempfile
import json


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import editor_server  # noqa: E402


def _write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    return path


def _teacher_output_rows() -> list[dict]:
    return [
        {
            "output_id": "out-1",
            "job_id": "job-1",
            "record_type": "sft_sample",
            "target_split": "train",
            "product": "JAWS",
            "language": "de",
            "task_type": "faq_direct_answer",
            "source_doc_ids": ["doc-1"],
            "source_chunk_ids": ["chunk-1"],
            "teacher_provider": "codex_cli",
            "teacher_model": "gpt-5.4",
            "teacher_run_id": "run-1",
            "teacher_prompt_version": "prompt-v1",
            "generation_mode": "teacher_runner_codex_cli_v1",
            "review_status": "teacher_generated",
            "approved_by": None,
            "quality_score": 80,
            "selection_reason": "demo",
            "raw_response_path": "data/derived/teacher_outputs/JAWS/DE/demo_raw_responses.jsonl",
            "candidate": {
                "id": "out-1__candidate",
                "product": "JAWS",
                "language": "de",
                "task_type": "faq_direct_answer",
                "messages": [
                    {"role": "system", "content": "System"},
                    {"role": "user", "content": "Wie geht das?"},
                    {"role": "assistant", "content": "So geht das."},
                ],
                "source_doc_ids": ["doc-1"],
                "source_chunk_ids": ["chunk-1"],
                "teacher_provider": "codex_cli",
                "teacher_model": "gpt-5.4",
                "teacher_run_id": "run-1",
                "teacher_prompt_version": "prompt-v1",
                "generation_mode": "teacher_runner_codex_cli_v1",
                "review_status": "teacher_generated",
                "split": "train",
                "approved_by": None,
                "promoted_from": None,
                "provenance": {
                    "transform_pipeline_version": "0.1.0",
                    "source_records": [
                        {
                            "doc_id": "doc-1",
                            "chunk_id": "chunk-1",
                            "normalized_path": "data/normalized/x.md",
                            "source_spans": ["data/normalized/x.md#L1-L2"],
                        }
                    ],
                },
                "meta": {
                    "product": "JAWS",
                    "language": "de",
                    "task_type": "faq_direct_answer",
                    "teacher_provider": "codex_cli",
                    "teacher_model": "gpt-5.4",
                    "teacher_run_id": "run-1",
                    "source_doc_ids": ["doc-1"],
                    "source_chunk_ids": ["chunk-1"],
                    "teacher_prompt_version": "prompt-v1",
                    "generation_mode": "teacher_runner_codex_cli_v1",
                    "needs_clarification": False,
                    "review_status": "teacher_generated",
                    "split": "train",
                    "approved_by": None,
                    "promoted_from": None,
                    "provenance": {
                        "transform_pipeline_version": "0.1.0",
                        "source_records": [
                            {
                                "doc_id": "doc-1",
                                "chunk_id": "chunk-1",
                                "normalized_path": "data/normalized/x.md",
                                "source_spans": ["data/normalized/x.md#L1-L2"],
                            }
                        ],
                    },
                },
            },
            "provenance": {
                "transform_pipeline_version": "0.1.0",
                "source_job_path": "data/derived/teacher_jobs/x.jsonl",
                "source_records": [
                    {
                        "doc_id": "doc-1",
                        "chunk_id": "chunk-1",
                        "normalized_path": "data/normalized/x.md",
                        "source_spans": ["data/normalized/x.md#L1-L2"],
                    }
                ],
            },
        }
    ]


def _reviewed_teacher_output_rows() -> list[dict]:
    rows = _teacher_output_rows()
    row = rows[0]
    row["review_status"] = "human_reviewed"
    row["approved_by"] = "reviewer-x"
    row["candidate"]["review_status"] = "human_reviewed"
    row["candidate"]["approved_by"] = "reviewer-x"
    row["candidate"]["meta"]["review_status"] = "human_reviewed"
    row["candidate"]["meta"]["approved_by"] = "reviewer-x"

    rows.append(
        {
            "output_id": "out-2",
            "job_id": "job-2",
            "record_type": "eval_case",
            "target_split": "eval",
            "product": "JAWS",
            "language": "de",
            "task_type": "faq_direct_answer",
            "source_doc_ids": ["doc-2"],
            "source_chunk_ids": ["chunk-2"],
            "teacher_provider": "codex_cli",
            "teacher_model": "gpt-5.4",
            "teacher_run_id": "run-1",
            "teacher_prompt_version": "prompt-v1",
            "generation_mode": "teacher_runner_codex_cli_v1",
            "review_status": "human_reviewed",
            "approved_by": "reviewer-x",
            "quality_score": 85,
            "selection_reason": "demo",
            "raw_response_path": "data/derived/teacher_outputs/JAWS/DE/demo_raw_responses.jsonl",
            "candidate": {
                "eval_id": "out-2__candidate",
                "product": "JAWS",
                "language": "de",
                "case_type": "faq_direct_answer",
                "prompt": "Was ist das?",
                "case_description": "Kurze Direktantwort.",
                "expected_behavior": "Antwortet knapp.",
                "source_doc_ids": ["doc-2"],
                "source_chunk_ids": ["chunk-2"],
                "teacher_provider": "codex_cli",
                "teacher_model": "gpt-5.4",
                "teacher_run_id": "run-1",
                "teacher_prompt_version": "prompt-v1",
                "generation_mode": "teacher_runner_codex_cli_v1",
                "review_status": "human_reviewed",
                "split": "eval",
                "approved_by": "reviewer-x",
                "promoted_from": None,
                "reference_answer": "Das ist die Antwort.",
                "rubric": {
                    "must_include": [],
                    "must_not_include": [],
                    "style": "kurz",
                    "scoring_notes": "",
                },
                "provenance": {
                    "transform_pipeline_version": "0.1.0",
                    "source_records": [
                        {
                            "doc_id": "doc-2",
                            "chunk_id": "chunk-2",
                            "normalized_path": "data/normalized/y.md",
                            "source_spans": ["data/normalized/y.md#L1-L2"],
                        }
                    ],
                },
            },
            "provenance": {
                "transform_pipeline_version": "0.1.0",
                "source_job_path": "data/derived/teacher_jobs/y.jsonl",
                "source_records": [
                    {
                        "doc_id": "doc-2",
                        "chunk_id": "chunk-2",
                        "normalized_path": "data/normalized/y.md",
                        "source_spans": ["data/normalized/y.md#L1-L2"],
                    }
                ],
            },
        }
    )
    return rows


def _repo_temp_dir():
    base = ROOT / "tmp" / "pytest_editor_server"
    base.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=base)


def test_file_class_for_paths():
    reviewed = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_reviewed_teacher_outputs.jsonl"
    gold = ROOT / "data" / "gold" / "train" / "sft" / "JAWS" / "DE" / "demo_sft_samples.jsonl"
    raw = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_raw_responses.jsonl"

    assert editor_server.file_class_for_path(reviewed).category == "reviewed_teacher_outputs"
    assert editor_server.file_class_for_path(reviewed).editable is True
    assert editor_server.file_class_for_path(gold).category == "gold_train"
    assert editor_server.file_class_for_path(gold).editable is True
    assert editor_server.file_class_for_path(raw).editable is False


def test_normalize_row_for_save_updates_nested_status_fields():
    row = {
        "output_id": "out-1",
        "review_status": "human_reviewed",
        "approved_by": "tester",
        "candidate": {
            "review_status": "teacher_generated",
            "approved_by": None,
            "meta": {
                "review_status": "teacher_generated",
                "approved_by": None,
            },
        },
    }

    normalized = editor_server.normalize_row_for_save(row)

    assert normalized["candidate"]["review_status"] == "human_reviewed"
    assert normalized["candidate"]["approved_by"] == "tester"
    assert normalized["candidate"]["meta"]["review_status"] == "human_reviewed"
    assert normalized["candidate"]["meta"]["approved_by"] == "tester"


def test_validate_rows_rejects_empty_gold_file():
    path = ROOT / "data" / "gold" / "eval" / "JAWS" / "DE" / "demo_eval_cases.jsonl"
    errors = editor_server.validate_rows(path, [], "eval_case.schema.json")

    assert errors == [f"{editor_server.repo_relative_posix(path)} is empty"]


def test_suggested_review_output_path_for_teacher_outputs():
    source = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_teacher_outputs.jsonl"
    assert (
        editor_server.suggested_review_output_path(source)
        == "data/derived/teacher_outputs/JAWS/DE/demo_reviewed_teacher_outputs.jsonl"
    )


def test_validate_review_export_requires_decision_and_reviewed_target():
    source = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_teacher_outputs.jsonl"
    output = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_reviewed_teacher_outputs.jsonl"
    info = editor_server.file_class_for_path(source)
    rows = [
        {
            "output_id": "out-1",
            "job_id": "job-1",
            "record_type": "eval_case",
            "target_split": "eval",
            "product": "JAWS",
            "language": "de",
            "task_type": "faq_direct_answer",
            "source_doc_ids": ["doc-1"],
            "source_chunk_ids": ["chunk-1"],
            "teacher_model": "teacher-x",
            "teacher_run_id": "run-1",
            "teacher_prompt_version": "prompt-v1",
            "generation_mode": "mode-x",
            "review_status": "teacher_generated",
            "approved_by": None,
            "candidate": {
                "eval_id": "eval-1",
                "product": "JAWS",
                "language": "de",
                "case_type": "faq_direct_answer",
                "prompt": "Wie geht das?",
                "expected_behavior": "Antworten.",
                "source_doc_ids": ["doc-1"],
                "source_chunk_ids": ["chunk-1"],
                "teacher_model": "teacher-x",
                "teacher_run_id": "run-1",
                "teacher_prompt_version": "prompt-v1",
                "generation_mode": "mode-x",
                "review_status": "teacher_generated",
                "split": "eval",
                "provenance": {
                    "transform_pipeline_version": "0.1.0",
                    "source_records": [
                        {
                            "doc_id": "doc-1",
                            "chunk_id": "chunk-1",
                            "normalized_path": "data/normalized/x.md",
                            "source_spans": ["data/normalized/x.md#L1-L2"],
                        }
                    ],
                },
                "rubric": {"must_include": [], "must_not_include": [], "style": "kurz"},
            },
            "provenance": {
                "source_job_path": "data/derived/teacher_jobs/x.jsonl",
                "transform_pipeline_version": "0.1.0",
                "source_records": [
                    {
                        "doc_id": "doc-1",
                        "chunk_id": "chunk-1",
                        "normalized_path": "data/normalized/x.md",
                        "source_spans": ["data/normalized/x.md#L1-L2"],
                    }
                ],
            },
        }
    ]

    errors = editor_server.validate_review_export(source, output, rows, info)

    assert "No review decisions found; set at least one row to human_reviewed or rejected." in errors


def test_load_jsonl_payload_exposes_review_context():
    with _repo_temp_dir() as tmpdir:
        base = Path(tmpdir)
        path = _write_jsonl(
            base / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_teacher_outputs.jsonl",
            _teacher_output_rows(),
        )
        reviewed_path = _write_jsonl(
            base / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_reviewed_teacher_outputs.jsonl",
            _reviewed_teacher_output_rows(),
        )
        target_path = ROOT / path.relative_to(base)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        target_reviewed = ROOT / reviewed_path.relative_to(base)
        target_reviewed.parent.mkdir(parents=True, exist_ok=True)
        target_reviewed.write_text(reviewed_path.read_text(encoding="utf-8"), encoding="utf-8")
        try:
            payload = editor_server.load_jsonl_payload(target_path)
        finally:
            target_path.unlink(missing_ok=True)
            target_reviewed.unlink(missing_ok=True)

    assert payload["review"]["enabled"] is True
    assert payload["review"]["default_status_filter"] == "teacher_generated"
    assert payload["review"]["pending_count"] > 0
    assert payload["review"]["existing_output_exists"] is True
    assert payload["review"]["existing_output_path"].endswith("demo_reviewed_teacher_outputs.jsonl")
    assert payload["review"]["existing_merge_summary"]["mergeable_count"] > 0


def test_suggested_gold_output_paths_for_reviewed_outputs():
    source = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_reviewed_teacher_outputs.jsonl"
    suggested = editor_server.suggested_gold_output_paths(source)

    assert suggested["train_output_path"] == "data/gold/train/sft/JAWS/DE/promoted_demo_sft_samples.jsonl"
    assert suggested["eval_output_path"] == "data/gold/eval/JAWS/DE/promoted_demo_eval_cases.jsonl"


def test_load_jsonl_payload_exposes_promotion_context():
    with _repo_temp_dir() as tmpdir:
        base = Path(tmpdir)
        path = _write_jsonl(
            base / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_reviewed_teacher_outputs.jsonl",
            _reviewed_teacher_output_rows(),
        )
        target_path = ROOT / path.relative_to(base)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        try:
            payload = editor_server.load_jsonl_payload(target_path)
        finally:
            target_path.unlink(missing_ok=True)

    assert payload["promotion"]["enabled"] is True
    assert payload["promotion"]["eligible_count"] > 0
    assert payload["promotion"]["train_output_path"].endswith("_sft_samples.jsonl")
    assert payload["promotion"]["eval_output_path"].endswith("_eval_cases.jsonl")


def test_validate_promotion_export_accepts_real_reviewed_file():
    path = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_reviewed_teacher_outputs.jsonl"
    info = editor_server.file_class_for_path(path)
    rows = _reviewed_teacher_output_rows()
    suggested = editor_server.suggested_gold_output_paths(path)
    train_output = ROOT / suggested["train_output_path"]
    eval_output = ROOT / suggested["eval_output_path"]

    errors, train_rows, eval_rows = editor_server.validate_promotion_export(path, train_output, eval_output, rows, info)

    assert errors == []
    assert len(train_rows) > 0
    assert len(eval_rows) > 0


def test_summarize_review_merge_reports_conflicts_and_missing():
    source_rows = [
        {
            "output_id": "out-1",
            "job_id": "job-1",
            "record_type": "eval_case",
            "target_split": "eval",
            "task_type": "faq_direct_answer",
            "source_doc_ids": ["doc-1"],
            "source_chunk_ids": ["chunk-1"],
            "candidate": {"eval_id": "eval-1", "source_doc_ids": ["doc-1"], "source_chunk_ids": ["chunk-1"]},
        },
        {
            "output_id": "out-2",
            "job_id": "job-2",
            "record_type": "eval_case",
            "target_split": "eval",
            "task_type": "faq_direct_answer",
            "source_doc_ids": ["doc-2"],
            "source_chunk_ids": ["chunk-2"],
            "candidate": {"eval_id": "eval-2", "source_doc_ids": ["doc-2"], "source_chunk_ids": ["chunk-2"]},
        },
    ]
    reviewed_rows = [
        {
            "output_id": "out-1",
            "job_id": "job-1",
            "record_type": "eval_case",
            "target_split": "eval",
            "task_type": "faq_direct_answer",
            "source_doc_ids": ["doc-1"],
            "source_chunk_ids": ["chunk-1-modified"],
            "candidate": {"eval_id": "eval-1", "source_doc_ids": ["doc-1"], "source_chunk_ids": ["chunk-1-modified"]},
        },
        {
            "output_id": "out-3",
            "job_id": "job-3",
            "record_type": "eval_case",
            "target_split": "eval",
            "task_type": "faq_direct_answer",
            "source_doc_ids": ["doc-3"],
            "source_chunk_ids": ["chunk-3"],
            "candidate": {"eval_id": "eval-3", "source_doc_ids": ["doc-3"], "source_chunk_ids": ["chunk-3"]},
        },
    ]

    summary = editor_server.summarize_review_merge(source_rows, reviewed_rows)

    assert summary["missing_count"] == 1
    assert summary["extra_count"] == 1
    assert summary["conflict_count"] == 1


def test_merge_reviewed_overlay_skips_conflicts():
    source_rows = [
        {
            "output_id": "out-1",
            "job_id": "job-1",
            "record_type": "eval_case",
            "target_split": "eval",
            "task_type": "faq_direct_answer",
            "source_doc_ids": ["doc-1"],
            "source_chunk_ids": ["chunk-1"],
            "review_status": "teacher_generated",
            "approved_by": None,
            "candidate": {
                "eval_id": "eval-1",
                "source_doc_ids": ["doc-1"],
                "source_chunk_ids": ["chunk-1"],
                "review_status": "teacher_generated",
                "prompt": "Original",
            },
        }
    ]
    reviewed_rows = [
        {
            "output_id": "out-1",
            "job_id": "job-1",
            "record_type": "eval_case",
            "target_split": "eval",
            "task_type": "faq_direct_answer",
            "source_doc_ids": ["doc-1"],
            "source_chunk_ids": ["chunk-1-modified"],
            "review_status": "human_reviewed",
            "approved_by": "reviewer-x",
            "candidate": {
                "eval_id": "eval-1",
                "source_doc_ids": ["doc-1"],
                "source_chunk_ids": ["chunk-1-modified"],
                "review_status": "human_reviewed",
                "prompt": "Edited",
            },
        }
    ]

    merged_rows, summary = editor_server.merge_reviewed_overlay(source_rows, reviewed_rows)

    assert summary["conflict_count"] == 1
    assert summary["merged_count"] == 0
    assert merged_rows[0]["review_status"] == "teacher_generated"


def test_gold_post_checks_reports_success():
    reviewed_source = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "demo_reviewed_teacher_outputs.jsonl"
    train_rows, _ = editor_server.build_promoted_rows(editor_server.repo_relative_posix(reviewed_source), _reviewed_teacher_output_rows())
    path = ROOT / "data" / "gold" / "train" / "sft" / "JAWS" / "DE" / "promoted_demo_sft_samples.jsonl"
    checks = editor_server.gold_post_checks(path, train_rows, "sft_sample.schema.json")

    assert checks["schema_ok"] is True
    assert checks["provenance_ok"] is True

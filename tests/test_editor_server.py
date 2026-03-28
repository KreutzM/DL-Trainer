from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import editor_server  # noqa: E402


def test_file_class_for_paths():
    reviewed = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "wave1_reviewed_teacher_outputs.jsonl"
    gold = ROOT / "data" / "gold" / "train" / "sft" / "JAWS" / "DE" / "consolidated_gold_v1_sft_samples.jsonl"
    raw = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "wave1_codex_gpt54_raw_responses.jsonl"

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
    path = ROOT / "data" / "gold" / "eval" / "JAWS" / "DE" / "promoted_teacher_wave2_codex_gpt54_topoff_eval_cases.jsonl"
    errors = editor_server.validate_rows(path, [], "eval_case.schema.json")

    assert errors == [f"{editor_server.repo_relative_posix(path)} is empty"]


def test_suggested_review_output_path_for_teacher_outputs():
    source = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "wave1_teacher_outputs.jsonl"
    assert (
        editor_server.suggested_review_output_path(source)
        == "data/derived/teacher_outputs/JAWS/DE/wave1_reviewed_teacher_outputs.jsonl"
    )


def test_validate_review_export_requires_decision_and_reviewed_target():
    source = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "wave1_teacher_outputs.jsonl"
    output = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "wave1_reviewed_teacher_outputs.jsonl"
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
    path = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "wave1_teacher_outputs.jsonl"
    payload = editor_server.load_jsonl_payload(path)

    assert payload["review"]["enabled"] is True
    assert payload["review"]["default_status_filter"] == "teacher_generated"
    assert payload["review"]["pending_count"] > 0
    assert payload["review"]["existing_output_exists"] is True
    assert payload["review"]["existing_output_path"].endswith("wave1_reviewed_teacher_outputs.jsonl")
    assert payload["review"]["existing_merge_summary"]["mergeable_count"] > 0


def test_suggested_gold_output_paths_for_reviewed_outputs():
    source = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "wave1_reviewed_teacher_outputs.jsonl"
    suggested = editor_server.suggested_gold_output_paths(source)

    assert suggested["train_output_path"] == "data/gold/train/sft/JAWS/DE/promoted_wave1_sft_samples.jsonl"
    assert suggested["eval_output_path"] == "data/gold/eval/JAWS/DE/promoted_wave1_eval_cases.jsonl"


def test_load_jsonl_payload_exposes_promotion_context():
    path = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "wave1_reviewed_teacher_outputs.jsonl"
    payload = editor_server.load_jsonl_payload(path)

    assert payload["promotion"]["enabled"] is True
    assert payload["promotion"]["eligible_count"] > 0
    assert payload["promotion"]["train_output_path"].endswith("_sft_samples.jsonl")
    assert payload["promotion"]["eval_output_path"].endswith("_eval_cases.jsonl")


def test_validate_promotion_export_accepts_real_reviewed_file():
    path = ROOT / "data" / "derived" / "teacher_outputs" / "JAWS" / "DE" / "wave1_reviewed_teacher_outputs.jsonl"
    info = editor_server.file_class_for_path(path)
    rows = editor_server.read_jsonl(path)
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
    path = ROOT / "data" / "gold" / "train" / "sft" / "JAWS" / "DE" / "consolidated_gold_v1_sft_samples.jsonl"
    rows = editor_server.read_jsonl(path)
    checks = editor_server.gold_post_checks(path, rows[:2], "sft_sample.schema.json")

    assert checks["schema_ok"] is True
    assert checks["provenance_ok"] is True

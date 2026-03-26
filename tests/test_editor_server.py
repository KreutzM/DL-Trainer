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

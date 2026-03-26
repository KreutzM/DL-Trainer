from pathlib import Path


def test_expected_paths_exist():
    root = Path(__file__).resolve().parents[1]
    for rel in [
        "schemas/chunk.schema.json",
        "schemas/sft_sample.schema.json",
        "schemas/qwen_sft_record.schema.json",
        "scripts/validate_jsonl.py",
        "scripts/export_qwen_sft.py",
        "scripts/build_jaws_teacher_wave.py",
        "scripts/build_wave1_gpt54_subset.py",
        "scripts/select_teacher_wave_review_ids.py",
        "scripts/validate_teacher_responses.py",
        "scripts/smoke_test_qwen_sft.py",
        "scripts/audit_qwen_source_faithfulness.py",
        "scripts/run_qwen_clean_gate.py",
        "prompts/teacher/support_answer.md",
        "training/ms-swift/qwen3_8b_jaws_de_lora.yaml",
        "training/ms-swift/qwen3_8b_jaws_de_lora_clean.yaml",
        "training/ms-swift/qwen3_8b_jaws_de_lora_clean_dry_run.yaml",
        ".codex/config.toml",
        "AGENTS.md",
    ]:
        assert (root / rel).exists()

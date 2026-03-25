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
        "scripts/select_teacher_wave_review_ids.py",
        "scripts/smoke_test_qwen_sft.py",
        "prompts/teacher/support_answer.md",
        "training/ms-swift/qwen3_8b_jaws_de_lora.yaml",
        ".codex/config.toml",
        "AGENTS.md",
    ]:
        assert (root / rel).exists()

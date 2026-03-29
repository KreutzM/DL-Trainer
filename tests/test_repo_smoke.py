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
        "scripts/run_codex_cli_teacher_batch.py",
        "prompts/teacher/support_answer.md",
        "data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_raw_responses.jsonl",
        "data/gold/train/sft/JAWS/DE/codex_cli_smoke_v1_promoted_sft_samples.jsonl",
        ".codex/config.toml",
        "AGENTS.md",
    ]:
        assert (root / rel).exists()

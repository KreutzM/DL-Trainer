from pathlib import Path

def test_expected_paths_exist():
    root = Path(__file__).resolve().parents[1]
    for rel in [
        "schemas/chunk.schema.json",
        "schemas/sft_sample.schema.json",
        "scripts/validate_jsonl.py",
        "prompts/teacher/support_answer.md",
        ".codex/config.toml",
        "AGENTS.md",
    ]:
        assert (root / rel).exists()

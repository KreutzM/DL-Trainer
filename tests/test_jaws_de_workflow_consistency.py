from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_core_docs_point_to_workflow() -> None:
    expected_ref = "docs/jaws_de_workflow.md"
    for rel in [
        "README.md",
        "docs/architecture.md",
        "docs/training_policy.md",
        "docs/repo_specification.md",
        "docs/gpt54_teacher_runner.md",
        "docs/sft_eval_pipeline.md",
        "training/transformers/README.md",
    ]:
        assert expected_ref in _read(rel), rel


def test_current_baseline_is_consistent_across_docs() -> None:
    expected_run = "codex_cli_support_validation_v2"
    for rel in [
        "README.md",
        "docs/jaws_de_workflow.md",
        "data/derived/user_simulations/JAWS/DE/README.md",
        "data/derived/teacher_outputs/JAWS/DE/README.md",
        "data/derived/teacher_reviews/JAWS/DE/README.md",
        "data/gold/train/sft/JAWS/DE/README.md",
        "data/gold/eval/JAWS/DE/README.md",
        "data/exports/qwen_sft/JAWS/DE/README.md",
        "Makefile",
    ]:
        assert expected_run in _read(rel), rel


def test_training_config_points_to_current_export() -> None:
    config = yaml.safe_load(_read("training/transformers/jaws_de_current.yaml"))
    dataset = config["dataset"]
    assert dataset["train_file"] == "data/exports/qwen_sft/JAWS/DE/current/train.jsonl"
    assert dataset["eval_file"] == "data/exports/qwen_sft/JAWS/DE/current/eval.jsonl"
    assert dataset["manifest_file"] == "data/exports/qwen_sft/JAWS/DE/current/manifest.json"


def test_makefile_uses_validation_baseline_and_current_config() -> None:
    text = _read("Makefile")
    assert "CURRENT_JAWS_DE_RUN := codex_cli_support_validation_v2" in text
    assert "training/transformers/jaws_de_current.yaml" in text
    assert "scripts/run_codex_cli_support_mvp_pipeline.py" in text

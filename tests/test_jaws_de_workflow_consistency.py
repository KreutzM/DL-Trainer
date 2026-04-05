import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = "docs/jaws_de_current_baseline.json"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _read_json(path: str) -> dict:
    return json.loads(_read(path))


def test_core_docs_point_to_workflow_and_current_baseline() -> None:
    expected_ref = "docs/jaws_de_workflow.md"
    baseline_ref = BASELINE_PATH
    for rel in [
        "README.md",
        "docs/architecture.md",
        "docs/training_policy.md",
        "docs/repo_specification.md",
        "docs/gpt54_teacher_runner.md",
        "docs/sft_eval_pipeline.md",
        "training/transformers/README.md",
    ]:
        text = _read(rel)
        assert expected_ref in text, rel
        assert baseline_ref in text, rel


def test_terminology_governance_mentions_current_baseline_and_reference_path() -> None:
    agents = _read("AGENTS.md")
    assert "## Terminologie" in agents
    assert "JAWS-DE Current-Baseline" in agents
    assert "Support-MVP-Referenzpfad" in agents
    assert "Legacy" in agents

    readme = _read("README.md")
    assert "JAWS-DE Current-Baseline" in readme
    assert "Support-MVP-Referenzpfad" in readme

    rollout = _read("docs/openrouter_benchmark_rollout.md")
    assert "Support-MVP-Referenzpfad" in rollout
    assert "JAWS-DE Current-Baseline" in rollout


def test_current_baseline_is_consistent_across_docs() -> None:
    baseline = _read_json(BASELINE_PATH)
    expected_run = baseline["committed_baseline"]["run_name"]
    expected_selection = baseline["current_job_selection"]["selection_manifest"]
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
        text = _read(rel)
        assert expected_run in text, rel
        if rel in {"README.md", "docs/jaws_de_workflow.md", "Makefile"}:
            assert expected_selection in text, rel


def test_current_baseline_references_existing_files() -> None:
    baseline = _read_json(BASELINE_PATH)
    paths = [
        baseline["workflow_doc"],
        baseline["pipeline_entrypoint"],
        baseline["committed_baseline"]["user_simulations_file"],
        baseline["committed_baseline"]["teacher_outputs_file"],
        baseline["committed_baseline"]["reviewed_teacher_outputs_file"],
        baseline["committed_baseline"]["judge_results_file"],
        baseline["committed_baseline"]["train_file"],
        baseline["committed_baseline"]["eval_file"],
        baseline["current_export"]["output_dir"],
        baseline["current_export"]["manifest_file"],
        baseline["current_training"]["config_file"],
        baseline["current_job_selection"]["selection_manifest"],
        baseline["current_job_selection"]["jobs_file"],
        baseline["current_job_selection"]["job_ids_file"],
    ]
    for rel in paths:
        assert (ROOT / rel).exists(), rel


def test_training_config_and_export_manifest_follow_current_baseline() -> None:
    baseline = _read_json(BASELINE_PATH)
    config = yaml.safe_load(_read(baseline["current_training"]["config_file"]))
    export_manifest = _read_json(baseline["current_export"]["manifest_file"])
    dataset = config["dataset"]
    assert dataset["train_file"] == export_manifest["train_file"]
    assert dataset["eval_file"] == export_manifest["eval_file"]
    assert dataset["train_metadata_file"] == export_manifest["train_metadata_file"]
    assert dataset["eval_metadata_file"] == export_manifest["eval_metadata_file"]
    assert dataset["manifest_file"] == baseline["current_export"]["manifest_file"]
    assert export_manifest["output_dir"] == baseline["current_export"]["output_dir"]
    assert export_manifest["export_id"] == baseline["current_export"]["export_id"]
    assert export_manifest["source_train_files"] == [baseline["committed_baseline"]["train_file"]]
    assert export_manifest["source_eval_files"] == [baseline["committed_baseline"]["eval_file"]]


def test_makefile_uses_current_baseline_and_selection_pointer() -> None:
    baseline = _read_json(BASELINE_PATH)
    text = _read("Makefile")
    assert f"CURRENT_JAWS_DE_BASELINE := {BASELINE_PATH}" in text
    assert f"CURRENT_JAWS_DE_RUN := {baseline['committed_baseline']['run_name']}" in text
    assert baseline["current_training"]["config_file"] in text
    assert baseline["current_job_selection"]["selection_manifest"] in text
    assert "--selection-manifest $(CURRENT_JAWS_DE_SELECTION)" in text
    assert baseline["pipeline_entrypoint"] in text


def test_pipeline_entrypoint_supports_selection_manifest() -> None:
    baseline = _read_json(BASELINE_PATH)
    text = _read(baseline["pipeline_entrypoint"])
    assert "--selection-manifest" in text
    assert "load_selection_manifest" in text


def test_makefile_exposes_support_mvp_benchmark_targets() -> None:
    text = _read("Makefile")
    assert "support-mvp-benchmark-reference:" in text
    assert "support-mvp-benchmark-candidate:" in text
    assert "support-mvp-benchmark-compare:" in text
    assert "support_mvp_default" in text
    assert "support_mvp_openrouter_candidate" in text


def test_current_selection_manifest_matches_current_job_ids() -> None:
    baseline = _read_json(BASELINE_PATH)
    selection = _read_json(baseline["current_job_selection"]["selection_manifest"])
    assert selection["jobs_file"] == baseline["current_job_selection"]["jobs_file"]
    assert selection["job_ids_file"] == baseline["current_job_selection"]["job_ids_file"]
    lines = [line for line in _read(selection["job_ids_file"]).splitlines() if line.strip()]
    assert selection["selected_job_count"] == len(lines)
    assert selection["historical_source"]["job_ids_file"] == "data/derived/teacher_jobs/JAWS/DE/codex_cli_support_validation_v1_job_ids.txt"


def test_active_entrypoints_do_not_use_historical_job_ids_name() -> None:
    old_ref = "codex_cli_support_validation_v1_job_ids.txt"
    for rel in [
        "README.md",
        "Makefile",
        "docs/jaws_de_workflow.md",
        "training/transformers/README.md",
        "data/derived/teacher_jobs/JAWS/DE/README.md",
    ]:
        assert old_ref not in _read(rel), rel

from __future__ import annotations

from argparse import Namespace
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_codex_cli_support_mvp_pipeline as pipeline  # noqa: E402


def _base_args(tmp_path: Path, **overrides: object) -> Namespace:
    payload = {
        "jobs": "data/derived/teacher_jobs/JAWS/DE/demo.jsonl",
        "selection_manifest": None,
        "run_name": "demo-run",
        "job_id": [],
        "job_ids_file": [],
        "limit": None,
        "codex_bin": "codex",
        "sandbox": "read-only",
        "resume": False,
        "codex_config": [],
        "timeout_sec": 600,
        "llm_backend": "codex_cli",
        "openrouter_api_base": "https://openrouter.ai/api/v1",
        "openrouter_api_key_env": "OPENROUTER_API_KEY",
        "llm_profile_config": str(ROOT / "config" / "llm_stage_profiles.json"),
        "llm_profile_set": None,
        "benchmark_name": None,
        "benchmark_role": None,
        "promote": False,
        "user_sim_model": "gpt-5.4-mini",
        "user_sim_reasoning_effort": "low",
        "user_sim_batch_size": 8,
        "user_sim_max_attempts": 1,
        "answer_model": "gpt-5.4",
        "answer_reasoning_effort": "medium",
        "answer_batch_size": 4,
        "answer_max_attempts": 1,
        "judge_model": "gpt-5.4-mini",
        "judge_reasoning_effort": "medium",
        "judge_batch_size": 8,
        "judge_max_attempts": 1,
    }
    payload.update(overrides)
    return Namespace(**payload)


def _fake_report() -> dict[str, object]:
    return {"selected_jobs": 1, "completed_jobs": 1}


def test_pipeline_profile_mode_passes_profile_args(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-token")
    args = _base_args(
        tmp_path,
        llm_profile_set="support_mvp_openrouter_candidate",
        benchmark_name="shadow-apr-2026",
        benchmark_role="candidate",
    )
    commands: list[list[str]] = []
    written_reports: dict[str, dict[str, object]] = {}

    def fake_run_command(command: list[str], repo_root: Path) -> None:
        commands.append(command)
        command_text = " ".join(command)
        if "run_codex_cli_user_sim_batch.py" in command_text:
            (repo_root / "data/derived/user_simulations/JAWS/DE/demo-run_user_simulations_report.json").parent.mkdir(
                parents=True, exist_ok=True
            )
            (repo_root / "data/derived/user_simulations/JAWS/DE/demo-run_user_simulations_report.json").write_text(
                json.dumps(_fake_report()),
                encoding="utf-8",
            )
        if "run_codex_cli_support_answer_batch.py" in command_text:
            (repo_root / "data/derived/teacher_outputs/JAWS/DE/demo-run_answer_report.json").parent.mkdir(
                parents=True, exist_ok=True
            )
            (repo_root / "data/derived/teacher_outputs/JAWS/DE/demo-run_answer_report.json").write_text(
                json.dumps(_fake_report()),
                encoding="utf-8",
            )
        if "run_codex_cli_support_judge_batch.py" in command_text:
            (repo_root / "data/derived/teacher_reviews/JAWS/DE/demo-run_judge_report.json").parent.mkdir(
                parents=True, exist_ok=True
            )
            (repo_root / "data/derived/teacher_reviews/JAWS/DE/demo-run_judge_report.json").write_text(
                json.dumps(_fake_report()),
                encoding="utf-8",
            )

    monkeypatch.setattr(pipeline, "parse_args", lambda: args)
    monkeypatch.setattr(pipeline, "find_repo_root", lambda _: tmp_path)
    monkeypatch.setattr(pipeline, "run_command", fake_run_command)
    monkeypatch.setattr(
        pipeline,
        "write_json",
        lambda path, obj: written_reports.__setitem__(str(path), obj),
    )

    pipeline.main()

    assert any("--llm-profile-set" in command for command in commands)
    assert all("--llm-backend" not in command for command in commands[:3])
    assert all("--teacher-model" not in command for command in commands[:3])
    pipeline_report = written_reports[str(tmp_path / "data/derived/teacher_reviews/JAWS/DE/demo-run_pipeline_report.json")]
    assert pipeline_report["llm_profile_set"] == "support_mvp_openrouter_candidate"
    assert pipeline_report["benchmark"] == {
        "name": "shadow-apr-2026",
        "role": "candidate",
        "profile_set": "support_mvp_openrouter_candidate",
    }


def test_pipeline_profile_mode_rejects_legacy_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    args = _base_args(tmp_path, llm_profile_set="support_mvp_openrouter_candidate", llm_backend="openrouter")

    monkeypatch.setattr(pipeline, "parse_args", lambda: args)
    monkeypatch.setattr(pipeline, "find_repo_root", lambda _: tmp_path)

    with pytest.raises(SystemExit) as exc:
        pipeline.main()

    assert "--llm-backend" in str(exc.value)


def test_pipeline_benchmark_mode_requires_profile_set(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    args = _base_args(tmp_path, benchmark_name="shadow-apr-2026", benchmark_role="reference")

    monkeypatch.setattr(pipeline, "parse_args", lambda: args)
    monkeypatch.setattr(pipeline, "find_repo_root", lambda _: tmp_path)

    with pytest.raises(SystemExit) as exc:
        pipeline.main()

    assert "--llm-profile-set" in str(exc.value)

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from codex_cli_support_mvp_common import (  # noqa: E402
    ANSWER_MODE,
    JUDGE_MODE,
    USER_SIMULATION_MODE,
    resolve_stage_runtime_settings,
    stage_defaults,
)
from llm_stage_profiles import load_profile_config, resolve_profile_set  # noqa: E402


def _stage_args(*, llm_profile_set: str | None = None, **overrides: object) -> Namespace:
    defaults = stage_defaults(USER_SIMULATION_MODE)
    payload = {
        "simulator_model": defaults["model"],
        "codex_bin": "codex",
        "reasoning_effort": defaults["reasoning_effort"],
        "sandbox": "read-only",
        "job_id": [],
        "job_ids_file": [],
        "limit": None,
        "resume": False,
        "batch_size": defaults["batch_size"],
        "max_attempts": defaults["max_attempts"],
        "codex_config": [],
        "timeout_sec": 600,
        "llm_backend": "codex_cli",
        "openrouter_api_base": "https://openrouter.ai/api/v1",
        "openrouter_api_key_env": "OPENROUTER_API_KEY",
        "llm_profile_config": None,
        "llm_profile_set": llm_profile_set,
    }
    payload.update(overrides)
    return Namespace(**payload)


def test_default_profile_config_loads_and_matches_stage_defaults() -> None:
    config = load_profile_config(ROOT)
    assert "support_mvp_default" in config["profile_sets"]

    resolved = resolve_profile_set(ROOT, profile_set_name="support_mvp_default")

    assert resolved["user_simulation"].backend == "codex_cli"
    assert resolved["answer"].backend == "codex_cli"
    assert resolved["judge"].backend == "codex_cli"
    assert resolved["user_simulation"].model == stage_defaults(USER_SIMULATION_MODE)["model"]
    assert resolved["answer"].model == stage_defaults(ANSWER_MODE)["model"]
    assert resolved["judge"].model == stage_defaults(JUDGE_MODE)["model"]


def test_resolve_profile_set_rejects_invalid_backend_and_stage(tmp_path: Path) -> None:
    invalid_config = {
        "version": 1,
        "profile_sets": {
            "broken": {
                "stages": {
                    "user_simulation": {
                        "profile_name": "broken",
                        "backend": "not-real",
                        "model": "x",
                        "batch_size": 1,
                        "max_attempts": 1,
                        "timeout_sec": 10,
                    },
                    "answer": {
                        "profile_name": "answer",
                        "backend": "codex_cli",
                        "model": "gpt-5.4",
                        "batch_size": 1,
                        "max_attempts": 1,
                        "timeout_sec": 10,
                        "codex_cli": {
                            "reasoning_effort": "medium",
                            "sandbox": "read-only",
                            "extra_config": [],
                        },
                    },
                    "unknown_stage": {
                        "profile_name": "judge",
                        "backend": "codex_cli",
                        "model": "gpt-5.4-mini",
                        "batch_size": 1,
                        "max_attempts": 1,
                        "timeout_sec": 10,
                        "codex_cli": {
                            "reasoning_effort": "medium",
                            "sandbox": "read-only",
                            "extra_config": [],
                        },
                    },
                }
            }
        },
    }
    config_path = tmp_path / "profiles.json"
    config_path.write_text(json.dumps(invalid_config), encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        load_profile_config(tmp_path, config_path)

    message = str(exc.value)
    assert "unknown stage keys" in message
    assert "backend must be one of" in message


def test_resolve_stage_runtime_settings_uses_profile_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-token")
    args = _stage_args(llm_profile_set="support_mvp_openrouter_candidate")

    runtime = resolve_stage_runtime_settings(
        args,
        repo_root=ROOT,
        stage_mode=USER_SIMULATION_MODE,
        model_arg_name="simulator_model",
    )

    assert runtime.llm_backend == "openrouter"
    assert runtime.model == "openai/gpt-4.1-mini"
    assert runtime.temperature == 0.2
    assert runtime.max_output_tokens == 1200
    assert runtime.llm_profile_set == "support_mvp_openrouter_candidate"
    assert runtime.openrouter_api_key_env == "OPENROUTER_API_KEY"


def test_resolve_stage_runtime_settings_rejects_legacy_override_with_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-token")
    args = _stage_args(
        llm_profile_set="support_mvp_openrouter_candidate",
        llm_backend="openrouter",
    )

    with pytest.raises(SystemExit) as exc:
        resolve_stage_runtime_settings(
            args,
            repo_root=ROOT,
            stage_mode=USER_SIMULATION_MODE,
            model_arg_name="simulator_model",
        )

    assert "--llm-backend" in str(exc.value)


def test_resolve_stage_runtime_settings_keeps_legacy_default_path() -> None:
    args = _stage_args()

    runtime = resolve_stage_runtime_settings(
        args,
        repo_root=ROOT,
        stage_mode=USER_SIMULATION_MODE,
        model_arg_name="simulator_model",
    )

    assert runtime.llm_backend == "codex_cli"
    assert runtime.model == stage_defaults(USER_SIMULATION_MODE)["model"]
    assert runtime.temperature is None
    assert runtime.llm_profile_set is None

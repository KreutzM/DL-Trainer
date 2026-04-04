from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from common import read_json
from llm_json_backends import OPENROUTER_API_BASE


DEFAULT_PROFILE_CONFIG_PATH = Path("config/llm_stage_profiles.json")
MVP_STAGE_NAMES = ("user_simulation", "answer", "judge")
SUPPORTED_BACKENDS = {"codex_cli", "openrouter"}
RESERVED_PROVIDER_OPTION_KEYS = {"model", "messages", "response_format", "temperature", "max_tokens", "provider"}


@dataclass(slots=True)
class ResolvedStageLlmProfile:
    profile_set_name: str
    stage_name: str
    profile_name: str
    backend: str
    model: str
    batch_size: int
    max_attempts: int
    timeout_sec: int
    temperature: float | None = None
    max_output_tokens: int | None = None
    codex_cli: dict[str, Any] = field(default_factory=dict)
    openrouter: dict[str, Any] = field(default_factory=dict)

    @property
    def reasoning_effort(self) -> str:
        return str(self.codex_cli.get("reasoning_effort", "medium"))

    @property
    def sandbox(self) -> str:
        return str(self.codex_cli.get("sandbox", "read-only"))

    @property
    def extra_config(self) -> list[str]:
        return [str(item) for item in self.codex_cli.get("extra_config", [])]

    @property
    def api_base(self) -> str:
        return str(self.openrouter.get("api_base", OPENROUTER_API_BASE))

    @property
    def api_key_env(self) -> str:
        return str(self.openrouter.get("api_key_env", "OPENROUTER_API_KEY"))

    @property
    def extra_headers(self) -> dict[str, str]:
        return {str(key): str(value) for key, value in dict(self.openrouter.get("extra_headers", {})).items()}

    @property
    def provider_options(self) -> dict[str, Any]:
        return dict(self.openrouter.get("provider_options", {}))

    def profile_metadata(self) -> dict[str, str]:
        return {
            "profile_set": self.profile_set_name,
            "profile_stage": self.stage_name,
            "profile_name": self.profile_name,
        }

    def summary(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "profile_set": self.profile_set_name,
            "profile_stage": self.stage_name,
            "profile_name": self.profile_name,
            "backend": self.backend,
            "model": self.model,
            "batch_size": self.batch_size,
            "max_attempts": self.max_attempts,
            "timeout_sec": self.timeout_sec,
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.max_output_tokens is not None:
            payload["max_output_tokens"] = self.max_output_tokens
        if self.backend == "codex_cli":
            payload["codex_cli"] = {
                "reasoning_effort": self.reasoning_effort,
                "sandbox": self.sandbox,
                "extra_config": self.extra_config,
            }
        if self.backend == "openrouter":
            payload["openrouter"] = {
                "api_base": self.api_base,
                "api_key_env": self.api_key_env,
                "extra_headers": self.extra_headers,
                "provider_options": self.provider_options,
            }
        return payload


def default_profile_config_path(repo_root: Path) -> Path:
    return repo_root / DEFAULT_PROFILE_CONFIG_PATH


def load_profile_config(repo_root: Path, profile_config_path: str | Path | None = None) -> dict[str, Any]:
    config_path = default_profile_config_path(repo_root) if profile_config_path is None else repo_root / Path(profile_config_path)
    try:
        config = read_json(config_path)
    except FileNotFoundError as exc:
        raise ValueError(f"LLM profile config not found: {config_path}") from exc
    validate_profile_config(config, config_path=config_path)
    return config


def validate_profile_config(config: dict[str, Any], *, config_path: Path | None = None) -> None:
    errors: list[str] = []
    prefix = f"{config_path}: " if config_path else ""
    if config.get("version") != 1:
        errors.append(f"{prefix}version must be 1")
    profile_sets = config.get("profile_sets")
    if not isinstance(profile_sets, dict) or not profile_sets:
        errors.append(f"{prefix}profile_sets must be a non-empty object")
        _raise_profile_errors(errors)
    for profile_set_name, profile_set in profile_sets.items():
        errors.extend(_validate_profile_set(profile_set_name, profile_set))
    _raise_profile_errors(errors)


def resolve_profile_set(
    repo_root: Path,
    *,
    profile_set_name: str,
    profile_config_path: str | Path | None = None,
    check_runtime_env: bool = False,
) -> dict[str, ResolvedStageLlmProfile]:
    config = load_profile_config(repo_root, profile_config_path)
    profile_sets = config["profile_sets"]
    if profile_set_name not in profile_sets:
        available = ", ".join(sorted(profile_sets))
        raise ValueError(f"Unknown LLM profile set '{profile_set_name}'. Available: {available}")
    profile_set = profile_sets[profile_set_name]
    stages = dict(profile_set["stages"])
    missing_stages = [stage_name for stage_name in MVP_STAGE_NAMES if stage_name not in stages]
    if missing_stages:
        raise ValueError(
            f"Profile set '{profile_set_name}' is missing required stages: {', '.join(missing_stages)}"
        )
    resolved: dict[str, ResolvedStageLlmProfile] = {}
    for stage_name in MVP_STAGE_NAMES:
        resolved_stage = _build_resolved_stage_profile(profile_set_name, stage_name, stages[stage_name])
        if check_runtime_env and resolved_stage.backend == "openrouter":
            env_name = resolved_stage.api_key_env
            if not os.environ.get(env_name):
                raise ValueError(
                    f"Profile set '{profile_set_name}' stage '{stage_name}' requires environment variable {env_name}"
                )
        resolved[stage_name] = resolved_stage
    return resolved


def _build_resolved_stage_profile(
    profile_set_name: str,
    stage_name: str,
    raw_stage: dict[str, Any],
) -> ResolvedStageLlmProfile:
    return ResolvedStageLlmProfile(
        profile_set_name=profile_set_name,
        stage_name=stage_name,
        profile_name=str(raw_stage["profile_name"]),
        backend=str(raw_stage["backend"]),
        model=str(raw_stage["model"]),
        batch_size=int(raw_stage["batch_size"]),
        max_attempts=int(raw_stage["max_attempts"]),
        timeout_sec=int(raw_stage["timeout_sec"]),
        temperature=None if raw_stage.get("temperature") is None else float(raw_stage["temperature"]),
        max_output_tokens=None
        if raw_stage.get("max_output_tokens") is None
        else int(raw_stage["max_output_tokens"]),
        codex_cli=dict(raw_stage.get("codex_cli", {})),
        openrouter=dict(raw_stage.get("openrouter", {})),
    )


def _validate_profile_set(profile_set_name: str, profile_set: Any) -> list[str]:
    errors: list[str] = []
    prefix = f"profile_sets.{profile_set_name}"
    if not isinstance(profile_set, dict):
        return [f"{prefix} must be an object"]
    stages = profile_set.get("stages")
    if not isinstance(stages, dict) or not stages:
        return [f"{prefix}.stages must be a non-empty object"]
    unknown_stages = sorted(stage_name for stage_name in stages if stage_name not in MVP_STAGE_NAMES)
    if unknown_stages:
        errors.append(f"{prefix}.stages contains unknown stage keys: {', '.join(unknown_stages)}")
    for stage_name, stage_config in stages.items():
        errors.extend(_validate_stage_config(profile_set_name, stage_name, stage_config))
    return errors


def _validate_stage_config(profile_set_name: str, stage_name: str, stage_config: Any) -> list[str]:
    errors: list[str] = []
    prefix = f"profile_sets.{profile_set_name}.stages.{stage_name}"
    if not isinstance(stage_config, dict):
        return [f"{prefix} must be an object"]
    for required_key in ("profile_name", "backend", "model", "batch_size", "max_attempts", "timeout_sec"):
        if required_key not in stage_config:
            errors.append(f"{prefix}.{required_key} is required")
    if errors:
        return errors

    backend = stage_config.get("backend")
    if backend not in SUPPORTED_BACKENDS:
        errors.append(f"{prefix}.backend must be one of: {', '.join(sorted(SUPPORTED_BACKENDS))}")

    if not str(stage_config.get("profile_name") or "").strip():
        errors.append(f"{prefix}.profile_name must be a non-empty string")
    if not str(stage_config.get("model") or "").strip():
        errors.append(f"{prefix}.model must be a non-empty string")

    errors.extend(_validate_positive_int(prefix, stage_config, "batch_size"))
    errors.extend(_validate_positive_int(prefix, stage_config, "max_attempts"))
    errors.extend(_validate_positive_int(prefix, stage_config, "timeout_sec"))

    temperature = stage_config.get("temperature")
    if temperature is not None:
        try:
            numeric_temperature = float(temperature)
        except (TypeError, ValueError):
            errors.append(f"{prefix}.temperature must be numeric when set")
        else:
            if numeric_temperature < 0 or numeric_temperature > 2:
                errors.append(f"{prefix}.temperature must be between 0 and 2")

    errors.extend(_validate_optional_positive_int(prefix, stage_config, "max_output_tokens"))

    codex_config = stage_config.get("codex_cli")
    openrouter_config = stage_config.get("openrouter")
    if backend == "codex_cli":
        if stage_config.get("temperature") is not None:
            errors.append(f"{prefix}.temperature is not supported for backend codex_cli")
        if stage_config.get("max_output_tokens") is not None:
            errors.append(f"{prefix}.max_output_tokens is not supported for backend codex_cli")
        if openrouter_config is not None:
            errors.append(f"{prefix}.openrouter is not allowed for backend codex_cli")
        errors.extend(_validate_codex_cli_config(prefix, codex_config))
    elif backend == "openrouter":
        if codex_config is not None:
            errors.append(f"{prefix}.codex_cli is not allowed for backend openrouter")
        errors.extend(_validate_openrouter_config(prefix, openrouter_config))
    return errors


def _validate_positive_int(prefix: str, payload: dict[str, Any], key: str) -> list[str]:
    try:
        value = int(payload.get(key))
    except (TypeError, ValueError):
        return [f"{prefix}.{key} must be an integer >= 1"]
    if value < 1:
        return [f"{prefix}.{key} must be an integer >= 1"]
    return []


def _validate_optional_positive_int(prefix: str, payload: dict[str, Any], key: str) -> list[str]:
    if payload.get(key) is None:
        return []
    return _validate_positive_int(prefix, payload, key)


def _validate_codex_cli_config(prefix: str, codex_config: Any) -> list[str]:
    errors: list[str] = []
    config_prefix = f"{prefix}.codex_cli"
    if not isinstance(codex_config, dict):
        return [f"{config_prefix} must be an object for backend codex_cli"]
    if not str(codex_config.get("reasoning_effort") or "").strip():
        errors.append(f"{config_prefix}.reasoning_effort must be a non-empty string")
    if not str(codex_config.get("sandbox") or "").strip():
        errors.append(f"{config_prefix}.sandbox must be a non-empty string")
    extra_config = codex_config.get("extra_config", [])
    if not isinstance(extra_config, list) or not all(isinstance(item, str) for item in extra_config):
        errors.append(f"{config_prefix}.extra_config must be a list of strings")
    return errors


def _validate_openrouter_config(prefix: str, openrouter_config: Any) -> list[str]:
    errors: list[str] = []
    config_prefix = f"{prefix}.openrouter"
    if not isinstance(openrouter_config, dict):
        return [f"{config_prefix} must be an object for backend openrouter"]
    if not str(openrouter_config.get("api_base") or "").strip():
        errors.append(f"{config_prefix}.api_base must be a non-empty string")
    if not str(openrouter_config.get("api_key_env") or "").strip():
        errors.append(f"{config_prefix}.api_key_env must be a non-empty string")
    extra_headers = openrouter_config.get("extra_headers", {})
    if not isinstance(extra_headers, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in extra_headers.items()
    ):
        errors.append(f"{config_prefix}.extra_headers must be an object with string keys and values")
    provider_options = openrouter_config.get("provider_options", {})
    if not isinstance(provider_options, dict):
        errors.append(f"{config_prefix}.provider_options must be an object")
    else:
        reserved = sorted(key for key in provider_options if key in RESERVED_PROVIDER_OPTION_KEYS)
        if reserved:
            errors.append(
                f"{config_prefix}.provider_options cannot override reserved request keys: {', '.join(reserved)}"
            )
    return errors


def _raise_profile_errors(errors: list[str]) -> None:
    if errors:
        raise ValueError("Invalid LLM profile config:\n- " + "\n- ".join(errors))

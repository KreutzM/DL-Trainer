from __future__ import annotations

from itertools import islice
from pathlib import Path
from typing import Any
from dataclasses import dataclass

from common import find_repo_root
from llm_json_backends import (
    JsonGenerationRequest,
    JsonGenerationResult,
    OPENROUTER_API_BASE,
    build_backend_record,
    provider_name_for_backend,
    resolve_json_backend,
)
from llm_stage_profiles import ResolvedStageLlmProfile, resolve_profile_set


TRANSFORM_PIPELINE_VERSION = "0.8.0"
USER_SIMULATION_MODE = "teacher_user_simulator_codex_cli_v1"
ANSWER_MODE = "teacher_answer_codex_cli_v1"
JUDGE_MODE = "teacher_judge_codex_cli_v1"
USER_SIMULATION_PROMPT_VERSION = "jaws_de_user_simulation_v1"
ANSWER_PROMPT_VERSION = "jaws_de_support_answer_mvp_v4"
JUDGE_PROMPT_VERSION = "jaws_de_support_judge_v3"
STAGE_DEFAULTS = {
    USER_SIMULATION_MODE: {
        "model": "gpt-5.4-mini",
        "reasoning_effort": "low",
        "batch_size": 8,
        "max_attempts": 1,
    },
    ANSWER_MODE: {
        "model": "gpt-5.4",
        "reasoning_effort": "medium",
        "batch_size": 4,
        "max_attempts": 1,
    },
    JUDGE_MODE: {
        "model": "gpt-5.4-mini",
        "reasoning_effort": "medium",
        "batch_size": 8,
        "max_attempts": 1,
    },
}
STAGE_NAME_BY_MODE = {
    USER_SIMULATION_MODE: "user_simulation",
    ANSWER_MODE: "answer",
    JUDGE_MODE: "judge",
}
LEGACY_TIMEOUT_DEFAULT_SEC = 600


@dataclass(slots=True)
class StageRuntimeSettings:
    stage_name: str
    llm_backend: str
    model: str
    reasoning_effort: str
    batch_size: int
    max_attempts: int
    timeout_sec: int
    sandbox: str
    codex_bin: str
    codex_config: list[str]
    openrouter_api_base: str
    openrouter_api_key_env: str
    openrouter_extra_headers: dict[str, str]
    openrouter_provider_options: dict[str, Any]
    temperature: float | None = None
    max_output_tokens: int | None = None
    llm_profile_set: str | None = None
    llm_profile_name: str | None = None

    def profile_metadata(self) -> dict[str, str] | None:
        if not self.llm_profile_set or not self.llm_profile_name:
            return None
        return {
            "profile_set": self.llm_profile_set,
            "profile_stage": self.stage_name,
            "profile_name": self.llm_profile_name,
        }

    def report_summary(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "backend": self.llm_backend,
            "model": self.model,
            "batch_size": self.batch_size,
            "max_attempts": self.max_attempts,
            "timeout_sec": self.timeout_sec,
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.max_output_tokens is not None:
            payload["max_output_tokens"] = self.max_output_tokens
        if self.llm_backend == "codex_cli":
            payload["codex_cli"] = {
                "reasoning_effort": self.reasoning_effort,
                "sandbox": self.sandbox,
                "extra_config": list(self.codex_config),
            }
        elif self.llm_backend == "openrouter":
            payload["openrouter"] = {
                "api_base": self.openrouter_api_base,
                "api_key_env": self.openrouter_api_key_env,
                "extra_headers": dict(self.openrouter_extra_headers),
                "provider_options": dict(self.openrouter_provider_options),
            }
        profile_metadata = self.profile_metadata()
        if profile_metadata:
            payload["llm_profile"] = profile_metadata
        return payload


def normalized_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def safe_slug(text: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)


def load_repo_text(repo_root: Path, relative_path: str) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8").strip()


def compact_text(text: str | None) -> str:
    if not text:
        return ""
    lines = [line.rstrip() for line in str(text).replace("\r\n", "\n").splitlines()]
    compacted: list[str] = []
    blank_pending = False
    for line in lines:
        if line.strip():
            if blank_pending and compacted:
                compacted.append("")
            compacted.append(line.strip())
            blank_pending = False
        else:
            blank_pending = True
    return "\n".join(compacted).strip()


def chunked(items: list[Any], chunk_size: int) -> list[list[Any]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be >= 1")
    iterator = iter(items)
    chunks: list[list[Any]] = []
    while batch := list(islice(iterator, chunk_size)):
        chunks.append(batch)
    return chunks


def stage_defaults(stage_mode: str) -> dict[str, Any]:
    try:
        return dict(STAGE_DEFAULTS[stage_mode])
    except KeyError as exc:
        raise KeyError(f"Unknown stage mode: {stage_mode}") from exc


def add_llm_backend_args(parser: Any) -> None:
    parser.add_argument("--llm-backend", choices=["codex_cli", "openrouter"], default="codex_cli")
    parser.add_argument("--openrouter-api-base", default=OPENROUTER_API_BASE)
    parser.add_argument("--openrouter-api-key-env", default="OPENROUTER_API_KEY")


def add_llm_profile_args(parser: Any) -> None:
    parser.add_argument("--llm-profile-config")
    parser.add_argument("--llm-profile-set")


def generation_mode_for_backend(stage_mode: str, backend_name: str) -> str:
    if backend_name == "codex_cli":
        return stage_mode
    return stage_mode.replace("codex_cli", backend_name)


def stage_provider_name(backend_name: str) -> str:
    return provider_name_for_backend(backend_name)


def run_stage_json_generation(
    *,
    llm_backend: str,
    repo_root: Path,
    model: str,
    prompt_text: str,
    schema: dict[str, Any],
    artifact_dir: Path,
    request_payload: dict[str, Any],
    timeout_sec: int,
    max_attempts: int = 1,
    reasoning_effort: str = "medium",
    sandbox: str = "read-only",
    codex_bin: str = "codex",
    extra_config: list[str] | None = None,
    openrouter_api_base: str = OPENROUTER_API_BASE,
    openrouter_api_key_env: str = "OPENROUTER_API_KEY",
    openrouter_extra_headers: dict[str, str] | None = None,
    openrouter_provider_options: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
) -> JsonGenerationResult:
    if llm_backend == "codex_cli":
        backend = resolve_json_backend(
            llm_backend,
            repo_root=repo_root,
            codex_bin=codex_bin,
            reasoning_effort=reasoning_effort,
            sandbox=sandbox,
            extra_config=extra_config,
        )
    else:
        backend = resolve_json_backend(
            llm_backend,
            api_base=openrouter_api_base,
            api_key_env=openrouter_api_key_env,
            extra_headers=openrouter_extra_headers,
            provider_options=openrouter_provider_options,
        )
    request = JsonGenerationRequest(
        model=model,
        prompt_text=prompt_text,
        response_schema=schema,
        request_payload=request_payload,
        artifact_dir=artifact_dir,
        timeout_sec=timeout_sec,
        max_attempts=max_attempts,
        metadata=metadata or {},
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    return backend.generate(request)


def build_stage_backend_record(
    result: JsonGenerationResult,
    *,
    batch_id: str | None = None,
    batch_size: int | None = None,
    batch_index: int | None = None,
) -> dict[str, Any]:
    return build_backend_record(
        result,
        batch_id=batch_id,
        batch_size=batch_size,
        batch_index=batch_index,
    )


def build_stage_metrics(
    *,
    selected_jobs: int,
    completed_jobs: int,
    skipped_existing_jobs: list[str],
    failed_jobs: list[dict[str, str]],
    batch_size: int,
    executed_batches: int,
    completed_batches: int,
    total_elapsed_ms: int,
    total_prompt_chars: int,
    total_source_excerpt_chars: int,
    total_retry_attempts: int,
) -> dict[str, Any]:
    processed_jobs = max(completed_jobs - len(skipped_existing_jobs), 0)
    return {
        "selected_jobs": selected_jobs,
        "completed_jobs": completed_jobs,
        "processed_jobs": processed_jobs,
        "skipped_existing_jobs": len(skipped_existing_jobs),
        "failed_jobs": len(failed_jobs),
        "configured_batch_size": batch_size,
        "executed_batches": executed_batches,
        "completed_batches": completed_batches,
        "avg_jobs_per_completed_batch": round(processed_jobs / completed_batches, 2) if completed_batches else 0,
        "total_elapsed_ms": total_elapsed_ms,
        "avg_elapsed_ms_per_processed_job": round(total_elapsed_ms / processed_jobs, 2) if processed_jobs else 0,
        "avg_elapsed_ms_per_completed_batch": round(total_elapsed_ms / completed_batches, 2) if completed_batches else 0,
        "total_prompt_chars": total_prompt_chars,
        "avg_prompt_chars_per_processed_job": round(total_prompt_chars / processed_jobs, 2) if processed_jobs else 0,
        "total_source_excerpt_chars": total_source_excerpt_chars,
        "avg_source_excerpt_chars_per_processed_job": round(
            total_source_excerpt_chars / processed_jobs, 2
        )
        if processed_jobs
        else 0,
        "total_retry_attempts": total_retry_attempts,
    }


def repo_root_from_cwd() -> Path:
    return find_repo_root(Path.cwd())


def stage_name_for_mode(stage_mode: str) -> str:
    try:
        return STAGE_NAME_BY_MODE[stage_mode]
    except KeyError as exc:
        raise KeyError(f"Unknown stage mode: {stage_mode}") from exc


def resolve_stage_runtime_settings(
    args: Any,
    *,
    repo_root: Path,
    stage_mode: str,
    model_arg_name: str,
) -> StageRuntimeSettings:
    stage_name = stage_name_for_mode(stage_mode)
    if not getattr(args, "llm_profile_set", None):
        return StageRuntimeSettings(
            stage_name=stage_name,
            llm_backend=args.llm_backend,
            model=getattr(args, model_arg_name),
            reasoning_effort=args.reasoning_effort,
            batch_size=args.batch_size,
            max_attempts=args.max_attempts,
            timeout_sec=args.timeout_sec,
            sandbox=args.sandbox,
            codex_bin=args.codex_bin,
            codex_config=list(args.codex_config),
            openrouter_api_base=args.openrouter_api_base,
            openrouter_api_key_env=args.openrouter_api_key_env,
            openrouter_extra_headers={},
            openrouter_provider_options={},
        )

    ensure_profile_mode_has_no_legacy_overrides(args, stage_mode=stage_mode, model_arg_name=model_arg_name)
    resolved_profiles = resolve_profile_set(
        repo_root,
        profile_set_name=args.llm_profile_set,
        profile_config_path=args.llm_profile_config,
        check_runtime_env=True,
    )
    profile = resolved_profiles[stage_name]
    return runtime_settings_from_profile(profile, codex_bin=args.codex_bin)


def runtime_settings_from_profile(profile: ResolvedStageLlmProfile, *, codex_bin: str) -> StageRuntimeSettings:
    return StageRuntimeSettings(
        stage_name=profile.stage_name,
        llm_backend=profile.backend,
        model=profile.model,
        reasoning_effort=profile.reasoning_effort,
        batch_size=profile.batch_size,
        max_attempts=profile.max_attempts,
        timeout_sec=profile.timeout_sec,
        sandbox=profile.sandbox,
        codex_bin=codex_bin,
        codex_config=profile.extra_config,
        openrouter_api_base=profile.api_base,
        openrouter_api_key_env=profile.api_key_env,
        openrouter_extra_headers=profile.extra_headers,
        openrouter_provider_options=profile.provider_options,
        temperature=profile.temperature,
        max_output_tokens=profile.max_output_tokens,
        llm_profile_set=profile.profile_set_name,
        llm_profile_name=profile.profile_name,
    )


def ensure_profile_mode_has_no_legacy_overrides(args: Any, *, stage_mode: str, model_arg_name: str) -> None:
    defaults = stage_defaults(stage_mode)
    conflicts: list[str] = []
    if getattr(args, model_arg_name) != defaults["model"]:
        conflicts.append(f"--{model_arg_name.replace('_', '-')}")
    if args.reasoning_effort != defaults["reasoning_effort"]:
        conflicts.append("--reasoning-effort")
    if args.batch_size != defaults["batch_size"]:
        conflicts.append("--batch-size")
    if args.max_attempts != defaults["max_attempts"]:
        conflicts.append("--max-attempts")
    if args.timeout_sec != LEGACY_TIMEOUT_DEFAULT_SEC:
        conflicts.append("--timeout-sec")
    if args.llm_backend != "codex_cli":
        conflicts.append("--llm-backend")
    if args.sandbox != "read-only":
        conflicts.append("--sandbox")
    if args.openrouter_api_base != OPENROUTER_API_BASE:
        conflicts.append("--openrouter-api-base")
    if args.openrouter_api_key_env != "OPENROUTER_API_KEY":
        conflicts.append("--openrouter-api-key-env")
    if args.codex_config:
        conflicts.append("--codex-config")
    if conflicts:
        joined = ", ".join(conflicts)
        raise SystemExit(
            f"--llm-profile-set cannot be combined with legacy stage LLM overrides for {stage_name_for_mode(stage_mode)}: {joined}"
        )

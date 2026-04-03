from __future__ import annotations

from itertools import islice
from pathlib import Path
from typing import Any

from common import find_repo_root
from llm_json_backends import (
    JsonGenerationRequest,
    JsonGenerationResult,
    OPENROUTER_API_BASE,
    build_backend_record,
    provider_name_for_backend,
    resolve_json_backend,
)


TRANSFORM_PIPELINE_VERSION = "0.8.0"
USER_SIMULATION_MODE = "teacher_user_simulator_codex_cli_v1"
ANSWER_MODE = "teacher_answer_codex_cli_v1"
JUDGE_MODE = "teacher_judge_codex_cli_v1"
USER_SIMULATION_PROMPT_VERSION = "jaws_de_user_simulation_v1"
ANSWER_PROMPT_VERSION = "jaws_de_support_answer_mvp_v1"
JUDGE_PROMPT_VERSION = "jaws_de_support_judge_v1"
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
    metadata: dict[str, Any] | None = None,
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

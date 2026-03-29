from __future__ import annotations

import json
import shutil
import subprocess
import time
from itertools import islice
from pathlib import Path
from typing import Any

from common import find_repo_root, sha256_file, write_json


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


def build_codex_command(
    *,
    codex_bin: str,
    repo_root: Path,
    model: str,
    reasoning_effort: str,
    sandbox: str,
    schema_path: Path,
    output_path: Path,
    extra_config: list[str],
) -> list[str]:
    resolved_codex = shutil.which(codex_bin)
    if not resolved_codex and Path(codex_bin).suffix == "":
        resolved_codex = shutil.which(f"{codex_bin}.cmd") or shutil.which(f"{codex_bin}.exe")
    if not resolved_codex:
        raise SystemExit(f"Could not resolve Codex CLI binary: {codex_bin}")
    command = [
        resolved_codex,
        "exec",
        "-m",
        model,
        "-s",
        sandbox,
        "--skip-git-repo-check",
        "--ephemeral",
        "--color",
        "never",
        "--output-schema",
        str(schema_path),
        "-o",
        str(output_path),
        "-C",
        str(repo_root),
        "-",
        "-c",
        f'reasoning_effort="{reasoning_effort}"',
    ]
    for config_value in extra_config:
        command.extend(["-c", config_value])
    return command


def run_codex_json_generation(
    *,
    codex_bin: str,
    repo_root: Path,
    model: str,
    reasoning_effort: str,
    sandbox: str,
    schema: dict[str, Any],
    prompt_text: str,
    artifact_dir: Path,
    request_payload: dict[str, Any],
    extra_config: list[str],
    timeout_sec: int,
    max_attempts: int = 1,
) -> tuple[dict[str, Any], str, dict[str, Path], list[str], int, int]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    request_path = artifact_dir / "request.json"
    prompt_path = artifact_dir / "prompt.txt"
    schema_path = artifact_dir / "response_schema.json"
    response_path = artifact_dir / "last_message.json"
    stdout_path = artifact_dir / "stdout.txt"
    stderr_path = artifact_dir / "stderr.txt"

    write_json(request_path, request_payload)
    write_json(schema_path, schema)
    prompt_path.write_text(prompt_text, encoding="utf-8")

    command = build_codex_command(
        codex_bin=codex_bin,
        repo_root=repo_root,
        model=model,
        reasoning_effort=reasoning_effort,
        sandbox=sandbox,
        schema_path=schema_path,
        output_path=response_path,
        extra_config=extra_config,
    )

    last_error: RuntimeError | None = None
    total_elapsed_ms = 0
    for attempt in range(1, max_attempts + 1):
        started = time.perf_counter()
        completed = subprocess.run(
            command,
            input=prompt_text,
            text=True,
            capture_output=True,
            cwd=repo_root,
            timeout=timeout_sec,
            encoding="utf-8",
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        total_elapsed_ms += elapsed_ms
        stdout_path.write_text(completed.stdout or "", encoding="utf-8")
        stderr_path.write_text(completed.stderr or "", encoding="utf-8")

        if completed.returncode != 0:
            last_error = RuntimeError(f"codex_exit_{completed.returncode}: {normalized_path(stderr_path)}")
            continue
        if not response_path.exists():
            last_error = RuntimeError(f"missing_last_message: {normalized_path(stderr_path)}")
            continue

        raw_text = response_path.read_text(encoding="utf-8").strip()
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            last_error = RuntimeError(f"invalid_json:{exc}: {normalized_path(response_path)}")
            continue
        break
    else:
        if last_error is not None:
            raise last_error
        raise RuntimeError(f"codex_unknown_failure: {normalized_path(stderr_path)}")

    artifact_paths = {
        "request": request_path,
        "prompt": prompt_path,
        "schema": schema_path,
        "response": response_path,
        "stdout": stdout_path,
        "stderr": stderr_path,
    }
    return parsed, raw_text, artifact_paths, command, total_elapsed_ms, attempt


def build_codex_cli_meta(
    *,
    command: list[str],
    artifact_paths: dict[str, Path],
    batch_id: str | None = None,
    batch_size: int | None = None,
    batch_index: int | None = None,
) -> dict[str, Any]:
    portable_command = list(command)
    if portable_command:
        binary_name = Path(portable_command[0]).name.lower()
        if binary_name.startswith("codex"):
            portable_command[0] = "codex"
    return {
        "command": portable_command,
        "batch_id": batch_id,
        "batch_size": batch_size,
        "batch_index": batch_index,
        "request_path": normalized_path(artifact_paths["request"]),
        "prompt_path": normalized_path(artifact_paths["prompt"]),
        "schema_path": normalized_path(artifact_paths["schema"]),
        "response_path": normalized_path(artifact_paths["response"]),
        "stdout_path": normalized_path(artifact_paths["stdout"]),
        "stderr_path": normalized_path(artifact_paths["stderr"]),
        "prompt_sha256": sha256_file(artifact_paths["prompt"]),
        "schema_sha256": sha256_file(artifact_paths["schema"]),
    }


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

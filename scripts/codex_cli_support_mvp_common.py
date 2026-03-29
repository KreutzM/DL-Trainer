from __future__ import annotations

import json
import shutil
import subprocess
import time
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


def normalized_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def safe_slug(text: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)


def load_repo_text(repo_root: Path, relative_path: str) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8").strip()


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
) -> tuple[dict[str, Any], str, dict[str, Path], list[str], int]:
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
    stdout_path.write_text(completed.stdout or "", encoding="utf-8")
    stderr_path.write_text(completed.stderr or "", encoding="utf-8")

    if completed.returncode != 0:
        raise RuntimeError(f"codex_exit_{completed.returncode}: {normalized_path(stderr_path)}")
    if not response_path.exists():
        raise RuntimeError(f"missing_last_message: {normalized_path(stderr_path)}")

    raw_text = response_path.read_text(encoding="utf-8").strip()
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid_json:{exc}: {normalized_path(response_path)}") from exc

    artifact_paths = {
        "request": request_path,
        "prompt": prompt_path,
        "schema": schema_path,
        "response": response_path,
        "stdout": stdout_path,
        "stderr": stderr_path,
    }
    return parsed, raw_text, artifact_paths, command, elapsed_ms


def build_codex_cli_meta(
    *,
    command: list[str],
    artifact_paths: dict[str, Path],
) -> dict[str, Any]:
    portable_command = list(command)
    if portable_command:
        binary_name = Path(portable_command[0]).name.lower()
        if binary_name.startswith("codex"):
            portable_command[0] = "codex"
    return {
        "command": portable_command,
        "request_path": normalized_path(artifact_paths["request"]),
        "prompt_path": normalized_path(artifact_paths["prompt"]),
        "schema_path": normalized_path(artifact_paths["schema"]),
        "response_path": normalized_path(artifact_paths["response"]),
        "stdout_path": normalized_path(artifact_paths["stdout"]),
        "stderr_path": normalized_path(artifact_paths["stderr"]),
        "prompt_sha256": sha256_file(artifact_paths["prompt"]),
        "schema_sha256": sha256_file(artifact_paths["schema"]),
    }


def repo_root_from_cwd() -> Path:
    return find_repo_root(Path.cwd())

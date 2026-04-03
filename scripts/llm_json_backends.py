from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from common import sha256_file, write_json


OPENAI_API_BASE = "https://api.openai.com/v1"
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


def normalized_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


@dataclass(slots=True)
class JsonGenerationRequest:
    model: str
    prompt_text: str
    response_schema: dict[str, Any]
    request_payload: dict[str, Any]
    artifact_dir: Path
    timeout_sec: int
    max_attempts: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    messages: list[dict[str, str]] | None = None
    schema_name: str = "json_generation_payload"
    temperature: float | None = None
    max_output_tokens: int | None = None


@dataclass(slots=True)
class JsonGenerationResult:
    backend_name: str
    provider_name: str
    model: str
    parsed_response: dict[str, Any]
    raw_text: str
    provider_response_id: str | None
    usage: dict[str, Any] | None
    elapsed_ms: int
    attempt_count: int
    artifact_paths: dict[str, Path]
    backend_metadata: dict[str, Any]


class JsonGenerationBackend(Protocol):
    backend_name: str
    provider_name: str

    def generate(self, request: JsonGenerationRequest) -> JsonGenerationResult:
        ...


def provider_name_for_backend(backend_name: str) -> str:
    if backend_name in {"codex_cli", "openai", "openrouter"}:
        return backend_name
    raise ValueError(f"Unsupported JSON backend: {backend_name}")


def build_backend_record(result: JsonGenerationResult, **extra_metadata: Any) -> dict[str, Any]:
    metadata = dict(result.backend_metadata)
    metadata.update({key: value for key, value in extra_metadata.items() if value is not None})
    return {result.provider_name: metadata}


def _write_request_manifest(path: Path, payload: dict[str, Any], metadata: dict[str, Any]) -> None:
    manifest = dict(payload)
    if metadata:
        manifest["_llm_request_metadata"] = metadata
    write_json(path, manifest)


def _extract_message_content(response_json: dict[str, Any]) -> str:
    choices = response_json.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("missing_choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise RuntimeError("missing_message")
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = [
            str(item.get("text") or "")
            for item in content
            if isinstance(item, dict) and item.get("type") in {None, "text"}
        ]
        joined = "".join(text_parts).strip()
        if joined:
            return joined
    raise RuntimeError("missing_message_content")


class CodexCliJsonBackend:
    backend_name = "codex_cli"
    provider_name = "codex_cli"

    def __init__(
        self,
        *,
        repo_root: Path,
        codex_bin: str = "codex",
        reasoning_effort: str = "medium",
        sandbox: str = "read-only",
        extra_config: list[str] | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.codex_bin = codex_bin
        self.reasoning_effort = reasoning_effort
        self.sandbox = sandbox
        self.extra_config = list(extra_config or [])

    def _resolve_binary(self) -> str:
        resolved_codex = shutil.which(self.codex_bin)
        if not resolved_codex and Path(self.codex_bin).suffix == "":
            resolved_codex = shutil.which(f"{self.codex_bin}.cmd") or shutil.which(f"{self.codex_bin}.exe")
        if not resolved_codex:
            raise RuntimeError(f"Could not resolve Codex CLI binary: {self.codex_bin}")
        return resolved_codex

    def _build_command(self, *, model: str, schema_path: Path, output_path: Path) -> list[str]:
        command = [
            self._resolve_binary(),
            "exec",
            "-m",
            model,
            "-s",
            self.sandbox,
            "--skip-git-repo-check",
            "--ephemeral",
            "--color",
            "never",
            "--output-schema",
            str(schema_path),
            "-o",
            str(output_path),
            "-C",
            str(self.repo_root),
            "-",
            "-c",
            f'reasoning_effort="{self.reasoning_effort}"',
        ]
        for config_value in self.extra_config:
            command.extend(["-c", config_value])
        return command

    def generate(self, request: JsonGenerationRequest) -> JsonGenerationResult:
        if request.temperature is not None:
            raise RuntimeError("codex_cli backend does not support temperature")
        if request.max_output_tokens is not None:
            raise RuntimeError("codex_cli backend does not support max_output_tokens")
        request.artifact_dir.mkdir(parents=True, exist_ok=True)
        request_path = request.artifact_dir / "request.json"
        prompt_path = request.artifact_dir / "prompt.txt"
        schema_path = request.artifact_dir / "response_schema.json"
        response_path = request.artifact_dir / "last_message.json"
        stdout_path = request.artifact_dir / "stdout.txt"
        stderr_path = request.artifact_dir / "stderr.txt"

        _write_request_manifest(request_path, request.request_payload, request.metadata)
        write_json(schema_path, request.response_schema)
        prompt_path.write_text(request.prompt_text, encoding="utf-8")

        command = self._build_command(model=request.model, schema_path=schema_path, output_path=response_path)

        parsed: dict[str, Any] | None = None
        raw_text = ""
        last_error: RuntimeError | None = None
        total_elapsed_ms = 0
        for attempt in range(1, request.max_attempts + 1):
            started = time.perf_counter()
            completed = subprocess.run(
                command,
                input=request.prompt_text,
                text=True,
                capture_output=True,
                cwd=self.repo_root,
                timeout=request.timeout_sec,
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
            raise last_error or RuntimeError(f"codex_unknown_failure: {normalized_path(stderr_path)}")

        portable_command = list(command)
        if portable_command:
            binary_name = Path(portable_command[0]).name.lower()
            if binary_name.startswith("codex"):
                portable_command[0] = "codex"

        artifact_paths = {
            "request": request_path,
            "prompt": prompt_path,
            "schema": schema_path,
            "response": response_path,
            "stdout": stdout_path,
            "stderr": stderr_path,
        }
        backend_metadata = {
            "command": portable_command,
            "request_path": normalized_path(request_path),
            "prompt_path": normalized_path(prompt_path),
            "schema_path": normalized_path(schema_path),
            "response_path": normalized_path(response_path),
            "stdout_path": normalized_path(stdout_path),
            "stderr_path": normalized_path(stderr_path),
            "prompt_sha256": sha256_file(prompt_path),
            "schema_sha256": sha256_file(schema_path),
        }
        if request.metadata:
            backend_metadata["request_metadata"] = request.metadata

        return JsonGenerationResult(
            backend_name=self.backend_name,
            provider_name=self.provider_name,
            model=request.model,
            parsed_response=parsed or {},
            raw_text=raw_text,
            provider_response_id=None,
            usage=None,
            elapsed_ms=total_elapsed_ms,
            attempt_count=attempt,
            artifact_paths=artifact_paths,
            backend_metadata=backend_metadata,
        )


class OpenAICompatibleJsonBackend:
    def __init__(
        self,
        *,
        provider_name: str,
        api_base: str,
        api_key: str | None = None,
        api_key_env: str | None = None,
        extra_headers: dict[str, str] | None = None,
        provider_options: dict[str, Any] | None = None,
    ) -> None:
        self.backend_name = provider_name
        self.provider_name = provider_name
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.api_key_env = api_key_env
        self.extra_headers = dict(extra_headers or {})
        self.provider_options = dict(provider_options or {})

    def _resolve_api_key(self) -> str:
        if self.api_key:
            return self.api_key
        if self.api_key_env:
            api_key = os.environ.get(self.api_key_env)
            if api_key:
                return api_key
        raise RuntimeError(
            f"Environment variable {self.api_key_env} is required for backend {self.provider_name}"
        )

    def generate(self, request: JsonGenerationRequest) -> JsonGenerationResult:
        request.artifact_dir.mkdir(parents=True, exist_ok=True)
        request_path = request.artifact_dir / "request.json"
        prompt_path = request.artifact_dir / "prompt.txt"
        schema_path = request.artifact_dir / "response_schema.json"
        request_body_path = request.artifact_dir / "http_request.json"
        response_path = request.artifact_dir / "response.json"

        _write_request_manifest(request_path, request.request_payload, request.metadata)
        write_json(schema_path, request.response_schema)
        prompt_path.write_text(request.prompt_text, encoding="utf-8")

        api_key = self._resolve_api_key()
        messages = request.messages or [{"role": "user", "content": request.prompt_text}]
        request_body: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": request.schema_name,
                    "strict": True,
                    "schema": request.response_schema,
                },
            },
        }
        if request.temperature is not None:
            request_body["temperature"] = request.temperature
        if request.max_output_tokens is not None:
            request_body["max_tokens"] = request.max_output_tokens
        request_body.update(self.provider_options)
        write_json(request_body_path, request_body)

        parsed: dict[str, Any] | None = None
        raw_text = ""
        response_json: dict[str, Any] | None = None
        last_error: RuntimeError | None = None
        total_elapsed_ms = 0
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }
        for attempt in range(1, request.max_attempts + 1):
            http_request = urllib.request.Request(
                url=f"{self.api_base}/chat/completions",
                method="POST",
                data=json.dumps(request_body).encode("utf-8"),
                headers=headers,
            )
            started = time.perf_counter()
            try:
                with urllib.request.urlopen(http_request, timeout=request.timeout_sec) as response:
                    response_text = response.read().decode("utf-8")
            except urllib.error.HTTPError as exc:
                response_text = exc.read().decode("utf-8", errors="replace")
                response_path.write_text(response_text, encoding="utf-8")
                last_error = RuntimeError(f"{self.provider_name}_http_{exc.code}: {normalized_path(response_path)}")
                total_elapsed_ms += int((time.perf_counter() - started) * 1000)
                continue
            except urllib.error.URLError as exc:
                last_error = RuntimeError(f"{self.provider_name}_request_failed: {exc}")
                total_elapsed_ms += int((time.perf_counter() - started) * 1000)
                continue

            elapsed_ms = int((time.perf_counter() - started) * 1000)
            total_elapsed_ms += elapsed_ms
            response_path.write_text(response_text, encoding="utf-8")

            try:
                response_json = json.loads(response_text)
            except json.JSONDecodeError as exc:
                last_error = RuntimeError(f"invalid_http_json:{exc}: {normalized_path(response_path)}")
                continue
            try:
                raw_text = _extract_message_content(response_json).strip()
            except RuntimeError as exc:
                last_error = RuntimeError(f"{exc}: {normalized_path(response_path)}")
                continue
            try:
                parsed = json.loads(raw_text)
            except json.JSONDecodeError as exc:
                last_error = RuntimeError(f"invalid_json:{exc}: {normalized_path(response_path)}")
                continue
            break
        else:
            raise last_error or RuntimeError(f"{self.provider_name}_unknown_failure")

        artifact_paths = {
            "request": request_path,
            "prompt": prompt_path,
            "schema": schema_path,
            "request_body": request_body_path,
            "response": response_path,
        }
        backend_metadata = {
            "api_base": self.api_base,
            "request_path": normalized_path(request_path),
            "prompt_path": normalized_path(prompt_path),
            "schema_path": normalized_path(schema_path),
            "request_body_path": normalized_path(request_body_path),
            "response_path": normalized_path(response_path),
            "prompt_sha256": sha256_file(prompt_path),
            "schema_sha256": sha256_file(schema_path),
        }
        if self.provider_options:
            backend_metadata["provider_options"] = self.provider_options
        if request.temperature is not None:
            backend_metadata["temperature"] = request.temperature
        if request.max_output_tokens is not None:
            backend_metadata["max_output_tokens"] = request.max_output_tokens
        if request.metadata:
            backend_metadata["request_metadata"] = request.metadata

        return JsonGenerationResult(
            backend_name=self.backend_name,
            provider_name=self.provider_name,
            model=request.model,
            parsed_response=parsed or {},
            raw_text=raw_text,
            provider_response_id=(response_json or {}).get("id"),
            usage=(response_json or {}).get("usage"),
            elapsed_ms=total_elapsed_ms,
            attempt_count=attempt,
            artifact_paths=artifact_paths,
            backend_metadata=backend_metadata,
        )


def resolve_json_backend(
    backend_name: str,
    *,
    repo_root: Path | None = None,
    codex_bin: str = "codex",
    reasoning_effort: str = "medium",
    sandbox: str = "read-only",
    extra_config: list[str] | None = None,
    api_base: str | None = None,
    api_key: str | None = None,
    api_key_env: str | None = None,
    extra_headers: dict[str, str] | None = None,
    provider_options: dict[str, Any] | None = None,
) -> JsonGenerationBackend:
    if backend_name == "codex_cli":
        if repo_root is None:
            raise ValueError("repo_root is required for the codex_cli backend")
        return CodexCliJsonBackend(
            repo_root=repo_root,
            codex_bin=codex_bin,
            reasoning_effort=reasoning_effort,
            sandbox=sandbox,
            extra_config=extra_config,
        )
    if backend_name == "openai":
        return OpenAICompatibleJsonBackend(
            provider_name="openai",
            api_base=api_base or OPENAI_API_BASE,
            api_key=api_key,
            api_key_env=api_key_env or "OPENAI_API_KEY",
            extra_headers=extra_headers,
            provider_options=provider_options,
        )
    if backend_name == "openrouter":
        return OpenAICompatibleJsonBackend(
            provider_name="openrouter",
            api_base=api_base or OPENROUTER_API_BASE,
            api_key=api_key,
            api_key_env=api_key_env or "OPENROUTER_API_KEY",
            extra_headers=extra_headers,
            provider_options=provider_options,
        )
    raise ValueError(f"Unsupported JSON backend: {backend_name}")

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from llm_json_backends import JsonGenerationRequest, JsonGenerationResult, resolve_json_backend
from codex_cli_support_mvp_common import build_stage_backend_record


def _teacher_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "answer",
            "task_type",
            "needs_clarification",
            "clarification_question",
            "escalate",
            "uncertainty_reason",
            "steps",
            "source_chunk_ids",
            "notes",
        ],
        "properties": {
            "answer": {"type": "string"},
            "task_type": {"type": "string"},
            "needs_clarification": {"type": "boolean"},
            "clarification_question": {"type": ["string", "null"]},
            "escalate": {"type": "boolean"},
            "uncertainty_reason": {"type": ["string", "null"]},
            "steps": {"type": "array", "items": {"type": "string"}},
            "source_chunk_ids": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "array", "items": {"type": "string"}},
        },
    }


def _teacher_payload() -> dict:
    return {
        "answer": "Belegte Antwort",
        "task_type": "faq_direct_answer",
        "needs_clarification": False,
        "clarification_question": None,
        "escalate": False,
        "uncertainty_reason": None,
        "steps": [],
        "source_chunk_ids": ["chunk-1"],
        "notes": [],
    }


def test_resolve_json_backend_rejects_unknown_backend() -> None:
    with pytest.raises(ValueError):
        resolve_json_backend("unknown-backend")


def test_codex_cli_backend_runs_and_normalizes_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from llm_json_backends import shutil as llm_shutil
    from llm_json_backends import subprocess as llm_subprocess

    monkeypatch.setattr(llm_shutil, "which", lambda name: r"C:\Tools\codex.exe")

    def fake_run(command: list[str], **kwargs: object):
        output_path = Path(command[command.index("-o") + 1])
        output_path.write_text(json.dumps(_teacher_payload()), encoding="utf-8")

        class Completed:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return Completed()

    monkeypatch.setattr(llm_subprocess, "run", fake_run)

    backend = resolve_json_backend(
        "codex_cli",
        repo_root=tmp_path,
        codex_bin="codex",
        reasoning_effort="medium",
        sandbox="read-only",
    )
    result = backend.generate(
        JsonGenerationRequest(
            model="gpt-5.4",
            prompt_text="prompt",
            response_schema=_teacher_schema(),
            request_payload={"job_id": "job-1"},
            artifact_dir=tmp_path / "artifacts",
            timeout_sec=10,
            max_attempts=1,
        )
    )

    assert result.provider_name == "codex_cli"
    assert result.parsed_response == _teacher_payload()
    assert result.backend_metadata["command"][0] == "codex"
    assert Path(result.backend_metadata["prompt_path"]).name == "prompt.txt"
    assert Path(result.backend_metadata["response_path"]).name == "last_message.json"


def test_build_stage_backend_record_adds_batch_context() -> None:
    result = JsonGenerationResult(
        backend_name="codex_cli",
        provider_name="codex_cli",
        model="gpt-5.4",
        parsed_response={},
        raw_text="{}",
        provider_response_id=None,
        usage=None,
        elapsed_ms=123,
        attempt_count=1,
        artifact_paths={},
        backend_metadata={"prompt_path": "prompt.txt"},
    )

    record = build_stage_backend_record(
        result,
        batch_id="run::batch::0001",
        batch_size=4,
        batch_index=1,
    )

    assert record == {
        "codex_cli": {
            "prompt_path": "prompt.txt",
            "batch_id": "run::batch::0001",
            "batch_size": 4,
            "batch_index": 1,
        }
    }


def test_openrouter_backend_uses_openai_compatible_json_schema(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from llm_json_backends import urllib as llm_urllib

    captured: dict[str, object] = {}

    class FakeResponse:
        def __init__(self, body: str) -> None:
            self._body = body

        def read(self) -> bytes:
            return self._body.encode("utf-8")

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    def fake_urlopen(request, timeout: int):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        response_payload = {
            "id": "or-123",
            "choices": [
                {
                    "message": {
                        "content": json.dumps(_teacher_payload()),
                    }
                }
            ],
            "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
        }
        return FakeResponse(json.dumps(response_payload))

    monkeypatch.setattr(llm_urllib.request, "urlopen", fake_urlopen)

    backend = resolve_json_backend(
        "openrouter",
        api_base="https://openrouter.ai/api/v1",
        api_key="test-token",
        provider_options={
            "order": ["openai", "anthropic"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "zdr": True,
        },
    )
    result = backend.generate(
        JsonGenerationRequest(
            model="openrouter/test-model",
            prompt_text="prompt",
            response_schema=_teacher_schema(),
            request_payload={"job_id": "job-1"},
            artifact_dir=tmp_path / "openrouter",
            timeout_sec=30,
            messages=[{"role": "user", "content": "prompt"}],
            schema_name="teacher_candidate_payload",
            temperature=0.2,
            max_output_tokens=321,
        )
    )

    request_body = captured["body"]
    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-token"
    assert request_body["response_format"]["type"] == "json_schema"
    assert request_body["response_format"]["json_schema"]["name"] == "teacher_candidate_payload"
    assert request_body["response_format"]["json_schema"]["strict"] is True
    assert request_body["temperature"] == 0.2
    assert request_body["max_tokens"] == 321
    assert request_body["provider"] == {
        "order": ["openai", "anthropic"],
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr": True,
    }
    assert "order" not in request_body
    assert "allow_fallbacks" not in request_body
    assert "require_parameters" not in request_body
    assert "data_collection" not in request_body
    assert "zdr" not in request_body
    assert result.provider_name == "openrouter"
    assert result.provider_response_id == "or-123"
    assert result.parsed_response == _teacher_payload()

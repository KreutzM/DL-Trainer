from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from common import find_repo_root, make_parser, read_jsonl, sha256_file, write_json, write_jsonl
from run_teacher_jobs import (
    RAW_RESPONSE_FORMAT_VERSION,
    build_output_from_raw_response,
    build_prompt_payload,
    build_teacher_response_schema,
    filter_jobs,
    load_jobs,
    normalized_path,
)


TRANSFORM_PIPELINE_VERSION = "0.7.0"
RUNNER_CODEX_CLI_MODE = "teacher_runner_codex_cli_v1"


def parse_args() -> Any:
    parser = make_parser(
        "Generate real teacher raw responses via Codex CLI and optionally materialize teacher outputs."
    )
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--raw-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--teacher-run-id", required=True)
    parser.add_argument("--teacher-output")
    parser.add_argument("--teacher-model", default="gpt-5.4")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--reasoning-effort", default="high")
    parser.add_argument("--sandbox", default="read-only")
    parser.add_argument("--job-id", action="append", default=[])
    parser.add_argument("--job-ids-file", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--codex-config", action="append", default=[])
    parser.add_argument("--timeout-sec", type=int, default=600)
    return parser.parse_args()


def safe_slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text)


def build_codex_exec_prompt(job: dict) -> str:
    source_paths = sorted(
        {
            record["normalized_path"]
            for record in job["provenance"]["source_records"]
            if record.get("normalized_path")
        }
    )
    prompt_parts = [
        "Erzeuge einen strukturierten Teacher-Kandidaten fuer genau einen JAWS-DE-Job.",
        "Nutze nur den angegebenen Quellkontext und die referenzierten normalized Dateien.",
        "Erfinde keine Fakten, keine Menuepunkte und keine Tastenkombinationen.",
        "Gib ausschliesslich das sichtbare Endergebnis als JSON gemaess Output-Schema zurueck.",
        "Keine Codeblocks, keine Erklaerungen, keine Chain-of-thought, keine versteckten Zwischenschritte.",
        "Wenn die Quelle fuer eine sichere direkte Antwort nicht reicht, antworte konservativ gemaess task_type.",
        "",
        f"Referenzierte normalized Dateien: {', '.join(source_paths)}",
        "",
        build_prompt_payload(job),
    ]
    return "\n".join(prompt_parts).strip() + "\n"


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


def load_existing_raw_rows(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    rows = read_jsonl(path)
    return {row["job_id"]: row for row in rows}


def build_raw_row(
    *,
    job: dict,
    jobs_path: Path,
    parsed_response: dict,
    raw_text: str,
    teacher_model: str,
    teacher_run_id: str,
    command: list[str],
    artifact_paths: dict[str, Path],
    elapsed_ms: int,
) -> dict:
    return {
        "response_id": f"{teacher_run_id}::{job['job_id']}::response",
        "job_id": job["job_id"],
        "output_id": f"{teacher_run_id}::{job['job_id']}",
        "wave_id": job.get("wave_id"),
        "record_type": job["expected_output_kind"],
        "target_split": job["target_split"],
        "product": job["product"],
        "language": job["language"],
        "task_type": job["task_type"],
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
        "teacher_provider": "codex_cli",
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": job["teacher_prompt_version"],
        "generation_mode": RUNNER_CODEX_CLI_MODE,
        "response_status": "completed",
        "response_format_version": RAW_RESPONSE_FORMAT_VERSION,
        "provider_response_id": None,
        "raw_text": raw_text,
        "parsed_response": parsed_response,
        "usage": {"elapsed_ms": elapsed_ms},
        "codex_cli": {
            "command": command,
            "request_path": normalized_path(artifact_paths["request"]),
            "prompt_path": normalized_path(artifact_paths["prompt"]),
            "schema_path": normalized_path(artifact_paths["schema"]),
            "response_path": normalized_path(artifact_paths["response"]),
            "stdout_path": normalized_path(artifact_paths["stdout"]),
            "stderr_path": normalized_path(artifact_paths["stderr"]),
            "prompt_sha256": sha256_file(artifact_paths["prompt"]),
            "schema_sha256": sha256_file(artifact_paths["schema"]),
        },
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "source_job_path": normalized_path(jobs_path),
            "behavior_spec_path": job["behavior_spec_path"],
            "prompt_template_path": job["prompt_template_path"],
            "source_records": job["provenance"]["source_records"],
        },
    }


def materialize_teacher_outputs(
    jobs: list[dict],
    raw_rows_by_job_id: dict[str, dict],
    raw_output_path: Path,
) -> list[dict]:
    outputs: list[dict] = []
    raw_response_path = normalized_path(raw_output_path)
    for job in jobs:
        raw_row = raw_rows_by_job_id[job["job_id"]]
        output = build_output_from_raw_response(job, raw_row, raw_response_path)
        output["provenance"]["source_job_path"] = normalized_path(Path(raw_row["provenance"]["source_job_path"]))
        outputs.append(output)
    return outputs


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    jobs_path = Path(args.jobs)
    jobs = filter_jobs(load_jobs(jobs_path), set(args.job_id), args.job_ids_file, args.limit)
    artifact_root = Path(args.artifact_dir)
    artifact_root.mkdir(parents=True, exist_ok=True)

    existing_raw_rows = load_existing_raw_rows(Path(args.raw_output)) if args.resume else {}
    generated_rows: list[dict] = []
    skipped_job_ids: list[str] = []
    failures: list[dict[str, str]] = []

    for job in jobs:
        if job["job_id"] in existing_raw_rows:
            generated_rows.append(existing_raw_rows[job["job_id"]])
            skipped_job_ids.append(job["job_id"])
            continue

        job_slug = safe_slug(job["job_id"])
        job_dir = artifact_root / job_slug
        job_dir.mkdir(parents=True, exist_ok=True)

        request_path = job_dir / "request.json"
        prompt_path = job_dir / "prompt.txt"
        schema_path = job_dir / "response_schema.json"
        response_path = job_dir / "last_message.json"
        stdout_path = job_dir / "stdout.txt"
        stderr_path = job_dir / "stderr.txt"

        prompt_text = build_codex_exec_prompt(job)
        schema = build_teacher_response_schema(job["expected_output_kind"], job["task_type"])
        request_payload = {
            "job_id": job["job_id"],
            "teacher_run_id": args.teacher_run_id,
            "teacher_model": args.teacher_model,
            "generation_mode": RUNNER_CODEX_CLI_MODE,
            "expected_output_kind": job["expected_output_kind"],
            "task_type": job["task_type"],
            "source_chunk_ids": job["source_chunk_ids"],
            "source_doc_ids": job["source_doc_ids"],
            "runner_input": job["runner_input"],
            "source_excerpt": job.get("source_excerpt"),
            "fixture_payload": job.get("fixture_payload"),
            "provenance": job["provenance"],
        }
        write_json(request_path, request_payload)
        write_json(schema_path, schema)
        prompt_path.write_text(prompt_text, encoding="utf-8")

        command = build_codex_command(
            codex_bin=args.codex_bin,
            repo_root=repo_root,
            model=args.teacher_model,
            reasoning_effort=args.reasoning_effort,
            sandbox=args.sandbox,
            schema_path=schema_path,
            output_path=response_path,
            extra_config=args.codex_config,
        )

        started = time.perf_counter()
        completed = subprocess.run(
            command,
            input=prompt_text,
            text=True,
            capture_output=True,
            cwd=repo_root,
            timeout=args.timeout_sec,
            encoding="utf-8",
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        stdout_path.write_text(completed.stdout or "", encoding="utf-8")
        stderr_path.write_text(completed.stderr or "", encoding="utf-8")

        if completed.returncode != 0:
            failures.append(
                {
                    "job_id": job["job_id"],
                    "reason": f"codex_exit_{completed.returncode}",
                    "stderr_path": normalized_path(stderr_path),
                }
            )
            continue
        if not response_path.exists():
            failures.append(
                {
                    "job_id": job["job_id"],
                    "reason": "missing_last_message",
                    "stderr_path": normalized_path(stderr_path),
                }
            )
            continue

        raw_text = response_path.read_text(encoding="utf-8").strip()
        try:
            parsed_response = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            failures.append(
                {
                    "job_id": job["job_id"],
                    "reason": f"invalid_json:{exc}",
                    "response_path": normalized_path(response_path),
                }
            )
            continue

        artifact_paths = {
            "request": request_path,
            "prompt": prompt_path,
            "schema": schema_path,
            "response": response_path,
            "stdout": stdout_path,
            "stderr": stderr_path,
        }
        generated_rows.append(
            build_raw_row(
                job=job,
                jobs_path=jobs_path,
                parsed_response=parsed_response,
                raw_text=raw_text,
                teacher_model=args.teacher_model,
                teacher_run_id=args.teacher_run_id,
                command=command,
                artifact_paths=artifact_paths,
                elapsed_ms=elapsed_ms,
            )
        )

    raw_rows_by_job_id = {row["job_id"]: row for row in generated_rows}
    ordered_rows = [raw_rows_by_job_id[job["job_id"]] for job in jobs if job["job_id"] in raw_rows_by_job_id]
    if not ordered_rows:
        raise SystemExit("No raw teacher responses were generated successfully")

    write_jsonl(Path(args.raw_output), ordered_rows)

    materialized_outputs = None
    if args.teacher_output:
        materialized_outputs = materialize_teacher_outputs(jobs=[job for job in jobs if job["job_id"] in raw_rows_by_job_id], raw_rows_by_job_id=raw_rows_by_job_id, raw_output_path=Path(args.raw_output))
        write_jsonl(Path(args.teacher_output), materialized_outputs)

    report = {
        "jobs_path": normalized_path(jobs_path),
        "teacher_run_id": args.teacher_run_id,
        "teacher_model": args.teacher_model,
        "teacher_provider": "codex_cli",
        "generation_mode": RUNNER_CODEX_CLI_MODE,
        "selected_jobs": len(jobs),
        "completed_jobs": len(ordered_rows),
        "skipped_existing_jobs": skipped_job_ids,
        "failed_jobs": failures,
        "raw_output": normalized_path(args.raw_output),
        "teacher_output": normalized_path(args.teacher_output) if args.teacher_output else None,
        "artifact_dir": normalized_path(artifact_root),
        "reasoning_effort": args.reasoning_effort,
        "sandbox": args.sandbox,
    }
    write_json(Path(args.report_output), report)

    print(f"Wrote {len(ordered_rows)} raw teacher responses -> {args.raw_output}")
    if args.teacher_output and materialized_outputs is not None:
        print(f"Wrote {len(materialized_outputs)} teacher outputs -> {args.teacher_output}")
    print(f"Wrote Codex CLI report -> {args.report_output}")


if __name__ == "__main__":
    main()

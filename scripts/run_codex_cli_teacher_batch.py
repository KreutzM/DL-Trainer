from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from common import find_repo_root, make_parser, read_jsonl, write_jsonl
from llm_json_backends import (
    JsonGenerationRequest,
    OPENROUTER_API_BASE,
    build_backend_record,
    provider_name_for_backend,
    resolve_json_backend,
)
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
RUNNER_OPENROUTER_MODE = "teacher_runner_openrouter_v1"


def parse_args() -> Any:
    parser = make_parser(
        "Generate real teacher raw responses via the configured JSON LLM backend and optionally materialize teacher outputs."
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
    parser.add_argument("--llm-backend", choices=["codex_cli", "openrouter"], default="codex_cli")
    parser.add_argument("--openrouter-api-base", default=OPENROUTER_API_BASE)
    parser.add_argument("--openrouter-api-key-env", default="OPENROUTER_API_KEY")
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
    llm_backend: str,
    generation_result: Any,
    elapsed_ms: int,
) -> dict:
    generation_mode = RUNNER_CODEX_CLI_MODE if llm_backend == "codex_cli" else RUNNER_OPENROUTER_MODE
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
        "teacher_provider": provider_name_for_backend(llm_backend),
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": job["teacher_prompt_version"],
        "generation_mode": generation_mode,
        "response_status": "completed",
        "response_format_version": RAW_RESPONSE_FORMAT_VERSION,
        "provider_response_id": generation_result.provider_response_id,
        "raw_text": raw_text,
        "parsed_response": parsed_response,
        "usage": {"elapsed_ms": elapsed_ms},
        **build_backend_record(generation_result),
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
    generation_mode = RUNNER_CODEX_CLI_MODE if args.llm_backend == "codex_cli" else RUNNER_OPENROUTER_MODE

    if args.llm_backend == "codex_cli":
        backend = resolve_json_backend(
            "codex_cli",
            repo_root=repo_root,
            codex_bin=args.codex_bin,
            reasoning_effort=args.reasoning_effort,
            sandbox=args.sandbox,
            extra_config=args.codex_config,
        )
    else:
        backend = resolve_json_backend(
            "openrouter",
            api_base=args.openrouter_api_base,
            api_key_env=args.openrouter_api_key_env,
        )

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

        prompt_text = build_codex_exec_prompt(job)
        schema = build_teacher_response_schema(job["expected_output_kind"], job["task_type"])
        request_payload = {
            "job_id": job["job_id"],
            "teacher_run_id": args.teacher_run_id,
            "teacher_model": args.teacher_model,
            "generation_mode": generation_mode,
            "expected_output_kind": job["expected_output_kind"],
            "task_type": job["task_type"],
            "source_chunk_ids": job["source_chunk_ids"],
            "source_doc_ids": job["source_doc_ids"],
            "runner_input": job["runner_input"],
            "source_excerpt": job.get("source_excerpt"),
            "fixture_payload": job.get("fixture_payload"),
            "provenance": job["provenance"],
        }
        try:
            generation_result = backend.generate(
                JsonGenerationRequest(
                    model=args.teacher_model,
                    prompt_text=prompt_text,
                    response_schema=schema,
                    request_payload=request_payload,
                    artifact_dir=job_dir,
                    timeout_sec=args.timeout_sec,
                )
            )
        except Exception as exc:
            failures.append({"job_id": job["job_id"], "reason": str(exc)})
            continue

        try:
            parsed_response = dict(generation_result.parsed_response)
            raw_text = generation_result.raw_text
        except Exception as exc:
            failures.append(
                {
                    "job_id": job["job_id"],
                    "reason": f"invalid_json:{exc}",
                    "response_path": normalized_path(job_dir),
                }
            )
            continue
        generated_rows.append(
            build_raw_row(
                job=job,
                jobs_path=jobs_path,
                parsed_response=parsed_response,
                raw_text=raw_text,
                teacher_model=args.teacher_model,
                teacher_run_id=args.teacher_run_id,
                llm_backend=args.llm_backend,
                generation_result=generation_result,
                elapsed_ms=generation_result.elapsed_ms,
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
        "teacher_provider": provider_name_for_backend(args.llm_backend),
        "generation_mode": generation_mode,
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

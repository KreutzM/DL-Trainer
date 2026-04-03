from __future__ import annotations

from pathlib import Path
from typing import Any

from codex_cli_support_mvp_common import (
    TRANSFORM_PIPELINE_VERSION,
    USER_SIMULATION_MODE,
    USER_SIMULATION_PROMPT_VERSION,
    add_llm_backend_args,
    build_stage_backend_record,
    build_stage_metrics,
    chunked,
    compact_text,
    generation_mode_for_backend,
    load_repo_text,
    normalized_path,
    repo_root_from_cwd,
    run_stage_json_generation,
    safe_slug,
    stage_provider_name,
    stage_defaults,
)
from common import make_parser, write_json, write_jsonl
from run_teacher_jobs import filter_jobs, load_jobs


def parse_args() -> Any:
    defaults = stage_defaults(USER_SIMULATION_MODE)
    parser = make_parser("Generate real JAWS-DE user simulations via Codex CLI.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--simulator-run-id", required=True)
    parser.add_argument("--simulator-model", default=defaults["model"])
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--reasoning-effort", default=defaults["reasoning_effort"])
    parser.add_argument("--sandbox", default="read-only")
    parser.add_argument("--job-id", action="append", default=[])
    parser.add_argument("--job-ids-file", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--batch-size", type=int, default=defaults["batch_size"])
    parser.add_argument("--max-attempts", type=int, default=defaults["max_attempts"])
    parser.add_argument("--codex-config", action="append", default=[])
    parser.add_argument("--timeout-sec", type=int, default=600)
    add_llm_backend_args(parser)
    return parser.parse_args()


def build_user_simulation_item_schema(job_ids: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "job_id",
            "request_text",
            "user_goal",
            "difficulty",
            "phrasing_style",
            "scenario_summary",
            "notes",
        ],
        "properties": {
            "job_id": {"type": "string", "enum": job_ids},
            "request_text": {"type": "string", "minLength": 1},
            "user_goal": {"type": "string", "minLength": 1},
            "difficulty": {"type": "string", "enum": ["basic", "intermediate", "advanced"]},
            "phrasing_style": {
                "type": "string",
                "enum": ["neutral", "urgent", "uncertain", "task_focused", "frustrated"],
            },
            "scenario_summary": {"type": "string", "minLength": 1},
            "notes": {"type": "array", "items": {"type": "string"}},
        },
    }


def build_user_simulation_schema(batch_jobs: list[dict[str, Any]]) -> dict[str, Any]:
    job_ids = [job["job_id"] for job in batch_jobs]
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["items"],
        "properties": {
            "items": {
                "type": "array",
                "minItems": len(job_ids),
                "maxItems": len(job_ids),
                "items": build_user_simulation_item_schema(job_ids),
            }
        },
    }


def build_prompt(batch_jobs: list[dict[str, Any]], *, repo_root: Path) -> str:
    prompt_template = load_repo_text(repo_root, "prompts/teacher/jaws_de_user_simulation.md")
    prompt_parts = [
        prompt_template,
        "",
        "## Batch-Regeln",
        "- Erzeuge fuer jede job_id genau eine eigenstaendige Nutzeranfrage.",
        "- Uebernimm job_id im JSON exakt.",
        "- Antworte fuer alle Faelle gesammelt in einem JSON-Objekt mit items[].",
        "- Verwende nur den pro Fall gezeigten Quellkontext.",
        "",
        "## Faelle",
    ]
    for job in batch_jobs:
        prompt_parts.extend(
            [
                f"### job_id: {job['job_id']}",
                f"- task_type: {job['task_type']}",
                f"- expected_output_kind: {job['expected_output_kind']}",
                f"- source_doc_ids: {', '.join(job['source_doc_ids'])}",
                f"- source_chunk_ids: {', '.join(job['source_chunk_ids'])}",
                f"- chunk_type: {job.get('chunk_type') or 'n/a'}",
                f"- section_path_text: {job.get('section_path_text') or 'n/a'}",
                f"- spaeteres supportziel: {str(job.get('fixture_payload', {}).get('expected_behavior') or 'n/a')}",
                "- seed_request: " + compact_text(job["runner_input"]["user_message"]),
                "- source_excerpt:",
                compact_text(job.get("source_excerpt") or "") or "(leer)",
                "",
            ]
        )
    return "\n".join(prompt_parts).strip() + "\n"


def build_row(
    *,
    job: dict,
    jobs_path: Path,
    parsed: dict[str, Any],
    simulator_model: str,
    simulator_run_id: str,
    llm_backend: str,
    generation_result: Any,
    elapsed_ms: int,
    batch_id: str,
    batch_size: int,
    batch_index: int,
    attempt_count: int,
    prompt_chars: int,
    source_excerpt_chars: int,
) -> dict[str, Any]:
    return {
        "simulation_id": f"{simulator_run_id}::{job['job_id']}::simulation",
        "job_id": job["job_id"],
        "wave_id": job.get("wave_id"),
        "target_split": job["target_split"],
        "expected_output_kind": job["expected_output_kind"],
        "task_type": job["task_type"],
        "product": job["product"],
        "language": job["language"],
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
        "simulator_provider": stage_provider_name(llm_backend),
        "simulator_model": simulator_model,
        "simulator_run_id": simulator_run_id,
        "simulator_prompt_version": USER_SIMULATION_PROMPT_VERSION,
        "generation_mode": generation_mode_for_backend(USER_SIMULATION_MODE, llm_backend),
        "simulation_status": "completed",
        "request_text": parsed["request_text"].strip(),
        "user_goal": parsed["user_goal"].strip(),
        "difficulty": parsed["difficulty"],
        "phrasing_style": parsed["phrasing_style"],
        "scenario_summary": parsed["scenario_summary"].strip(),
        "notes": parsed.get("notes", []),
        "usage": {
            "elapsed_ms": elapsed_ms,
            "batch_elapsed_ms": elapsed_ms * batch_size,
            "batch_size": batch_size,
            "attempt_count": attempt_count,
            "prompt_chars": prompt_chars,
            "source_excerpt_chars": source_excerpt_chars,
        },
        **build_stage_backend_record(
            generation_result,
            batch_id=batch_id,
            batch_size=batch_size,
            batch_index=batch_index,
        ),
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "source_job_path": normalized_path(jobs_path),
            "behavior_spec_path": job["behavior_spec_path"],
            "prompt_template_path": "prompts/teacher/jaws_de_user_simulation.md",
            "source_records": job["provenance"]["source_records"],
        },
    }


def main() -> None:
    args = parse_args()
    repo_root = repo_root_from_cwd()
    jobs_path = Path(args.jobs)
    jobs = filter_jobs(load_jobs(jobs_path), set(args.job_id), args.job_ids_file, args.limit)
    artifact_root = Path(args.artifact_dir)
    output_path = Path(args.output)
    existing_rows = {}
    if args.resume and output_path.exists():
        from common import read_jsonl

        existing_rows = {row["job_id"]: row for row in read_jsonl(output_path)}

    rows: list[dict[str, Any]] = []
    skipped: list[str] = []
    failures: list[dict[str, str]] = []
    pending_jobs: list[dict[str, Any]] = []
    for job in jobs:
        if job["job_id"] in existing_rows:
            rows.append(existing_rows[job["job_id"]])
            skipped.append(job["job_id"])
        else:
            pending_jobs.append(job)

    total_elapsed_ms = 0
    total_prompt_chars = 0
    total_source_excerpt_chars = 0
    total_retry_attempts = 0
    executed_batches = 0
    completed_batches = 0

    for batch_index, batch_jobs in enumerate(chunked(pending_jobs, args.batch_size), start=1):
        batch_id = f"{args.simulator_run_id}::batch::{batch_index:04d}"
        job_dir = artifact_root / safe_slug(batch_id)
        prompt_text = build_prompt(batch_jobs, repo_root=repo_root)
        prompt_chars = len(prompt_text)
        source_excerpt_chars = sum(len(compact_text(job.get("source_excerpt") or "")) for job in batch_jobs)
        total_prompt_chars += prompt_chars
        total_source_excerpt_chars += source_excerpt_chars
        executed_batches += 1
        request_payload = {
            "batch_id": batch_id,
            "job_ids": [job["job_id"] for job in batch_jobs],
            "simulator_run_id": args.simulator_run_id,
            "simulator_model": args.simulator_model,
            "generation_mode": generation_mode_for_backend(USER_SIMULATION_MODE, args.llm_backend),
            "jobs": [
                {
                    "job_id": job["job_id"],
                    "task_type": job["task_type"],
                    "source_chunk_ids": job["source_chunk_ids"],
                    "source_doc_ids": job["source_doc_ids"],
                    "source_excerpt": job.get("source_excerpt"),
                    "runner_input": job["runner_input"],
                    "provenance": job["provenance"],
                }
                for job in batch_jobs
            ],
        }
        try:
            generation_result = run_stage_json_generation(
                llm_backend=args.llm_backend,
                repo_root=repo_root,
                model=args.simulator_model,
                prompt_text=prompt_text,
                schema=build_user_simulation_schema(batch_jobs),
                artifact_dir=job_dir,
                request_payload=request_payload,
                timeout_sec=args.timeout_sec,
                max_attempts=args.max_attempts,
                reasoning_effort=args.reasoning_effort,
                sandbox=args.sandbox,
                codex_bin=args.codex_bin,
                extra_config=args.codex_config,
                openrouter_api_base=args.openrouter_api_base,
                openrouter_api_key_env=args.openrouter_api_key_env,
            )
        except Exception as exc:
            for job in batch_jobs:
                failures.append({"job_id": job["job_id"], "reason": str(exc)})
            continue

        items = generation_result.parsed_response.get("items")
        if not isinstance(items, list):
            for job in batch_jobs:
                failures.append({"job_id": job["job_id"], "reason": "batch_response_missing_items"})
            continue
        items_by_job_id = {item.get("job_id"): item for item in items if isinstance(item, dict) and item.get("job_id")}
        expected_job_ids = {job["job_id"] for job in batch_jobs}
        if set(items_by_job_id) != expected_job_ids:
            missing = sorted(expected_job_ids - set(items_by_job_id))
            extra = sorted(set(items_by_job_id) - expected_job_ids)
            reason = "batch_response_job_id_mismatch"
            if missing:
                reason += f":missing={','.join(missing)}"
            if extra:
                reason += f":extra={','.join(extra)}"
            for job in batch_jobs:
                failures.append({"job_id": job["job_id"], "reason": reason})
            continue

        completed_batches += 1
        total_elapsed_ms += generation_result.elapsed_ms
        total_retry_attempts += max(0, generation_result.attempt_count - 1)
        elapsed_share_ms = max(1, round(generation_result.elapsed_ms / len(batch_jobs)))
        prompt_share_chars = max(1, round(prompt_chars / len(batch_jobs)))
        source_excerpt_share_chars = max(0, round(source_excerpt_chars / len(batch_jobs)))
        for job in batch_jobs:
            rows.append(
                build_row(
                    job=job,
                    jobs_path=jobs_path,
                    parsed=items_by_job_id[job["job_id"]],
                    simulator_model=args.simulator_model,
                    simulator_run_id=args.simulator_run_id,
                    llm_backend=args.llm_backend,
                    generation_result=generation_result,
                    elapsed_ms=elapsed_share_ms,
                    batch_id=batch_id,
                    batch_size=len(batch_jobs),
                    batch_index=batch_index,
                    attempt_count=generation_result.attempt_count,
                    prompt_chars=prompt_share_chars,
                    source_excerpt_chars=source_excerpt_share_chars,
                )
            )

    if not rows:
        raise SystemExit("No user simulations were generated successfully")

    selected_job_ids = {job["job_id"] for job in jobs}
    ordered_rows = [row for row in rows if row["job_id"] in selected_job_ids]
    write_jsonl(output_path, ordered_rows)
    report = {
        "jobs_path": normalized_path(jobs_path),
        "simulator_run_id": args.simulator_run_id,
        "simulator_model": args.simulator_model,
        "simulator_provider": stage_provider_name(args.llm_backend),
        "generation_mode": generation_mode_for_backend(USER_SIMULATION_MODE, args.llm_backend),
        "selected_jobs": len(jobs),
        "completed_jobs": len(ordered_rows),
        "skipped_existing_jobs": skipped,
        "failed_jobs": failures,
        "output": normalized_path(output_path),
        "artifact_dir": normalized_path(artifact_root),
        "runtime": build_stage_metrics(
            selected_jobs=len(jobs),
            completed_jobs=len(ordered_rows),
            skipped_existing_jobs=skipped,
            failed_jobs=failures,
            batch_size=args.batch_size,
            executed_batches=executed_batches,
            completed_batches=completed_batches,
            total_elapsed_ms=total_elapsed_ms,
            total_prompt_chars=total_prompt_chars,
            total_source_excerpt_chars=total_source_excerpt_chars,
            total_retry_attempts=total_retry_attempts,
        ),
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(ordered_rows)} user simulations -> {args.output}")
    print(f"Wrote user simulation report -> {args.report_output}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from codex_cli_support_mvp_common import (
    ANSWER_MODE,
    ANSWER_PROMPT_VERSION,
    TRANSFORM_PIPELINE_VERSION,
    add_llm_backend_args,
    add_llm_profile_args,
    build_stage_backend_record,
    build_stage_metrics,
    chunked,
    compact_text,
    generation_mode_for_backend,
    load_repo_text,
    normalized_path,
    repo_root_from_cwd,
    resolve_stage_runtime_settings,
    run_stage_json_generation,
    safe_slug,
    stage_provider_name,
    stage_defaults,
)
from common import make_parser, read_jsonl, write_json, write_jsonl
from run_teacher_jobs import (
    RAW_RESPONSE_FORMAT_VERSION,
    build_output_from_raw_response_with_user_request,
    build_teacher_response_schema,
    filter_jobs,
    load_jobs,
)


def parse_args() -> Any:
    defaults = stage_defaults(ANSWER_MODE)
    parser = make_parser("Generate real JAWS-DE support answers via Codex CLI from simulated users.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--user-simulations", required=True)
    parser.add_argument("--raw-output", required=True)
    parser.add_argument("--teacher-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--teacher-run-id", required=True)
    parser.add_argument("--teacher-model", default=defaults["model"])
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
    add_llm_profile_args(parser)
    return parser.parse_args()


def build_batch_teacher_response_schema(batch_jobs: list[dict[str, Any]]) -> dict[str, Any]:
    task_types = sorted({job["task_type"] for job in batch_jobs})
    expected_output_kinds = {job["expected_output_kind"] for job in batch_jobs}
    if len(expected_output_kinds) != 1:
        raise SystemExit("Answer batching requires a uniform expected_output_kind per batch")
    expected_output_kind = next(iter(expected_output_kinds))
    item_properties: dict[str, Any] = {
        "job_id": {"type": "string", "enum": [job["job_id"] for job in batch_jobs]},
        "task_type": {"type": "string", "enum": task_types},
        "answer": {"type": "string", "minLength": 1},
        "needs_clarification": {"type": "boolean"},
        "clarification_question": {"type": ["string", "null"]},
        "escalate": {"type": "boolean"},
        "uncertainty_reason": {"type": ["string", "null"]},
        "steps": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
        "source_chunk_ids": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 1},
        },
        "notes": {
            "type": "array",
            "items": {"type": "string"},
        },
    }
    required = [
        "job_id",
        "answer",
        "task_type",
        "needs_clarification",
        "clarification_question",
        "escalate",
        "uncertainty_reason",
        "steps",
        "source_chunk_ids",
        "notes",
    ]
    if expected_output_kind == "eval_case":
        item_properties.update(
            {
                "case_description": {"type": "string", "minLength": 1},
                "expected_behavior": {"type": "string", "minLength": 1},
                "reference_answer": {"type": "string", "minLength": 1},
                "rubric": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["must_include", "must_not_include", "style", "scoring_notes"],
                    "properties": {
                        "must_include": {"type": "array", "items": {"type": "string"}},
                        "must_not_include": {"type": "array", "items": {"type": "string"}},
                        "style": {"type": "string", "minLength": 1},
                        "scoring_notes": {"type": ["string", "null"]},
                    },
                },
            }
        )
        required.extend(["case_description", "expected_behavior", "reference_answer", "rubric"])
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["items"],
        "properties": {
            "items": {
                "type": "array",
                "minItems": len(batch_jobs),
                "maxItems": len(batch_jobs),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": required,
                    "properties": item_properties,
                },
            }
        },
    }


def answer_contract_for_task(task_type: str) -> str:
    if task_type == "clarification":
        return (
            "needs_clarification=true; clarification_question genau eine fokussierte Rueckfrage; "
            "answer nur diese Rueckfrage und mit '?'; escalate=false; steps=[]"
        )
    if task_type == "uncertainty_escalation":
        return (
            "escalate=true; uncertainty_reason kurz nennen; Antwort muss Evidenzgrenze sichtbar machen; "
            "needs_clarification=false"
        )
    if task_type == "step_by_step":
        return "steps nur mit echten Schritten aus der Quelle fuellen; keine zweite oder widerspruechliche Schrittfolge"
    if task_type == "troubleshooting":
        return "symptombezogen antworten; dokumentierte Bedingung, Pruefung oder Abhilfe klar benennen"
    return "direkte, dokumentationsgebundene Antwort ohne unnoetige Vorrede"


def build_prompt(batch_jobs: list[dict[str, Any]], simulations: dict[str, dict[str, Any]], *, repo_root: Path) -> str:
    prompt_template = load_repo_text(repo_root, "prompts/teacher/jaws_de_support_answer_mvp.md")
    prompt_parts = [
        prompt_template,
        "",
        "## Batch-Regeln",
        "- Erzeuge fuer jede job_id genau eine dokumentationsgebundene Support-Antwort.",
        "- Gib alle Ergebnisse gesammelt in einem JSON-Objekt mit items[] zurueck.",
        "- Uebernimm job_id und task_type je Fall exakt.",
        "- Antworte nur auf die gegebene Nutzeranfrage und nur mit belegtem Quellinhalt.",
        "",
        "## Faelle",
    ]
    for job in batch_jobs:
        user_simulation = simulations[job["job_id"]]
        prompt_parts.extend(
            [
                f"### job_id: {job['job_id']}",
                f"- task_type: {job['task_type']}",
                f"- expected_output_kind: {job['expected_output_kind']}",
                f"- target_split: {job['target_split']}",
                f"- source_doc_ids: {', '.join(job['source_doc_ids'])}",
                f"- source_chunk_ids: {', '.join(job['source_chunk_ids'])}",
                f"- chunk_type: {job.get('chunk_type') or 'n/a'}",
                f"- section_path_text: {job.get('section_path_text') or 'n/a'}",
                f"- difficulty: {user_simulation['difficulty']}",
                f"- phrasing_style: {user_simulation['phrasing_style']}",
                f"- user_goal: {user_simulation['user_goal']}",
                f"- output_contract: {answer_contract_for_task(job['task_type'])}",
                "- user_request:",
                compact_text(user_simulation["request_text"]),
                "- expected_behavior:",
                str(job.get("fixture_payload", {}).get("expected_behavior") or "n/a"),
                "- source_excerpt:",
                compact_text(job.get("source_excerpt") or "") or "(leer)",
                "",
            ]
        )
    return "\n".join(prompt_parts).strip() + "\n"


def build_raw_row(
    *,
    job: dict,
    jobs_path: Path,
    user_simulation: dict,
    parsed_response: dict[str, Any],
    raw_text: str,
    teacher_model: str,
    teacher_run_id: str,
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
        "teacher_provider": stage_provider_name(llm_backend),
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": ANSWER_PROMPT_VERSION,
        "generation_mode": generation_mode_for_backend(ANSWER_MODE, llm_backend),
        "response_status": "completed",
        "response_format_version": RAW_RESPONSE_FORMAT_VERSION,
        "provider_response_id": generation_result.provider_response_id,
        "raw_text": raw_text,
        "parsed_response": parsed_response,
        "usage": {
            "elapsed_ms": elapsed_ms,
            "batch_elapsed_ms": elapsed_ms * batch_size,
            "batch_size": batch_size,
            "attempt_count": attempt_count,
            "prompt_chars": prompt_chars,
            "source_excerpt_chars": source_excerpt_chars,
        },
        "simulated_user": {
            "simulation_id": user_simulation["simulation_id"],
            "request_text": user_simulation["request_text"],
            "difficulty": user_simulation["difficulty"],
            "phrasing_style": user_simulation["phrasing_style"],
            "simulator_provider": user_simulation["simulator_provider"],
            "simulator_model": user_simulation["simulator_model"],
            "simulator_run_id": user_simulation["simulator_run_id"],
            "simulator_prompt_version": user_simulation["simulator_prompt_version"],
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
            "prompt_template_path": "prompts/teacher/jaws_de_support_answer_mvp.md",
            "source_records": job["provenance"]["source_records"],
        },
    }


def attach_simulated_user(output: dict[str, Any], user_simulation: dict[str, Any]) -> None:
    payload = {
        "simulation_id": user_simulation["simulation_id"],
        "request_text": user_simulation["request_text"],
        "difficulty": user_simulation["difficulty"],
        "phrasing_style": user_simulation["phrasing_style"],
        "user_goal": user_simulation["user_goal"],
        "scenario_summary": user_simulation["scenario_summary"],
        "simulator_provider": user_simulation["simulator_provider"],
        "simulator_model": user_simulation["simulator_model"],
        "simulator_run_id": user_simulation["simulator_run_id"],
        "simulator_prompt_version": user_simulation["simulator_prompt_version"],
    }
    output["simulated_user"] = payload
    candidate = output["candidate"]
    if output["record_type"] == "sft_sample":
        candidate.setdefault("meta", {})
        candidate["meta"]["simulated_user"] = payload
    else:
        candidate["simulated_user"] = payload


def main() -> None:
    args = parse_args()
    repo_root = repo_root_from_cwd()
    runtime = resolve_stage_runtime_settings(
        args,
        repo_root=repo_root,
        stage_mode=ANSWER_MODE,
        model_arg_name="teacher_model",
    )
    jobs_path = Path(args.jobs)
    jobs = filter_jobs(load_jobs(jobs_path), set(args.job_id), args.job_ids_file, args.limit)
    simulations = {row["job_id"]: row for row in read_jsonl(Path(args.user_simulations))}
    missing_simulations = [job["job_id"] for job in jobs if job["job_id"] not in simulations]
    if missing_simulations:
        raise SystemExit("Missing user simulations for job IDs: " + ", ".join(missing_simulations))

    raw_output_path = Path(args.raw_output)
    teacher_output_path = Path(args.teacher_output)
    existing_raw = {}
    if args.resume and raw_output_path.exists():
        existing_raw = {row["job_id"]: row for row in read_jsonl(raw_output_path)}

    raw_rows: list[dict[str, Any]] = []
    teacher_outputs: list[dict[str, Any]] = []
    skipped: list[str] = []
    failures: list[dict[str, str]] = []
    artifact_root = Path(args.artifact_dir)
    pending_jobs: list[dict[str, Any]] = []
    for job in jobs:
        simulation = simulations[job["job_id"]]
        if job["job_id"] in existing_raw:
            raw_row = existing_raw[job["job_id"]]
            raw_rows.append(raw_row)
            output = build_output_from_raw_response_with_user_request(
                job,
                raw_row,
                normalized_path(raw_output_path),
                user_message=simulation["request_text"],
            )
            attach_simulated_user(output, simulation)
            teacher_outputs.append(output)
            skipped.append(job["job_id"])
        else:
            pending_jobs.append(job)

    total_elapsed_ms = 0
    total_prompt_chars = 0
    total_source_excerpt_chars = 0
    total_retry_attempts = 0
    executed_batches = 0
    completed_batches = 0

    pending_groups: dict[str, list[dict[str, Any]]] = {}
    for job in pending_jobs:
        pending_groups.setdefault(job["expected_output_kind"], []).append(job)

    batch_index = 0
    for expected_output_kind, grouped_jobs in pending_groups.items():
        for batch_jobs in chunked(grouped_jobs, runtime.batch_size):
            batch_index += 1
            batch_id = f"{args.teacher_run_id}::batch::{expected_output_kind}::{batch_index:04d}"
            job_dir = artifact_root / safe_slug(batch_id)
            prompt_text = build_prompt(batch_jobs, simulations, repo_root=repo_root)
            prompt_chars = len(prompt_text)
            source_excerpt_chars = sum(len(compact_text(job.get("source_excerpt") or "")) for job in batch_jobs)
            total_prompt_chars += prompt_chars
            total_source_excerpt_chars += source_excerpt_chars
            executed_batches += 1
            request_payload = {
                "batch_id": batch_id,
                "job_ids": [job["job_id"] for job in batch_jobs],
                "teacher_run_id": args.teacher_run_id,
                "teacher_model": runtime.model,
                "generation_mode": generation_mode_for_backend(ANSWER_MODE, runtime.llm_backend),
                "expected_output_kind": expected_output_kind,
                "jobs": [
                    {
                        "job_id": job["job_id"],
                        "task_type": job["task_type"],
                        "source_chunk_ids": job["source_chunk_ids"],
                        "source_doc_ids": job["source_doc_ids"],
                        "user_simulation": simulations[job["job_id"]],
                        "source_excerpt": job.get("source_excerpt"),
                        "provenance": job["provenance"],
                    }
                    for job in batch_jobs
                ],
            }
            try:
                generation_result = run_stage_json_generation(
                    llm_backend=runtime.llm_backend,
                    repo_root=repo_root,
                    model=runtime.model,
                    prompt_text=prompt_text,
                    schema=build_batch_teacher_response_schema(batch_jobs),
                    artifact_dir=job_dir,
                    request_payload=request_payload,
                    timeout_sec=runtime.timeout_sec,
                    max_attempts=runtime.max_attempts,
                    reasoning_effort=runtime.reasoning_effort,
                    sandbox=runtime.sandbox,
                    codex_bin=runtime.codex_bin,
                    extra_config=runtime.codex_config,
                    openrouter_api_base=runtime.openrouter_api_base,
                    openrouter_api_key_env=runtime.openrouter_api_key_env,
                    openrouter_extra_headers=runtime.openrouter_extra_headers,
                    openrouter_provider_options=runtime.openrouter_provider_options,
                    metadata=runtime.profile_metadata(),
                    temperature=runtime.temperature,
                    max_output_tokens=runtime.max_output_tokens,
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
                simulation = simulations[job["job_id"]]
                item_parsed = dict(items_by_job_id[job["job_id"]])
                item_parsed.pop("job_id", None)
                raw_row = build_raw_row(
                    job=job,
                    jobs_path=jobs_path,
                    user_simulation=simulation,
                    parsed_response=item_parsed,
                    raw_text=json.dumps(item_parsed, ensure_ascii=False),
                    teacher_model=runtime.model,
                    teacher_run_id=args.teacher_run_id,
                    llm_backend=runtime.llm_backend,
                    generation_result=generation_result,
                    elapsed_ms=elapsed_share_ms,
                    batch_id=batch_id,
                    batch_size=len(batch_jobs),
                    batch_index=batch_index,
                    attempt_count=generation_result.attempt_count,
                    prompt_chars=prompt_share_chars,
                    source_excerpt_chars=source_excerpt_share_chars,
                )
                raw_rows.append(raw_row)
                output = build_output_from_raw_response_with_user_request(
                    job,
                    raw_row,
                    normalized_path(raw_output_path),
                    user_message=simulation["request_text"],
                )
                attach_simulated_user(output, simulation)
                teacher_outputs.append(output)

    if not raw_rows:
        raise SystemExit("No support answers were generated successfully")

    raw_rows_by_job = {row["job_id"]: row for row in raw_rows}
    outputs_by_job = {row["job_id"]: row for row in teacher_outputs}
    ordered_raw_rows = [raw_rows_by_job[job["job_id"]] for job in jobs if job["job_id"] in raw_rows_by_job]
    ordered_outputs = [outputs_by_job[job["job_id"]] for job in jobs if job["job_id"] in outputs_by_job]
    write_jsonl(raw_output_path, ordered_raw_rows)
    write_jsonl(teacher_output_path, ordered_outputs)
    report = {
        "jobs_path": normalized_path(jobs_path),
        "user_simulations": normalized_path(args.user_simulations),
        "teacher_run_id": args.teacher_run_id,
        "teacher_model": runtime.model,
        "teacher_provider": stage_provider_name(runtime.llm_backend),
        "generation_mode": generation_mode_for_backend(ANSWER_MODE, runtime.llm_backend),
        "selected_jobs": len(jobs),
        "completed_jobs": len(ordered_raw_rows),
        "skipped_existing_jobs": skipped,
        "failed_jobs": failures,
        "raw_output": normalized_path(raw_output_path),
        "teacher_output": normalized_path(teacher_output_path),
        "artifact_dir": normalized_path(artifact_root),
        "runtime": build_stage_metrics(
            selected_jobs=len(jobs),
            completed_jobs=len(ordered_raw_rows),
            skipped_existing_jobs=skipped,
            failed_jobs=failures,
            batch_size=runtime.batch_size,
            executed_batches=executed_batches,
            completed_batches=completed_batches,
            total_elapsed_ms=total_elapsed_ms,
            total_prompt_chars=total_prompt_chars,
            total_source_excerpt_chars=total_source_excerpt_chars,
            total_retry_attempts=total_retry_attempts,
        ),
    }
    if runtime.profile_metadata():
        report["llm_profile"] = runtime.profile_metadata()
        report["llm_profile_runtime"] = runtime.report_summary()
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(ordered_raw_rows)} raw teacher responses -> {args.raw_output}")
    print(f"Wrote {len(ordered_outputs)} teacher outputs -> {args.teacher_output}")
    print(f"Wrote answer report -> {args.report_output}")


if __name__ == "__main__":
    main()

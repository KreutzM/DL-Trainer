from __future__ import annotations

from pathlib import Path
from typing import Any

from codex_cli_support_mvp_common import (
    ANSWER_MODE,
    ANSWER_PROMPT_VERSION,
    TRANSFORM_PIPELINE_VERSION,
    build_codex_cli_meta,
    load_repo_text,
    normalized_path,
    repo_root_from_cwd,
    run_codex_json_generation,
    safe_slug,
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
    parser = make_parser("Generate real JAWS-DE support answers via Codex CLI from simulated users.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--user-simulations", required=True)
    parser.add_argument("--raw-output", required=True)
    parser.add_argument("--teacher-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--teacher-run-id", required=True)
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


def build_prompt(job: dict, user_simulation: dict, *, repo_root: Path) -> str:
    behavior_spec = load_repo_text(repo_root, job["behavior_spec_path"])
    prompt_template = load_repo_text(repo_root, "prompts/teacher/jaws_de_support_answer_mvp.md")
    source_paths = sorted(
        {
            record["normalized_path"]
            for record in job["provenance"]["source_records"]
            if record.get("normalized_path")
        }
    )
    prompt_parts = [
        prompt_template,
        "",
        "## Support-Verhaltensbasis",
        behavior_spec,
        "",
        "## Fallkontext",
        f"- task_type: {job['task_type']}",
        f"- expected_output_kind: {job['expected_output_kind']}",
        f"- target_split: {job['target_split']}",
        f"- source_doc_ids: {', '.join(job['source_doc_ids'])}",
        f"- source_chunk_ids: {', '.join(job['source_chunk_ids'])}",
        "",
        "## Simulierte Nutzeranfrage",
        f"- difficulty: {user_simulation['difficulty']}",
        f"- phrasing_style: {user_simulation['phrasing_style']}",
        f"- user_goal: {user_simulation['user_goal']}",
        user_simulation["request_text"],
        "",
        "## Referenzierte normalized Dateien",
        ", ".join(source_paths),
        "",
        "## Quellauszug",
        job.get("source_excerpt") or "",
        "",
        "## Erwartetes Verhalten",
        str(job.get("fixture_payload", {}).get("expected_behavior") or "n/a"),
        "",
        "## Ausgabehinweis",
        "Die Antwort muss exakt zu der simulierten Nutzeranfrage passen und darf nur dokumentierte Inhalte verwenden.",
    ]
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
    command: list[str],
    artifact_paths: dict[str, Path],
    elapsed_ms: int,
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
        "teacher_provider": "codex_cli",
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": ANSWER_PROMPT_VERSION,
        "generation_mode": ANSWER_MODE,
        "response_status": "completed",
        "response_format_version": RAW_RESPONSE_FORMAT_VERSION,
        "provider_response_id": None,
        "raw_text": raw_text,
        "parsed_response": parsed_response,
        "usage": {"elapsed_ms": elapsed_ms},
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
        "codex_cli": build_codex_cli_meta(command=command, artifact_paths=artifact_paths),
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
            continue

        job_dir = artifact_root / safe_slug(job["job_id"])
        prompt_text = build_prompt(job, simulation, repo_root=repo_root)
        schema = build_teacher_response_schema(job["expected_output_kind"], job["task_type"])
        request_payload = {
            "job_id": job["job_id"],
            "teacher_run_id": args.teacher_run_id,
            "teacher_model": args.teacher_model,
            "generation_mode": ANSWER_MODE,
            "task_type": job["task_type"],
            "source_chunk_ids": job["source_chunk_ids"],
            "source_doc_ids": job["source_doc_ids"],
            "user_simulation": simulation,
            "source_excerpt": job.get("source_excerpt"),
            "provenance": job["provenance"],
        }
        try:
            parsed, raw_text, artifact_paths, command, elapsed_ms = run_codex_json_generation(
                codex_bin=args.codex_bin,
                repo_root=repo_root,
                model=args.teacher_model,
                reasoning_effort=args.reasoning_effort,
                sandbox=args.sandbox,
                schema=schema,
                prompt_text=prompt_text,
                artifact_dir=job_dir,
                request_payload=request_payload,
                extra_config=args.codex_config,
                timeout_sec=args.timeout_sec,
            )
        except Exception as exc:
            failures.append({"job_id": job["job_id"], "reason": str(exc)})
            continue
        raw_row = build_raw_row(
            job=job,
            jobs_path=jobs_path,
            user_simulation=simulation,
            parsed_response=parsed,
            raw_text=raw_text,
            teacher_model=args.teacher_model,
            teacher_run_id=args.teacher_run_id,
            command=command,
            artifact_paths=artifact_paths,
            elapsed_ms=elapsed_ms,
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
        "teacher_model": args.teacher_model,
        "teacher_provider": "codex_cli",
        "generation_mode": ANSWER_MODE,
        "selected_jobs": len(jobs),
        "completed_jobs": len(ordered_raw_rows),
        "skipped_existing_jobs": skipped,
        "failed_jobs": failures,
        "raw_output": normalized_path(raw_output_path),
        "teacher_output": normalized_path(teacher_output_path),
        "artifact_dir": normalized_path(artifact_root),
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(ordered_raw_rows)} raw teacher responses -> {args.raw_output}")
    print(f"Wrote {len(ordered_outputs)} teacher outputs -> {args.teacher_output}")
    print(f"Wrote answer report -> {args.report_output}")


if __name__ == "__main__":
    main()

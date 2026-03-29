from __future__ import annotations

from pathlib import Path
from typing import Any

from codex_cli_support_mvp_common import (
    TRANSFORM_PIPELINE_VERSION,
    USER_SIMULATION_MODE,
    USER_SIMULATION_PROMPT_VERSION,
    build_codex_cli_meta,
    load_repo_text,
    normalized_path,
    repo_root_from_cwd,
    run_codex_json_generation,
    safe_slug,
)
from common import make_parser, write_json, write_jsonl
from run_teacher_jobs import filter_jobs, load_jobs


def parse_args() -> Any:
    parser = make_parser("Generate real JAWS-DE user simulations via Codex CLI.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--simulator-run-id", required=True)
    parser.add_argument("--simulator-model", default="gpt-5.4")
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


def build_user_simulation_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "request_text",
            "user_goal",
            "difficulty",
            "phrasing_style",
            "scenario_summary",
            "notes",
        ],
        "properties": {
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


def build_prompt(job: dict, *, repo_root: Path) -> str:
    behavior_spec = load_repo_text(repo_root, job["behavior_spec_path"])
    prompt_template = load_repo_text(repo_root, "prompts/teacher/jaws_de_user_simulation.md")
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
        "## Kontext",
        f"- task_type: {job['task_type']}",
        f"- expected_output_kind: {job['expected_output_kind']}",
        f"- product: {job['product']}",
        f"- language: {job['language']}",
        f"- source_doc_ids: {', '.join(job['source_doc_ids'])}",
        f"- source_chunk_ids: {', '.join(job['source_chunk_ids'])}",
        f"- selection_reason: {job.get('selection_reason') or 'n/a'}",
        f"- chunk_type: {job.get('chunk_type') or 'n/a'}",
        f"- section_path_text: {job.get('section_path_text') or 'n/a'}",
        "",
        "## Support-Verhaltensbasis",
        behavior_spec,
        "",
        "## Referenzierte normalized Dateien",
        ", ".join(source_paths),
        "",
        "## Legacy Seed Request",
        "Die folgende Seed-Frage dient nur als grobe Orientierung und darf nicht einfach kopiert werden.",
        job["runner_input"]["user_message"],
        "",
        "## Quellauszug",
        job.get("source_excerpt") or "",
        "",
        "## Erwartetes Verhalten des spaeteren Supportfalls",
        str(job.get("fixture_payload", {}).get("expected_behavior") or "n/a"),
        "",
        "## Ausgabehinweis",
        "Erzeuge genau eine realistische neue Nutzeranfrage fuer diesen Fall.",
    ]
    return "\n".join(prompt_parts).strip() + "\n"


def build_row(
    *,
    job: dict,
    jobs_path: Path,
    parsed: dict[str, Any],
    simulator_model: str,
    simulator_run_id: str,
    command: list[str],
    artifact_paths: dict[str, Path],
    elapsed_ms: int,
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
        "simulator_provider": "codex_cli",
        "simulator_model": simulator_model,
        "simulator_run_id": simulator_run_id,
        "simulator_prompt_version": USER_SIMULATION_PROMPT_VERSION,
        "generation_mode": USER_SIMULATION_MODE,
        "simulation_status": "completed",
        "request_text": parsed["request_text"].strip(),
        "user_goal": parsed["user_goal"].strip(),
        "difficulty": parsed["difficulty"],
        "phrasing_style": parsed["phrasing_style"],
        "scenario_summary": parsed["scenario_summary"].strip(),
        "notes": parsed.get("notes", []),
        "usage": {"elapsed_ms": elapsed_ms},
        "codex_cli": build_codex_cli_meta(command=command, artifact_paths=artifact_paths),
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
    schema = build_user_simulation_schema()
    artifact_root = Path(args.artifact_dir)
    output_path = Path(args.output)
    existing_rows = {}
    if args.resume and output_path.exists():
        from common import read_jsonl

        existing_rows = {row["job_id"]: row for row in read_jsonl(output_path)}

    rows: list[dict[str, Any]] = []
    skipped: list[str] = []
    failures: list[dict[str, str]] = []

    for job in jobs:
        if job["job_id"] in existing_rows:
            rows.append(existing_rows[job["job_id"]])
            skipped.append(job["job_id"])
            continue
        job_dir = artifact_root / safe_slug(job["job_id"])
        prompt_text = build_prompt(job, repo_root=repo_root)
        request_payload = {
            "job_id": job["job_id"],
            "simulator_run_id": args.simulator_run_id,
            "simulator_model": args.simulator_model,
            "generation_mode": USER_SIMULATION_MODE,
            "task_type": job["task_type"],
            "source_chunk_ids": job["source_chunk_ids"],
            "source_doc_ids": job["source_doc_ids"],
            "source_excerpt": job.get("source_excerpt"),
            "runner_input": job["runner_input"],
            "provenance": job["provenance"],
        }
        try:
            parsed, _raw_text, artifact_paths, command, elapsed_ms = run_codex_json_generation(
                codex_bin=args.codex_bin,
                repo_root=repo_root,
                model=args.simulator_model,
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
        rows.append(
            build_row(
                job=job,
                jobs_path=jobs_path,
                parsed=parsed,
                simulator_model=args.simulator_model,
                simulator_run_id=args.simulator_run_id,
                command=command,
                artifact_paths=artifact_paths,
                elapsed_ms=elapsed_ms,
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
        "simulator_provider": "codex_cli",
        "generation_mode": USER_SIMULATION_MODE,
        "selected_jobs": len(jobs),
        "completed_jobs": len(ordered_rows),
        "skipped_existing_jobs": skipped,
        "failed_jobs": failures,
        "output": normalized_path(output_path),
        "artifact_dir": normalized_path(artifact_root),
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(ordered_rows)} user simulations -> {args.output}")
    print(f"Wrote user simulation report -> {args.report_output}")


if __name__ == "__main__":
    main()

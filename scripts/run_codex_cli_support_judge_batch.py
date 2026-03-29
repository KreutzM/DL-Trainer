from __future__ import annotations

from pathlib import Path
from typing import Any

from codex_cli_support_mvp_common import (
    JUDGE_MODE,
    JUDGE_PROMPT_VERSION,
    TRANSFORM_PIPELINE_VERSION,
    build_codex_cli_meta,
    load_repo_text,
    normalized_path,
    repo_root_from_cwd,
    run_codex_json_generation,
    safe_slug,
)
from common import make_parser, read_jsonl, write_json, write_jsonl
from run_teacher_jobs import filter_jobs, load_jobs
from teacher_quality_gates import blocking_artifact_reasons


def parse_args() -> Any:
    parser = make_parser("Judge JAWS-DE simulated user/support pairs via Codex CLI and gate reviewed outputs.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--user-simulations", required=True)
    parser.add_argument("--raw-output", required=True)
    parser.add_argument("--teacher-output", required=True)
    parser.add_argument("--judge-output", required=True)
    parser.add_argument("--reviewed-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--reviewer-run-id", required=True)
    parser.add_argument("--reviewer-model", default="gpt-5.4")
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


def build_judge_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "decision",
            "quality_score",
            "summary",
            "blocking_reasons",
            "strengths",
            "improvement_notes",
            "source_chunk_ids_confirmed",
        ],
        "properties": {
            "decision": {"type": "string", "enum": ["approve", "reject"]},
            "quality_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "summary": {"type": "string", "minLength": 1},
            "blocking_reasons": {"type": "array", "items": {"type": "string"}},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "improvement_notes": {"type": "array", "items": {"type": "string"}},
            "source_chunk_ids_confirmed": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
        },
    }


def build_prompt(job: dict, simulation: dict, teacher_output: dict, *, repo_root: Path) -> str:
    prompt_template = load_repo_text(repo_root, "prompts/teacher/jaws_de_support_judge.md")
    answer_text = ""
    candidate = teacher_output["candidate"]
    if teacher_output["record_type"] == "sft_sample":
        for message in reversed(candidate.get("messages", [])):
            if message.get("role") == "assistant":
                answer_text = str(message.get("content") or "")
                break
    else:
        answer_text = str(candidate.get("reference_answer") or "")

    prompt_parts = [
        prompt_template,
        "",
        "## Fallkontext",
        f"- task_type: {job['task_type']}",
        f"- expected_output_kind: {job['expected_output_kind']}",
        f"- target_split: {job['target_split']}",
        f"- source_doc_ids: {', '.join(job['source_doc_ids'])}",
        f"- source_chunk_ids: {', '.join(job['source_chunk_ids'])}",
        "",
        "## Simulierte Nutzeranfrage",
        simulation["request_text"],
        "",
        "## Erzeugte Support-Antwort",
        answer_text,
        "",
        "## Quellauszug",
        job.get("source_excerpt") or "",
        "",
        "## Strenge Regel",
        "Wenn die Antwort auch nur leicht erfunden, zu generisch oder nicht gut genug fuer einen Gold-Kandidaten wirkt, entscheide reject.",
    ]
    return "\n".join(prompt_parts).strip() + "\n"


def build_judge_row(
    *,
    job: dict,
    jobs_path: Path,
    simulation: dict,
    raw_row: dict,
    parsed: dict[str, Any],
    reviewer_model: str,
    reviewer_run_id: str,
    command: list[str],
    artifact_paths: dict[str, Path],
    elapsed_ms: int,
) -> dict[str, Any]:
    return {
        "review_id": f"{reviewer_run_id}::{job['job_id']}::review",
        "job_id": job["job_id"],
        "output_id": raw_row["output_id"],
        "simulation_id": simulation["simulation_id"],
        "response_id": raw_row["response_id"],
        "target_split": job["target_split"],
        "record_type": job["expected_output_kind"],
        "task_type": job["task_type"],
        "product": job["product"],
        "language": job["language"],
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
        "reviewer_provider": "codex_cli",
        "reviewer_model": reviewer_model,
        "reviewer_run_id": reviewer_run_id,
        "reviewer_prompt_version": JUDGE_PROMPT_VERSION,
        "generation_mode": JUDGE_MODE,
        "decision": parsed["decision"],
        "quality_score": parsed["quality_score"],
        "summary": parsed["summary"].strip(),
        "blocking_reasons": parsed.get("blocking_reasons", []),
        "strengths": parsed.get("strengths", []),
        "improvement_notes": parsed.get("improvement_notes", []),
        "source_chunk_ids_confirmed": parsed["source_chunk_ids_confirmed"],
        "usage": {"elapsed_ms": elapsed_ms},
        "codex_cli": build_codex_cli_meta(command=command, artifact_paths=artifact_paths),
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "source_job_path": normalized_path(jobs_path),
            "source_records": job["provenance"]["source_records"],
        },
    }


def apply_auto_review(teacher_output: dict[str, Any], judge_row: dict[str, Any]) -> dict[str, Any]:
    reviewed = dict(teacher_output)
    reviewed["candidate"] = dict(teacher_output["candidate"])
    auto_review = {
        "review_id": judge_row["review_id"],
        "decision": judge_row["decision"],
        "quality_score": judge_row["quality_score"],
        "summary": judge_row["summary"],
        "blocking_reasons": list(judge_row["blocking_reasons"]),
        "strengths": judge_row["strengths"],
        "improvement_notes": judge_row["improvement_notes"],
        "reviewer_provider": judge_row["reviewer_provider"],
        "reviewer_model": judge_row["reviewer_model"],
        "reviewer_run_id": judge_row["reviewer_run_id"],
        "reviewer_prompt_version": judge_row["reviewer_prompt_version"],
    }
    artifact_reasons = blocking_artifact_reasons(reviewed)
    if artifact_reasons:
        auto_review["blocking_reasons"] = sorted(set(auto_review["blocking_reasons"] + artifact_reasons))
        auto_review["decision"] = "reject"

    approved = auto_review["decision"] == "approve" and not auto_review["blocking_reasons"]
    reviewed["review_status"] = "codex_reviewed" if approved else "rejected"
    reviewed["approved_by"] = judge_row["reviewer_run_id"]
    reviewed["auto_review"] = auto_review
    candidate = reviewed["candidate"]
    candidate["review_status"] = reviewed["review_status"]
    candidate["approved_by"] = judge_row["reviewer_run_id"]
    if reviewed["record_type"] == "sft_sample":
        candidate.setdefault("meta", {})
        candidate["meta"]["review_status"] = reviewed["review_status"]
        candidate["meta"]["approved_by"] = judge_row["reviewer_run_id"]
        candidate["meta"]["auto_review"] = auto_review
    else:
        candidate["auto_review"] = auto_review
    return reviewed


def task_alignment_blocking_reasons(raw_row: dict[str, Any], teacher_output: dict[str, Any]) -> list[str]:
    parsed = raw_row.get("parsed_response", {})
    task_type = raw_row.get("task_type")
    reasons: list[str] = []
    if task_type == "clarification":
        assistant_text = ""
        for message in reversed(teacher_output.get("candidate", {}).get("messages", [])):
            if message.get("role") == "assistant":
                assistant_text = str(message.get("content") or "").strip()
                break
        if not parsed.get("needs_clarification"):
            reasons.append("clarification task answered without needs_clarification=true")
        if not str(parsed.get("clarification_question") or "").strip():
            reasons.append("clarification task missing clarification_question")
        if assistant_text and not assistant_text.endswith("?"):
            reasons.append("clarification task does not end in a focused question")
    elif task_type == "uncertainty_escalation":
        if not parsed.get("escalate"):
            reasons.append("uncertainty_escalation task answered without escalate=true")
        if not str(parsed.get("uncertainty_reason") or "").strip():
            reasons.append("uncertainty_escalation task missing uncertainty_reason")
    elif task_type == "faq_direct_answer":
        if parsed.get("needs_clarification"):
            reasons.append("faq_direct_answer task should not require clarification")
        if parsed.get("escalate"):
            reasons.append("faq_direct_answer task should not escalate")
    return reasons


def main() -> None:
    args = parse_args()
    repo_root = repo_root_from_cwd()
    jobs_path = Path(args.jobs)
    jobs = filter_jobs(load_jobs(jobs_path), set(args.job_id), args.job_ids_file, args.limit)
    simulations = {row["job_id"]: row for row in read_jsonl(Path(args.user_simulations))}
    raw_rows = {row["job_id"]: row for row in read_jsonl(Path(args.raw_output))}
    teacher_outputs = {row["job_id"]: row for row in read_jsonl(Path(args.teacher_output))}
    missing_inputs = [
        job["job_id"]
        for job in jobs
        if job["job_id"] not in simulations or job["job_id"] not in raw_rows or job["job_id"] not in teacher_outputs
    ]
    if missing_inputs:
        raise SystemExit("Missing simulation/raw/output input for job IDs: " + ", ".join(missing_inputs))

    judge_output_path = Path(args.judge_output)
    existing_judges = {}
    if args.resume and judge_output_path.exists():
        existing_judges = {row["job_id"]: row for row in read_jsonl(judge_output_path)}

    artifact_root = Path(args.artifact_dir)
    judge_rows: list[dict[str, Any]] = []
    reviewed_rows: list[dict[str, Any]] = []
    skipped: list[str] = []
    failures: list[dict[str, str]] = []
    schema = build_judge_schema()

    for job in jobs:
        simulation = simulations[job["job_id"]]
        raw_row = raw_rows[job["job_id"]]
        teacher_output = teacher_outputs[job["job_id"]]
        if job["job_id"] in existing_judges:
            judge_row = existing_judges[job["job_id"]]
            judge_rows.append(judge_row)
            reviewed = apply_auto_review(teacher_output, judge_row)
            alignment_reasons = task_alignment_blocking_reasons(raw_row, reviewed)
            if alignment_reasons:
                reviewed["review_status"] = "rejected"
                reviewed["candidate"]["review_status"] = "rejected"
                reviewed["auto_review"]["decision"] = "reject"
                reviewed["auto_review"]["blocking_reasons"] = sorted(
                    set(reviewed["auto_review"]["blocking_reasons"] + alignment_reasons)
                )
                if reviewed["record_type"] == "sft_sample":
                    reviewed["candidate"]["meta"]["review_status"] = "rejected"
                    reviewed["candidate"]["meta"]["auto_review"] = reviewed["auto_review"]
            reviewed_rows.append(reviewed)
            skipped.append(job["job_id"])
            continue
        job_dir = artifact_root / safe_slug(job["job_id"])
        prompt_text = build_prompt(job, simulation, teacher_output, repo_root=repo_root)
        request_payload = {
            "job_id": job["job_id"],
            "reviewer_run_id": args.reviewer_run_id,
            "reviewer_model": args.reviewer_model,
            "generation_mode": JUDGE_MODE,
            "task_type": job["task_type"],
            "simulation_id": simulation["simulation_id"],
            "response_id": raw_row["response_id"],
            "output_id": raw_row["output_id"],
            "source_chunk_ids": job["source_chunk_ids"],
            "source_doc_ids": job["source_doc_ids"],
        }
        try:
            parsed, _raw_text, artifact_paths, command, elapsed_ms = run_codex_json_generation(
                codex_bin=args.codex_bin,
                repo_root=repo_root,
                model=args.reviewer_model,
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
        judge_row = build_judge_row(
            job=job,
            jobs_path=jobs_path,
            simulation=simulation,
            raw_row=raw_row,
            parsed=parsed,
            reviewer_model=args.reviewer_model,
            reviewer_run_id=args.reviewer_run_id,
            command=command,
            artifact_paths=artifact_paths,
            elapsed_ms=elapsed_ms,
        )
        judge_rows.append(judge_row)
        reviewed = apply_auto_review(teacher_output, judge_row)
        alignment_reasons = task_alignment_blocking_reasons(raw_row, reviewed)
        if alignment_reasons:
            reviewed["review_status"] = "rejected"
            reviewed["candidate"]["review_status"] = "rejected"
            reviewed["auto_review"]["decision"] = "reject"
            reviewed["auto_review"]["blocking_reasons"] = sorted(
                set(reviewed["auto_review"]["blocking_reasons"] + alignment_reasons)
            )
            if reviewed["record_type"] == "sft_sample":
                reviewed["candidate"]["meta"]["review_status"] = "rejected"
                reviewed["candidate"]["meta"]["auto_review"] = reviewed["auto_review"]
        reviewed_rows.append(reviewed)

    if not judge_rows:
        raise SystemExit("No judge results were generated successfully")

    judges_by_job = {row["job_id"]: row for row in judge_rows}
    reviewed_by_job = {row["job_id"]: row for row in reviewed_rows}
    ordered_judges = [judges_by_job[job["job_id"]] for job in jobs if job["job_id"] in judges_by_job]
    ordered_reviewed = [reviewed_by_job[job["job_id"]] for job in jobs if job["job_id"] in reviewed_by_job]
    write_jsonl(judge_output_path, ordered_judges)
    write_jsonl(Path(args.reviewed_output), ordered_reviewed)
    report = {
        "jobs_path": normalized_path(jobs_path),
        "user_simulations": normalized_path(args.user_simulations),
        "raw_output": normalized_path(args.raw_output),
        "teacher_output": normalized_path(args.teacher_output),
        "reviewer_run_id": args.reviewer_run_id,
        "reviewer_model": args.reviewer_model,
        "reviewer_provider": "codex_cli",
        "generation_mode": JUDGE_MODE,
        "selected_jobs": len(jobs),
        "completed_jobs": len(ordered_judges),
        "approved_jobs": sum(1 for row in ordered_reviewed if row["review_status"] == "codex_reviewed"),
        "rejected_jobs": sum(1 for row in ordered_reviewed if row["review_status"] == "rejected"),
        "skipped_existing_jobs": skipped,
        "failed_jobs": failures,
        "judge_output": normalized_path(args.judge_output),
        "reviewed_output": normalized_path(args.reviewed_output),
        "artifact_dir": normalized_path(artifact_root),
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(ordered_judges)} judge results -> {args.judge_output}")
    print(f"Wrote {len(ordered_reviewed)} auto-reviewed teacher outputs -> {args.reviewed_output}")
    print(f"Wrote judge report -> {args.report_output}")


if __name__ == "__main__":
    main()

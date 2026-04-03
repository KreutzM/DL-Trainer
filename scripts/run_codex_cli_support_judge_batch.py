from __future__ import annotations

from pathlib import Path
from typing import Any

from codex_cli_support_mvp_common import (
    JUDGE_MODE,
    JUDGE_PROMPT_VERSION,
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
from run_teacher_jobs import filter_jobs, load_jobs
from teacher_quality_gates import blocking_artifact_reasons


def parse_args() -> Any:
    defaults = stage_defaults(JUDGE_MODE)
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
    parser.add_argument("--reviewer-model", default=defaults["model"])
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


def build_judge_schema(batch_jobs: list[dict[str, Any]]) -> dict[str, Any]:
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
                    "required": [
                        "job_id",
                        "decision",
                        "quality_score",
                        "summary",
                        "blocking_reasons",
                        "strengths",
                        "improvement_notes",
                        "source_chunk_ids_confirmed",
                    ],
                    "properties": {
                        "job_id": {"type": "string", "enum": [job["job_id"] for job in batch_jobs]},
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
                },
            }
        },
    }


def normalize_quality_score(raw_score: Any) -> int:
    score = int(raw_score)
    if 0 <= score <= 10:
        return score * 10
    return score


def render_teacher_answer(teacher_output: dict) -> str:
    answer_text = ""
    candidate = teacher_output["candidate"]
    if teacher_output["record_type"] == "sft_sample":
        for message in reversed(candidate.get("messages", [])):
            if message.get("role") == "assistant":
                answer_text = str(message.get("content") or "")
                break
    else:
        answer_text = str(candidate.get("reference_answer") or "")
    return compact_text(answer_text)


def build_prompt(batch_jobs: list[dict[str, Any]], simulations: dict[str, dict], teacher_outputs: dict[str, dict], *, repo_root: Path) -> str:
    prompt_template = load_repo_text(repo_root, "prompts/teacher/jaws_de_support_judge.md")
    prompt_parts = [
        prompt_template,
        "",
        "## Batch-Regeln",
        "- Bewerte jeden Fall separat und gib fuer jede job_id genau eine Entscheidung zurueck.",
        "- Antworte gesammelt in einem JSON-Objekt mit items[].",
        "- approve nur bei klar belastbarer Gesamtqualitaet.",
        "- Wenn Anfrage oder Antwort auch nur leicht zu schwach wirkt, entscheide reject.",
        "",
        "## Faelle",
    ]
    for job in batch_jobs:
        simulation = simulations[job["job_id"]]
        teacher_output = teacher_outputs[job["job_id"]]
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
                f"- expected_behavior: {str(job.get('fixture_payload', {}).get('expected_behavior') or 'n/a')}",
                "- user_request:",
                compact_text(simulation["request_text"]),
                "- support_answer:",
                render_teacher_answer(teacher_output) or "(leer)",
                "- source_excerpt:",
                compact_text(job.get("source_excerpt") or "") or "(leer)",
                "",
            ]
        )
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
    normalized_quality_score = normalize_quality_score(parsed["quality_score"])
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
        "reviewer_provider": stage_provider_name(llm_backend),
        "reviewer_model": reviewer_model,
        "reviewer_run_id": reviewer_run_id,
        "reviewer_prompt_version": JUDGE_PROMPT_VERSION,
        "generation_mode": generation_mode_for_backend(JUDGE_MODE, llm_backend),
        "decision": parsed["decision"],
        "quality_score": normalized_quality_score,
        "summary": parsed["summary"].strip(),
        "blocking_reasons": parsed.get("blocking_reasons", []),
        "strengths": parsed.get("strengths", []),
        "improvement_notes": parsed.get("improvement_notes", []),
        "source_chunk_ids_confirmed": parsed["source_chunk_ids_confirmed"],
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
    if auto_review["decision"] == "approve" and int(auto_review["quality_score"]) < 70:
        auto_review["blocking_reasons"] = sorted(
            set(auto_review["blocking_reasons"] + ["approve decision below minimum quality score threshold"])
        )
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
    runtime = resolve_stage_runtime_settings(
        args,
        repo_root=repo_root,
        stage_mode=JUDGE_MODE,
        model_arg_name="reviewer_model",
    )
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
    total_elapsed_ms = 0
    total_prompt_chars = 0
    total_source_excerpt_chars = 0
    total_retry_attempts = 0
    executed_batches = 0
    completed_batches = 0

    pending_jobs: list[dict[str, Any]] = []
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
        else:
            pending_jobs.append(job)

    for batch_index, batch_jobs in enumerate(chunked(pending_jobs, runtime.batch_size), start=1):
        batch_id = f"{args.reviewer_run_id}::batch::{batch_index:04d}"
        job_dir = artifact_root / safe_slug(batch_id)
        prompt_text = build_prompt(batch_jobs, simulations, teacher_outputs, repo_root=repo_root)
        prompt_chars = len(prompt_text)
        source_excerpt_chars = sum(len(compact_text(job.get("source_excerpt") or "")) for job in batch_jobs)
        total_prompt_chars += prompt_chars
        total_source_excerpt_chars += source_excerpt_chars
        executed_batches += 1
        request_payload = {
            "batch_id": batch_id,
            "job_ids": [job["job_id"] for job in batch_jobs],
            "reviewer_run_id": args.reviewer_run_id,
            "reviewer_model": runtime.model,
            "generation_mode": generation_mode_for_backend(JUDGE_MODE, runtime.llm_backend),
            "jobs": [
                {
                    "job_id": job["job_id"],
                    "task_type": job["task_type"],
                    "simulation_id": simulations[job["job_id"]]["simulation_id"],
                    "response_id": raw_rows[job["job_id"]]["response_id"],
                    "output_id": raw_rows[job["job_id"]]["output_id"],
                    "source_chunk_ids": job["source_chunk_ids"],
                    "source_doc_ids": job["source_doc_ids"],
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
                schema=build_judge_schema(batch_jobs),
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
            raw_row = raw_rows[job["job_id"]]
            teacher_output = teacher_outputs[job["job_id"]]
            item_parsed = dict(items_by_job_id[job["job_id"]])
            item_parsed.pop("job_id", None)
            judge_row = build_judge_row(
                job=job,
                jobs_path=jobs_path,
                simulation=simulation,
                raw_row=raw_row,
                parsed=item_parsed,
                reviewer_model=runtime.model,
                reviewer_run_id=args.reviewer_run_id,
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
        "reviewer_model": runtime.model,
        "reviewer_provider": stage_provider_name(runtime.llm_backend),
        "generation_mode": generation_mode_for_backend(JUDGE_MODE, runtime.llm_backend),
        "selected_jobs": len(jobs),
        "completed_jobs": len(ordered_judges),
        "approved_jobs": sum(1 for row in ordered_reviewed if row["review_status"] == "codex_reviewed"),
        "rejected_jobs": sum(1 for row in ordered_reviewed if row["review_status"] == "rejected"),
        "skipped_existing_jobs": skipped,
        "failed_jobs": failures,
        "judge_output": normalized_path(args.judge_output),
        "reviewed_output": normalized_path(args.reviewed_output),
        "artifact_dir": normalized_path(artifact_root),
        "runtime": build_stage_metrics(
            selected_jobs=len(jobs),
            completed_jobs=len(ordered_judges),
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
    print(f"Wrote {len(ordered_judges)} judge results -> {args.judge_output}")
    print(f"Wrote {len(ordered_reviewed)} auto-reviewed teacher outputs -> {args.reviewed_output}")
    print(f"Wrote judge report -> {args.report_output}")


if __name__ == "__main__":
    main()

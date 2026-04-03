from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from common import find_repo_root, make_parser, read_jsonl, write_jsonl
from llm_json_backends import (
    OPENAI_API_BASE,
    OPENROUTER_API_BASE,
    JsonGenerationRequest,
    JsonGenerationResult,
    build_backend_record,
    provider_name_for_backend,
    resolve_json_backend,
)


TRANSFORM_PIPELINE_VERSION = "0.7.0"
RAW_RESPONSE_FORMAT_VERSION = "teacher_response_v1"
RUNNER_OPENAI_MODE = "teacher_runner_openai_chat_json_v1"
RUNNER_OPENROUTER_MODE = "teacher_runner_openrouter_chat_json_v1"
RUNNER_IMPORT_MODE = "teacher_runner_import_v1"
RUNNER_CODEX_MODE = "teacher_runner_codex_gpt54_v1"
RUNNER_REPLAY_MODE = "teacher_runner_replay_v1"
RUNNER_STUB_MODE = "teacher_runner_stub_v2"
SYSTEM_INSTRUCTION = (
    "Arbeite strikt dokumentationsgebunden. Nutze nur die bereitgestellten Quellen, "
    "erfinde keine Fakten und gib nur das sichtbare Endergebnis im JSON-Format aus."
)


def normalized_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def safe_slug(text: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)


def generation_mode_for_backend(backend_name: str) -> str:
    if backend_name == "openai":
        return RUNNER_OPENAI_MODE
    if backend_name == "openrouter":
        return RUNNER_OPENROUTER_MODE
    raise ValueError(f"Unsupported teacher backend: {backend_name}")


def mode_uses_generated_or_imported_raw_rows(mode: str) -> bool:
    return mode in {"codex", "import", "openai", "openrouter"}


def load_jobs(jobs_path: Path) -> list[dict]:
    jobs = read_jsonl(jobs_path)
    if not jobs:
        raise SystemExit(f"No teacher jobs found in {jobs_path}")
    return jobs


def filter_jobs(
    jobs: list[dict],
    explicit_job_ids: set[str],
    job_ids_files: list[str],
    limit: int | None,
) -> list[dict]:
    selected_job_ids = set(explicit_job_ids)
    for path_str in job_ids_files:
        selected_job_ids.update(
            line.strip()
            for line in Path(path_str).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )

    filtered = jobs
    if selected_job_ids:
        filtered = [job for job in jobs if job["job_id"] in selected_job_ids]
        missing = sorted(selected_job_ids - {job["job_id"] for job in filtered})
        if missing:
            raise SystemExit("Unknown job IDs: " + ", ".join(missing))

    if limit is not None:
        filtered = filtered[:limit]
    if not filtered:
        raise SystemExit("No teacher jobs selected")
    return filtered


def build_sft_candidate(
    job: dict,
    teacher_model: str,
    teacher_provider: str,
    teacher_run_id: str,
    generation_mode: str,
    assistant_message: str,
    *,
    user_message: str | None = None,
) -> dict:
    provenance = {
        "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
        "behavior_spec_path": job["behavior_spec_path"],
        "prompt_template_path": job["prompt_template_path"],
        "source_records": job["provenance"]["source_records"],
    }
    meta = {
        "product": job["product"],
        "language": job["language"],
        "task_type": job["task_type"],
        "teacher_provider": teacher_provider,
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
        "teacher_prompt_version": job["teacher_prompt_version"],
        "generation_mode": generation_mode,
        "needs_clarification": job["task_type"] == "clarification",
        "review_status": "teacher_generated",
        "split": "train",
        "approved_by": None,
        "promoted_from": None,
        "provenance": provenance,
    }
    return {
        "id": f"{job['job_id']}__candidate",
        "product": job["product"],
        "language": job["language"],
        "task_type": job["task_type"],
        "messages": [
            {"role": "system", "content": job["runner_input"]["system_message"]},
            {"role": "user", "content": user_message or job["runner_input"]["user_message"]},
            {"role": "assistant", "content": assistant_message},
        ],
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
        "teacher_provider": teacher_provider,
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": job["teacher_prompt_version"],
        "generation_mode": generation_mode,
        "review_status": "teacher_generated",
        "split": "train",
        "approved_by": None,
        "promoted_from": None,
        "provenance": provenance,
        "meta": meta,
    }


def render_visible_answer(parsed: dict, task_type: str, *, prefer_reference: bool = False) -> str:
    base_text = ""
    if prefer_reference:
        base_text = str(parsed.get("reference_answer") or parsed.get("answer") or "").strip()
    else:
        base_text = str(parsed.get("answer") or "").strip()
    if task_type != "step_by_step":
        return base_text

    steps = [str(step).strip() for step in parsed.get("steps", []) if str(step).strip()]
    if not steps:
        return base_text
    if base_text:
        numbered_lines = [line for line in base_text.splitlines() if line.strip()]
        if numbered_lines and numbered_lines[0].lstrip().startswith("1."):
            return base_text

    numbered_steps = "\n".join(f"{idx}. {step}" for idx, step in enumerate(steps, start=1))
    if not base_text:
        return numbered_steps
    return f"{base_text}\n\n{numbered_steps}"


def build_eval_candidate(
    job: dict,
    teacher_model: str,
    teacher_provider: str,
    teacher_run_id: str,
    generation_mode: str,
    *,
    prompt_text: str | None,
    case_description: str,
    expected_behavior: str,
    reference_answer: str,
    rubric: dict[str, Any],
) -> dict:
    normalized_rubric = dict(rubric)
    if normalized_rubric.get("scoring_notes") is None:
        normalized_rubric["scoring_notes"] = ""
    return {
        "eval_id": f"{job['job_id']}__candidate",
        "product": job["product"],
        "language": job["language"],
        "case_type": job["task_type"],
        "prompt": prompt_text or job["runner_input"]["user_message"],
        "case_description": case_description,
        "expected_behavior": expected_behavior,
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
        "teacher_provider": teacher_provider,
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": job["teacher_prompt_version"],
        "generation_mode": generation_mode,
        "review_status": "teacher_generated",
        "split": "eval",
        "approved_by": None,
        "promoted_from": None,
        "reference_answer": reference_answer,
        "rubric": normalized_rubric,
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "behavior_spec_path": job["behavior_spec_path"],
            "prompt_template_path": job["prompt_template_path"],
            "source_records": job["provenance"]["source_records"],
        },
    }


def replay_index(rows: list[dict]) -> dict[str, dict]:
    indexed: dict[str, dict] = {}
    for row in rows:
        if "job_id" not in row:
            raise SystemExit("Replay rows must include job_id")
        indexed[row["job_id"]] = row
    return indexed


def raw_response_index(rows: list[dict]) -> dict[str, dict]:
    indexed: dict[str, dict] = {}
    for row in rows:
        job_id = row.get("job_id")
        if not job_id:
            raise SystemExit("Imported teacher response rows must include job_id")
        indexed[job_id] = row
    return indexed


def build_output_from_candidate(
    job: dict,
    teacher_model: str,
    teacher_provider: str,
    teacher_run_id: str,
    generation_mode: str,
    candidate: dict,
    record_type: str,
    raw_response_path: str | None,
) -> dict:
    return {
        "output_id": f"{teacher_run_id}::{job['job_id']}",
        "job_id": job["job_id"],
        "wave_id": job.get("wave_id"),
        "record_type": record_type,
        "target_split": job["target_split"],
        "product": job["product"],
        "language": job["language"],
        "task_type": job["task_type"],
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
        "teacher_provider": teacher_provider,
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": job["teacher_prompt_version"],
        "generation_mode": generation_mode,
        "review_status": "teacher_generated",
        "approved_by": None,
        "promoted_to": None,
        "quality_score": job.get("quality_score"),
        "selection_reason": job.get("selection_reason"),
        "raw_response_path": raw_response_path,
        "candidate": candidate,
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "source_job_path": "",
            "source_records": job["provenance"]["source_records"],
        },
    }


def build_output_from_raw_response(job: dict, raw_response: dict, raw_response_path: str | None) -> dict:
    return build_output_from_raw_response_with_user_request(
        job,
        raw_response,
        raw_response_path,
        user_message=None,
    )


def build_output_from_raw_response_with_user_request(
    job: dict,
    raw_response: dict,
    raw_response_path: str | None,
    *,
    user_message: str | None,
) -> dict:
    parsed = raw_response["parsed_response"]
    generation_mode = raw_response["generation_mode"]
    teacher_model = raw_response["teacher_model"]
    teacher_provider = raw_response["teacher_provider"]
    teacher_run_id = raw_response["teacher_run_id"]
    raw_provenance = raw_response.get("provenance", {})

    if job["expected_output_kind"] == "sft_sample":
        candidate = build_sft_candidate(
            job,
            teacher_model,
            teacher_provider,
            teacher_run_id,
            generation_mode,
            render_visible_answer(parsed, job["task_type"]),
            user_message=user_message,
        )
        candidate["meta"]["needs_clarification"] = bool(parsed.get("needs_clarification", False))
        record_type = "sft_sample"
    else:
        candidate = build_eval_candidate(
            job,
            teacher_model,
            teacher_provider,
            teacher_run_id,
            generation_mode,
            prompt_text=user_message,
            case_description=parsed["case_description"],
            expected_behavior=parsed["expected_behavior"],
            reference_answer=render_visible_answer(parsed, job["task_type"], prefer_reference=True),
            rubric=parsed["rubric"],
        )
        record_type = "eval_case"

    candidate["teacher_provider"] = teacher_provider
    candidate["teacher_model"] = teacher_model
    candidate["teacher_run_id"] = teacher_run_id
    candidate["teacher_prompt_version"] = raw_response["teacher_prompt_version"]
    candidate["generation_mode"] = generation_mode
    candidate["provenance"]["transform_pipeline_version"] = raw_provenance.get(
        "transform_pipeline_version",
        candidate["provenance"].get("transform_pipeline_version"),
    )
    if raw_provenance.get("behavior_spec_path"):
        candidate["provenance"]["behavior_spec_path"] = raw_provenance["behavior_spec_path"]
    if raw_provenance.get("prompt_template_path"):
        candidate["provenance"]["prompt_template_path"] = raw_provenance["prompt_template_path"]
    if record_type == "sft_sample":
        candidate["meta"]["teacher_provider"] = teacher_provider
        candidate["meta"]["teacher_model"] = teacher_model
        candidate["meta"]["teacher_run_id"] = teacher_run_id
        candidate["meta"]["teacher_prompt_version"] = raw_response["teacher_prompt_version"]
        candidate["meta"]["generation_mode"] = generation_mode
        candidate["meta"]["provenance"] = candidate["provenance"]

    output = build_output_from_candidate(
        job,
        teacher_model,
        teacher_provider,
        teacher_run_id,
        generation_mode,
        candidate,
        record_type,
        raw_response_path,
    )
    output["teacher_prompt_version"] = raw_response["teacher_prompt_version"]
    output["generation_mode"] = generation_mode
    output["provenance"]["transform_pipeline_version"] = raw_provenance.get(
        "transform_pipeline_version",
        output["provenance"].get("transform_pipeline_version"),
    )
    if raw_provenance.get("source_job_path"):
        output["provenance"]["source_job_path"] = raw_provenance["source_job_path"]
    return output


def build_output(
    job: dict,
    teacher_model: str,
    teacher_provider: str,
    teacher_run_id: str,
    mode: str,
    replay_row: dict | None,
    imported_response: dict | None,
    raw_response_path: str | None,
) -> dict:
    if imported_response is not None:
        return build_output_from_raw_response(job, imported_response, raw_response_path)

    if mode == "stub":
        generation_mode = RUNNER_STUB_MODE
    elif mode == "replay":
        generation_mode = RUNNER_REPLAY_MODE
    else:
        generation_mode = RUNNER_IMPORT_MODE
    if replay_row is not None:
        candidate = replay_row["candidate"]
        record_type = replay_row["record_type"]
    else:
        if job["expected_output_kind"] == "sft_sample":
            stub_answer = (
                job["fixture_payload"].get("assistant_message")
                or job["fixture_payload"].get("draft_answer")
            )
            if not stub_answer:
                raise SystemExit(f"Stub fixture missing draft answer for {job['job_id']}")
            candidate = build_sft_candidate(
                job,
                teacher_model,
                teacher_provider,
                teacher_run_id,
                generation_mode,
                stub_answer,
                user_message=None,
            )
            record_type = "sft_sample"
        else:
            candidate = build_eval_candidate(
                job,
                teacher_model,
                teacher_provider,
                teacher_run_id,
                generation_mode,
                prompt_text=None,
                case_description=job["fixture_payload"]["case_description"],
                expected_behavior=job["fixture_payload"]["expected_behavior"],
                reference_answer=job["fixture_payload"]["reference_answer"],
                rubric=job["fixture_payload"]["rubric"],
            )
            record_type = "eval_case"

    return build_output_from_candidate(
        job,
        teacher_model,
        teacher_provider,
        teacher_run_id,
        generation_mode,
        candidate,
        record_type,
        raw_response_path,
    )


def build_teacher_response_schema(expected_output_kind: str, task_type: str) -> dict[str, Any]:
    base_schema: dict[str, Any] = {
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
            "answer": {"type": "string", "minLength": 1},
            "task_type": {"type": "string", "enum": [task_type]},
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
        },
    }
    if expected_output_kind == "eval_case":
        base_schema["required"].extend(["case_description", "expected_behavior", "reference_answer", "rubric"])
        base_schema["properties"].update(
            {
                "case_description": {"type": "string", "minLength": 1},
                "expected_behavior": {"type": "string", "minLength": 1},
                "reference_answer": {"type": "string", "minLength": 1},
                "rubric": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["must_include", "must_not_include", "style", "scoring_notes"],
                    "properties": {
                        "must_include": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "must_not_include": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "style": {"type": "string", "minLength": 1},
                        "scoring_notes": {"type": ["string", "null"]},
                    },
                },
            }
        )
    return base_schema


def build_prompt_payload(job: dict) -> str:
    prompt_template = Path(job["prompt_template_path"]).read_text(encoding="utf-8").strip()
    source_records = [
        {
            "doc_id": record["doc_id"],
            "chunk_id": record["chunk_id"],
            "section_id": record.get("section_id"),
            "section_title": record.get("section_title"),
            "normalized_path": record["normalized_path"],
            "source_spans": record["source_spans"],
        }
        for record in job["provenance"]["source_records"]
    ]
    payload = {
        "task_type": job["task_type"],
        "target_split": job["target_split"],
        "expected_output_kind": job["expected_output_kind"],
        "user_message": job["runner_input"]["user_message"],
        "prompt_template": prompt_template,
        "source_chunk_ids": job["source_chunk_ids"],
        "source_excerpt": job.get("source_excerpt", ""),
        "source_records": source_records,
        "case_description": job.get("fixture_payload", {}).get("case_description"),
        "expected_behavior": job.get("fixture_payload", {}).get("expected_behavior"),
        "rubric": job.get("fixture_payload", {}).get("rubric"),
    }
    instructions = [
        "Nutze nur den bereitgestellten Quellkontext.",
        "Antwortsprache ist Deutsch.",
        "Gib exakt ein JSON-Objekt nach dem angeforderten Schema zurueck.",
        "Keine Markdown-Umrahmung, keine Erklaerungen ausserhalb des JSON.",
        "Wenn task_type clarification ist, muss answer genau eine fokussierte Rueckfrage sein.",
        "Wenn task_type uncertainty_escalation ist, muss answer die Evidenzgrenze klar benennen.",
        "Wenn task_type step_by_step ist, darf steps nur dokumentierte Schritte enthalten.",
        "source_chunk_ids muessen exakt den uebergebenen Chunk-IDs entsprechen.",
        "Keine versteckten Denkschritte, keine Begruendung ausserhalb der sichtbaren Endantwort.",
    ]
    return (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"Arbeitskontext:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Verbindliche Arbeitsregeln:\n- "
        + "\n- ".join(instructions)
    )


def build_raw_response(
    job: dict,
    generation_result: JsonGenerationResult,
    teacher_model: str,
    teacher_run_id: str,
    teacher_provider: str,
    generation_mode: str,
) -> dict:
    parsed_response = dict(generation_result.parsed_response)
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
        "teacher_provider": teacher_provider,
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": job["teacher_prompt_version"],
        "generation_mode": generation_mode,
        "response_status": "completed",
        "response_format_version": RAW_RESPONSE_FORMAT_VERSION,
        "provider_response_id": generation_result.provider_response_id,
        "raw_text": generation_result.raw_text,
        "parsed_response": parsed_response,
        "usage": generation_result.usage,
        **build_backend_record(generation_result),
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "source_job_path": "",
            "behavior_spec_path": job["behavior_spec_path"],
            "prompt_template_path": job["prompt_template_path"],
            "source_records": job["provenance"]["source_records"],
        },
    }


def generate_raw_responses_via_llm(
    jobs: list[dict],
    jobs_path: Path,
    *,
    backend_name: str,
    artifact_root: Path,
    api_base: str,
    api_key_env: str | None,
    teacher_model: str,
    teacher_run_id: str,
    timeout_sec: int,
) -> list[dict]:
    backend = resolve_json_backend(
        backend_name,
        api_base=api_base,
        api_key_env=api_key_env,
    )
    generation_mode = generation_mode_for_backend(backend_name)
    teacher_provider = provider_name_for_backend(backend_name)

    raw_rows: list[dict] = []
    for job in jobs:
        system_message = f"{job['runner_input']['system_message'].strip()}\n\n{build_prompt_payload(job)}"
        generation_result = backend.generate(
            JsonGenerationRequest(
                model=teacher_model,
                prompt_text=system_message,
                response_schema=build_teacher_response_schema(job["expected_output_kind"], job["task_type"]),
                request_payload={
                    "job_id": job["job_id"],
                    "teacher_run_id": teacher_run_id,
                    "teacher_model": teacher_model,
                    "teacher_provider": teacher_provider,
                    "generation_mode": generation_mode,
                    "runner_input": job["runner_input"],
                    "source_chunk_ids": job["source_chunk_ids"],
                    "source_doc_ids": job["source_doc_ids"],
                },
                artifact_dir=artifact_root / safe_slug(job["job_id"]),
                timeout_sec=timeout_sec,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": job["runner_input"]["user_message"]},
                ],
                schema_name="teacher_candidate_payload",
            )
        )
        raw_row = build_raw_response(
            job,
            generation_result,
            teacher_model,
            teacher_run_id,
            teacher_provider,
            generation_mode,
        )
        raw_row["provenance"]["source_job_path"] = normalized_path(jobs_path)
        raw_rows.append(raw_row)
    return raw_rows


def parse_args() -> Any:
    parser = make_parser(
        "Materialize teacher outputs from stub, replay, import, precomputed raw responses or OpenAI-compatible JSON generation."
    )
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=["codex", "stub", "replay", "import", "openai", "openrouter"], default="stub")
    parser.add_argument("--teacher-model", default="teacher-stub-no-llm")
    parser.add_argument("--teacher-provider", default="local")
    parser.add_argument("--teacher-run-id", default="teacher_stub_run_v1")
    parser.add_argument("--replay-input")
    parser.add_argument("--import-input")
    parser.add_argument("--raw-output")
    parser.add_argument("--artifact-dir")
    parser.add_argument("--api-key-env")
    parser.add_argument("--api-base")
    parser.add_argument("--request-timeout-sec", type=int, default=120)
    parser.add_argument("--job-id", action="append", default=[])
    parser.add_argument("--job-ids-file", action="append", default=[])
    parser.add_argument("--limit", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    jobs_path = Path(args.jobs)
    jobs = filter_jobs(load_jobs(jobs_path), set(args.job_id), args.job_ids_file, args.limit)
    repo_root = find_repo_root(Path.cwd())

    raw_rows: list[dict] = []
    raw_response_path: str | None = None
    if args.mode in {"openai", "openrouter"}:
        default_api_base = OPENAI_API_BASE if args.mode == "openai" else OPENROUTER_API_BASE
        artifact_root = (
            Path(args.artifact_dir)
            if args.artifact_dir
            else repo_root / "tmp" / "teacher_runs" / args.teacher_run_id / provider_name_for_backend(args.mode)
        )
        raw_rows = generate_raw_responses_via_llm(
            jobs,
            jobs_path,
            backend_name=args.mode,
            artifact_root=artifact_root,
            api_base=args.api_base or default_api_base,
            api_key_env=args.api_key_env,
            teacher_model=args.teacher_model,
            teacher_run_id=args.teacher_run_id,
            timeout_sec=args.request_timeout_sec,
        )
        if args.raw_output:
            write_jsonl(Path(args.raw_output), raw_rows)
            raw_response_path = normalized_path(args.raw_output)
    elif args.mode in {"import", "codex"}:
        if not args.import_input:
            raise SystemExit("--import-input is required for --mode import/codex")
        raw_rows = read_jsonl(Path(args.import_input))
        raw_response_path = normalized_path(args.import_input)

    replay_rows = replay_index(read_jsonl(Path(args.replay_input))) if args.mode == "replay" else {}
    imported_rows = raw_response_index(raw_rows) if mode_uses_generated_or_imported_raw_rows(args.mode) else {}

    outputs = []
    for job in jobs:
        replay_row = replay_rows.get(job["job_id"])
        if args.mode == "replay" and replay_row is None:
            raise SystemExit(f"Replay input missing job_id {job['job_id']}")
        imported_row = imported_rows.get(job["job_id"])
        if mode_uses_generated_or_imported_raw_rows(args.mode) and imported_row is None:
            raise SystemExit(f"Imported/provider response missing job_id {job['job_id']}")
        output = build_output(
            job,
            args.teacher_model,
            args.teacher_provider if not mode_uses_generated_or_imported_raw_rows(args.mode) else args.mode,
            args.teacher_run_id,
            args.mode,
            replay_row,
            imported_row,
            raw_response_path,
        )
        output["provenance"]["source_job_path"] = normalized_path(jobs_path)
        outputs.append(output)

    write_jsonl(Path(args.output), outputs)
    print(f"Wrote {len(outputs)} teacher outputs -> {args.output}")
    if args.raw_output and raw_rows:
        print(f"Wrote {len(raw_rows)} raw teacher responses -> {args.raw_output}")


if __name__ == "__main__":
    main()

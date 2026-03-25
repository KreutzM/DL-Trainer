from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_jsonl


TRANSFORM_PIPELINE_VERSION = "0.6.0"
GENERATION_MODE = "teacher_runner_import_fixture_v1"
RESPONSE_FORMAT_VERSION = "teacher_response_v1"


def parse_args() -> Any:
    parser = make_parser("Build importable raw teacher responses from existing teacher jobs for replay/import tests.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--teacher-model", default="gpt-5.4")
    parser.add_argument("--teacher-provider", default="openai")
    parser.add_argument("--teacher-run-id", required=True)
    parser.add_argument("--job-ids-file", action="append", default=[])
    return parser.parse_args()


def extract_steps(answer: str) -> list[str]:
    steps: list[str] = []
    for line in answer.splitlines():
        match = re.match(r"^\s*\d+\.\s*(.+?)\s*$", line)
        if match:
            steps.append(match.group(1))
    return steps


def selected_job_ids(paths: list[str]) -> set[str]:
    selected: set[str] = set()
    for path_str in paths:
        selected.update(
            line.strip()
            for line in Path(path_str).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return selected


def build_parsed_response(job: dict) -> dict:
    task_type = job["task_type"]
    base = {
        "answer": "",
        "task_type": task_type,
        "needs_clarification": task_type == "clarification",
        "clarification_question": None,
        "escalate": task_type == "uncertainty_escalation",
        "uncertainty_reason": None,
        "steps": [],
        "source_chunk_ids": job["source_chunk_ids"],
        "notes": ["fixture import path for teacher replay validation"],
    }
    if job["expected_output_kind"] == "sft_sample":
        answer = job["fixture_payload"]["assistant_message"]
        base["answer"] = answer
        base["steps"] = extract_steps(answer)
        if task_type == "clarification":
            base["clarification_question"] = answer
        if task_type == "uncertainty_escalation":
            base["uncertainty_reason"] = "Unsicherheit aus dokumentierter Evidenzgrenze abgeleitet."
        return base

    reference_answer = job["fixture_payload"]["reference_answer"]
    base["answer"] = reference_answer
    base["steps"] = extract_steps(reference_answer)
    if task_type == "clarification":
        base["clarification_question"] = reference_answer
    if task_type == "uncertainty_escalation":
        base["uncertainty_reason"] = "Unsicherheit aus dokumentierter Evidenzgrenze abgeleitet."
    base["case_description"] = job["fixture_payload"]["case_description"]
    base["expected_behavior"] = job["fixture_payload"]["expected_behavior"]
    base["reference_answer"] = reference_answer
    base["rubric"] = job["fixture_payload"]["rubric"]
    return base


def build_response(job: dict, teacher_model: str, teacher_provider: str, teacher_run_id: str, jobs_path: str) -> dict:
    parsed_response = build_parsed_response(job)
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
        "generation_mode": GENERATION_MODE,
        "response_status": "imported",
        "response_format_version": RESPONSE_FORMAT_VERSION,
        "provider_response_id": None,
        "raw_text": json.dumps(parsed_response, ensure_ascii=False),
        "parsed_response": parsed_response,
        "usage": None,
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "source_job_path": jobs_path.replace("\\", "/"),
            "behavior_spec_path": job["behavior_spec_path"],
            "prompt_template_path": job["prompt_template_path"],
            "source_records": job["provenance"]["source_records"],
        },
    }


def main() -> None:
    args = parse_args()
    jobs = read_jsonl(Path(args.jobs))
    wanted = selected_job_ids(args.job_ids_file)
    if wanted:
        jobs = [job for job in jobs if job["job_id"] in wanted]
    if not jobs:
        raise SystemExit("No jobs selected for import fixture")

    output_rows = [
        build_response(
            job,
            teacher_model=args.teacher_model,
            teacher_provider=args.teacher_provider,
            teacher_run_id=args.teacher_run_id,
            jobs_path=args.jobs,
        )
        for job in jobs
    ]
    write_jsonl(Path(args.output), output_rows)
    print(f"Wrote {len(output_rows)} import fixture responses -> {args.output}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_jsonl


TRANSFORM_PIPELINE_VERSION = "0.4.0"


def build_sft_candidate(job: dict, teacher_model: str, teacher_run_id: str, generation_mode: str) -> dict:
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
            {"role": "user", "content": job["runner_input"]["user_message"]},
            {"role": "assistant", "content": job["fixture_payload"]["assistant_message"]},
        ],
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
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


def build_eval_candidate(job: dict, teacher_model: str, teacher_run_id: str, generation_mode: str) -> dict:
    return {
        "eval_id": f"{job['job_id']}__candidate",
        "product": job["product"],
        "language": job["language"],
        "case_type": job["task_type"],
        "prompt": job["runner_input"]["user_message"],
        "case_description": job["fixture_payload"]["case_description"],
        "expected_behavior": job["fixture_payload"]["expected_behavior"],
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": job["teacher_prompt_version"],
        "generation_mode": generation_mode,
        "review_status": "teacher_generated",
        "split": "eval",
        "approved_by": None,
        "promoted_from": None,
        "reference_answer": job["fixture_payload"]["reference_answer"],
        "rubric": job["fixture_payload"]["rubric"],
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


def build_output(job: dict, teacher_model: str, teacher_run_id: str, mode: str, replay_row: dict | None) -> dict:
    generation_mode = "teacher_runner_stub_v1" if mode == "stub" else "teacher_runner_replay_v1"
    if replay_row is not None:
        candidate = replay_row["candidate"]
        record_type = replay_row["record_type"]
    else:
        if job["expected_output_kind"] == "sft_sample":
            candidate = build_sft_candidate(job, teacher_model, teacher_run_id, generation_mode)
            record_type = "sft_sample"
        else:
            candidate = build_eval_candidate(job, teacher_model, teacher_run_id, generation_mode)
            record_type = "eval_case"

    return {
        "output_id": f"{teacher_run_id}::{job['job_id']}",
        "job_id": job["job_id"],
        "record_type": record_type,
        "target_split": job["target_split"],
        "product": job["product"],
        "language": job["language"],
        "task_type": job["task_type"],
        "source_doc_ids": job["source_doc_ids"],
        "source_chunk_ids": job["source_chunk_ids"],
        "teacher_model": teacher_model,
        "teacher_run_id": teacher_run_id,
        "teacher_prompt_version": job["teacher_prompt_version"],
        "generation_mode": generation_mode,
        "review_status": "teacher_generated",
        "approved_by": None,
        "promoted_to": None,
        "candidate": candidate,
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "source_job_path": "",
            "source_records": job["provenance"]["source_records"],
        },
    }


def parse_args() -> Any:
    parser = make_parser("Run teacher jobs in stub or replay mode and produce reviewable teacher outputs.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=["stub", "replay"], default="stub")
    parser.add_argument("--teacher-model", default="teacher-stub-no-llm")
    parser.add_argument("--teacher-run-id", default="teacher_stub_run_v1")
    parser.add_argument("--replay-input")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    jobs_path = Path(args.jobs)
    jobs = read_jsonl(jobs_path)
    replay_rows = replay_index(read_jsonl(Path(args.replay_input))) if args.mode == "replay" else {}

    outputs = []
    for job in jobs:
        replay_row = replay_rows.get(job["job_id"])
        if args.mode == "replay" and replay_row is None:
            raise SystemExit(f"Replay input missing job_id {job['job_id']}")
        output = build_output(job, args.teacher_model, args.teacher_run_id, args.mode, replay_row)
        output["provenance"]["source_job_path"] = str(jobs_path).replace("\\", "/")
        outputs.append(output)

    write_jsonl(Path(args.output), outputs)
    print(f"Wrote {len(outputs)} teacher outputs -> {args.output}")


if __name__ == "__main__":
    main()

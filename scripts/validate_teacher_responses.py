from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from common import make_parser, read_json, read_jsonl


def parse_args() -> Any:
    parser = make_parser("Validate raw/imported teacher responses against jobs and schema.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--schema", default="schemas/teacher_response.schema.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    jobs = {row["job_id"]: row for row in read_jsonl(Path(args.jobs))}
    rows = read_jsonl(Path(args.input))
    validator = Draft202012Validator(read_json(Path(args.schema)))

    failures: list[str] = []
    seen_job_ids: set[str] = set()

    for idx, row in enumerate(rows, start=1):
        for error in validator.iter_errors(row):
            failures.append(f"Teacher response row {idx}: {error.message}")

        job_id = row.get("job_id")
        if job_id in seen_job_ids:
            failures.append(f"Teacher response row {idx}: duplicate job_id {job_id}")
        seen_job_ids.add(job_id)

        job = jobs.get(job_id)
        if job is None:
            failures.append(f"Teacher response row {idx}: unknown job_id {job_id}")
            continue

        if row.get("output_id") != f"{row.get('teacher_run_id')}::{job_id}":
            failures.append(f"Teacher response row {idx}: output_id does not match teacher_run_id/job_id")
        if row.get("record_type") != job.get("expected_output_kind"):
            failures.append(f"Teacher response row {idx}: record_type mismatch")
        if row.get("target_split") != job.get("target_split"):
            failures.append(f"Teacher response row {idx}: target_split mismatch")
        if row.get("task_type") != job.get("task_type"):
            failures.append(f"Teacher response row {idx}: task_type mismatch")
        if row.get("source_chunk_ids") != job.get("source_chunk_ids"):
            failures.append(f"Teacher response row {idx}: source_chunk_ids mismatch")
        if row.get("source_doc_ids") != job.get("source_doc_ids"):
            failures.append(f"Teacher response row {idx}: source_doc_ids mismatch")
        if row.get("teacher_prompt_version") != job.get("teacher_prompt_version"):
            failures.append(f"Teacher response row {idx}: teacher_prompt_version mismatch")

        parsed = row.get("parsed_response", {})
        if parsed.get("task_type") != job.get("task_type"):
            failures.append(f"Teacher response row {idx}: parsed_response.task_type mismatch")
        if parsed.get("source_chunk_ids") != job.get("source_chunk_ids"):
            failures.append(f"Teacher response row {idx}: parsed_response.source_chunk_ids mismatch")
        if not parsed.get("answer"):
            failures.append(f"Teacher response row {idx}: empty parsed answer")
        if row.get("record_type") == "eval_case":
            if not parsed.get("reference_answer"):
                failures.append(f"Teacher response row {idx}: eval response missing reference_answer")
            rubric = parsed.get("rubric") or {}
            if not isinstance(rubric.get("must_include"), list):
                failures.append(f"Teacher response row {idx}: eval response missing rubric.must_include")
            if not isinstance(rubric.get("must_not_include"), list):
                failures.append(f"Teacher response row {idx}: eval response missing rubric.must_not_include")
            if not rubric.get("style"):
                failures.append(f"Teacher response row {idx}: eval response missing rubric.style")

    if failures:
        print("\n".join(failures))
        raise SystemExit(1)

    print(f"OK: {len(rows)} teacher responses validated against {len(jobs)} jobs")


if __name__ == "__main__":
    main()

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from common import make_parser, read_json, read_jsonl
from teacher_quality_gates import blocking_artifact_reasons


REVIEW_STATUSES = {"draft", "seed", "teacher_generated", "human_reviewed", "promoted", "rejected"}


def load_chunks(chunks_root: Path) -> dict[str, dict]:
    chunk_index: dict[str, dict] = {}
    for path in sorted(chunks_root.glob("*/chunks.jsonl")):
        for row in read_jsonl(path):
            chunk_index[row["chunk_id"]] = row
    if not chunk_index:
        raise SystemExit(f"No chunk files found under {chunks_root}")
    return chunk_index


def validate_chunk_links(prefix: str, row: dict, chunk_index: dict[str, dict], failures: list[str]) -> None:
    for chunk_id in row.get("source_chunk_ids", []):
        if chunk_id not in chunk_index:
            failures.append(f"{prefix}: unknown chunk_id {chunk_id}")
            continue
        chunk = chunk_index[chunk_id]
        if chunk["doc_id"] not in row.get("source_doc_ids", []):
            failures.append(f"{prefix}: doc/chunk mismatch for {chunk_id}")


def validate_jobs(rows: list[dict], validator: Draft202012Validator, chunk_index: dict[str, dict]) -> tuple[list[str], dict[str, dict]]:
    failures: list[str] = []
    job_index: dict[str, dict] = {}
    job_keys: set[tuple[str, str, tuple[str, ...]]] = set()
    for idx, row in enumerate(rows, start=1):
        for error in validator.iter_errors(row):
            failures.append(f"Job row {idx}: {error.message}")
        job_index[row["job_id"]] = row
        key = (row.get("target_split"), row.get("task_type"), tuple(row.get("source_chunk_ids", [])))
        if key in job_keys:
            failures.append(f"Job row {idx}: duplicate split/task/chunk combination")
        job_keys.add(key)
        if row.get("job_status") not in REVIEW_STATUSES:
            failures.append(f"Job row {idx}: invalid job_status {row.get('job_status')}")
        if row.get("review_status") not in REVIEW_STATUSES:
            failures.append(f"Job row {idx}: invalid review_status {row.get('review_status')}")
        if row.get("job_status") != row.get("review_status"):
            failures.append(f"Job row {idx}: job_status/review_status mismatch")
        validate_chunk_links(f"Job row {idx}", row, chunk_index, failures)
    return failures, job_index


def validate_candidate(candidate: dict, record_type: str, sft_validator: Draft202012Validator, eval_validator: Draft202012Validator) -> list[str]:
    errors: list[str] = []
    validator = sft_validator if record_type == "sft_sample" else eval_validator
    label = "SFT candidate" if record_type == "sft_sample" else "Eval candidate"
    for error in validator.iter_errors(candidate):
        errors.append(f"{label}: {error.message}")
    return errors


def validate_outputs(
    rows: list[dict],
    validator: Draft202012Validator,
    job_index: dict[str, dict],
    chunk_index: dict[str, dict],
    sft_validator: Draft202012Validator,
    eval_validator: Draft202012Validator,
) -> tuple[list[str], dict[str, dict]]:
    failures: list[str] = []
    output_index: dict[str, dict] = {}
    output_keys: set[tuple[str, str, tuple[str, ...]]] = set()
    for idx, row in enumerate(rows, start=1):
        for error in validator.iter_errors(row):
            failures.append(f"Output row {idx}: {error.message}")
        output_index[row["output_id"]] = row
        key = (row.get("target_split"), row.get("task_type"), tuple(row.get("source_chunk_ids", [])))
        if key in output_keys:
            failures.append(f"Output row {idx}: duplicate split/task/chunk combination")
        output_keys.add(key)
        job = job_index.get(row["job_id"])
        if job is None:
            failures.append(f"Output row {idx}: unknown job_id {row['job_id']}")
            continue
        if row.get("review_status") not in REVIEW_STATUSES:
            failures.append(f"Output row {idx}: invalid review_status {row.get('review_status')}")
        if row.get("record_type") != job.get("expected_output_kind"):
            failures.append(f"Output row {idx}: record_type does not match job")
        if row.get("target_split") != job.get("target_split"):
            failures.append(f"Output row {idx}: target_split does not match job")
        if row.get("source_chunk_ids") != job.get("source_chunk_ids"):
            failures.append(f"Output row {idx}: source_chunk_ids differ from job")
        if row.get("teacher_provider") in {None, ""}:
            failures.append(f"Output row {idx}: teacher_provider missing")
        candidate = row.get("candidate", {})
        failures.extend(f"Output row {idx}: {err}" for err in validate_candidate(candidate, row["record_type"], sft_validator, eval_validator))
        if candidate.get("review_status") != row.get("review_status"):
            failures.append(f"Output row {idx}: candidate review_status mismatch")
        if candidate.get("teacher_model") != row.get("teacher_model"):
            failures.append(f"Output row {idx}: candidate teacher_model mismatch")
        if candidate.get("teacher_run_id") != row.get("teacher_run_id"):
            failures.append(f"Output row {idx}: candidate teacher_run_id mismatch")
        if candidate.get("teacher_provider") not in {None, row.get("teacher_provider")}:
            failures.append(f"Output row {idx}: candidate teacher_provider mismatch")
        if row.get("review_status") in {"human_reviewed", "rejected"} and not row.get("approved_by"):
            failures.append(f"Output row {idx}: approved_by required for reviewed outputs")
        if row.get("review_status") in {"human_reviewed", "promoted"}:
            artifact_reasons = blocking_artifact_reasons(row)
            if artifact_reasons:
                failures.append(f"Output row {idx}: blocking artifacts present: {'; '.join(artifact_reasons)}")
        validate_chunk_links(f"Output row {idx}", row, chunk_index, failures)
    return failures, output_index


def validate_gold(
    rows: list[dict],
    validator: Draft202012Validator,
    output_index: dict[str, dict],
    kind: str,
) -> list[str]:
    failures: list[str] = []
    for idx, row in enumerate(rows, start=1):
        for error in validator.iter_errors(row):
            failures.append(f"{kind} gold row {idx}: {error.message}")
        if row.get("review_status") != "promoted":
            failures.append(f"{kind} gold row {idx}: review_status must be promoted")
        promoted_from = row.get("promoted_from") or {}
        output_id = promoted_from.get("output_id")
        if not output_id:
            failures.append(f"{kind} gold row {idx}: missing promoted_from.output_id")
            continue
        source_output = output_index.get(output_id)
        if source_output is None:
            failures.append(f"{kind} gold row {idx}: promoted_from.output_id not found")
            continue
        if source_output.get("review_status") != "human_reviewed":
            failures.append(f"{kind} gold row {idx}: source output is not human_reviewed")
    return failures


def load_jsonl_rows(path: str | None, directory: str | None) -> list[dict]:
    rows: list[dict] = []
    if path:
        rows.extend(read_jsonl(Path(path)))
    if directory:
        for jsonl_path in sorted(Path(directory).glob("*.jsonl")):
            rows.extend(read_jsonl(jsonl_path))
    return rows


def validate_gold_uniqueness(rows: list[dict], *, kind: str, key_field: str) -> list[str]:
    failures: list[str] = []
    chunk_counter: Counter[str] = Counter()
    id_counter: Counter[str] = Counter()
    for row in rows:
        for chunk_id in row.get("source_chunk_ids", []):
            chunk_counter[chunk_id] += 1
        item_id = row.get(key_field)
        if item_id:
            id_counter[item_id] += 1
    duplicate_chunks = sorted(chunk_id for chunk_id, count in chunk_counter.items() if count > 1)
    if duplicate_chunks:
        failures.append(f"{kind} gold duplicate chunk_ids detected: " + ", ".join(duplicate_chunks[:10]))
    duplicate_ids = sorted(item_id for item_id, count in id_counter.items() if count > 1)
    if duplicate_ids:
        failures.append(f"{kind} gold duplicate ids detected: " + ", ".join(duplicate_ids[:10]))
    return failures


def parse_args() -> Any:
    parser = make_parser("Validate teacher jobs, teacher outputs and promoted gold artifacts.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--outputs", required=True)
    parser.add_argument("--chunks-root", default="data/derived/chunks/JAWS/DE")
    parser.add_argument("--job-schema", default="schemas/teacher_job.schema.json")
    parser.add_argument("--output-schema", default="schemas/teacher_output.schema.json")
    parser.add_argument("--sft-schema", default="schemas/sft_sample.schema.json")
    parser.add_argument("--eval-schema", default="schemas/eval_case.schema.json")
    parser.add_argument("--gold-sft")
    parser.add_argument("--gold-eval")
    parser.add_argument("--gold-sft-dir")
    parser.add_argument("--gold-eval-dir")
    parser.add_argument("--require-all-task-types", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    chunk_index = load_chunks(Path(args.chunks_root))
    jobs = read_jsonl(Path(args.jobs))
    outputs = read_jsonl(Path(args.outputs))

    job_validator = Draft202012Validator(read_json(Path(args.job_schema)))
    output_validator = Draft202012Validator(read_json(Path(args.output_schema)))
    sft_validator = Draft202012Validator(read_json(Path(args.sft_schema)))
    eval_validator = Draft202012Validator(read_json(Path(args.eval_schema)))

    failures, job_index = validate_jobs(jobs, job_validator, chunk_index)
    output_failures, output_index = validate_outputs(
        outputs,
        output_validator,
        job_index,
        chunk_index,
        sft_validator,
        eval_validator,
    )
    failures.extend(output_failures)

    gold_train_rows: list[dict] = []
    gold_eval_rows: list[dict] = []
    if args.gold_sft or args.gold_sft_dir:
        gold_train_rows = load_jsonl_rows(args.gold_sft, args.gold_sft_dir)
        failures.extend(validate_gold(gold_train_rows, sft_validator, output_index, "Train"))
        failures.extend(validate_gold_uniqueness(gold_train_rows, kind="Train", key_field="id"))
    if args.gold_eval or args.gold_eval_dir:
        gold_eval_rows = load_jsonl_rows(args.gold_eval, args.gold_eval_dir)
        failures.extend(validate_gold(gold_eval_rows, eval_validator, output_index, "Eval"))
        failures.extend(validate_gold_uniqueness(gold_eval_rows, kind="Eval", key_field="eval_id"))

    train_chunk_ids = {chunk_id for row in gold_train_rows for chunk_id in row.get("source_chunk_ids", [])}
    eval_chunk_ids = {chunk_id for row in gold_eval_rows for chunk_id in row.get("source_chunk_ids", [])}
    overlap = sorted(train_chunk_ids & eval_chunk_ids)
    if overlap:
        failures.append("Gold train/eval chunk overlap detected: " + ", ".join(overlap[:10]))

    if args.require_all_task_types:
        expected = {
            "faq_direct_answer",
            "troubleshooting",
            "step_by_step",
            "clarification",
            "uncertainty_escalation",
        }
        job_types = {row.get("task_type") for row in jobs}
        output_types = {row.get("task_type") for row in outputs}
        missing_jobs = sorted(expected - job_types)
        missing_outputs = sorted(expected - output_types)
        if missing_jobs:
            failures.append("Missing task types in jobs: " + ", ".join(missing_jobs))
        if missing_outputs:
            failures.append("Missing task types in outputs: " + ", ".join(missing_outputs))
        if gold_train_rows:
            missing_gold_train = sorted(expected - {row.get("task_type") for row in gold_train_rows})
            if missing_gold_train:
                failures.append("Missing task types in gold train: " + ", ".join(missing_gold_train))
        if gold_eval_rows:
            eval_types = {row.get("case_type") for row in gold_eval_rows}
            missing_gold_eval = sorted(expected - eval_types)
            if missing_gold_eval:
                failures.append("Missing task types in gold eval: " + ", ".join(missing_gold_eval))

    if failures:
        print("\n".join(failures))
        raise SystemExit(1)

    print(
        f"OK: {len(jobs)} jobs, {len(outputs)} teacher outputs, "
        f"{len(gold_train_rows)} gold train, {len(gold_eval_rows)} gold eval"
    )


if __name__ == "__main__":
    main()

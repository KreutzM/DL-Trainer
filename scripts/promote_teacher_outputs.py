from __future__ import annotations

from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_jsonl
from teacher_quality_gates import blocking_artifact_reasons


def build_promoted_from(row: dict, input_path: str) -> dict:
    return {
        "teacher_output_path": input_path.replace("\\", "/"),
        "output_id": row["output_id"],
        "job_id": row["job_id"],
        "teacher_provider": row.get("teacher_provider"),
        "teacher_model": row.get("teacher_model"),
        "teacher_run_id": row["teacher_run_id"],
    }


def promote_sft(row: dict, input_path: str) -> dict:
    candidate = dict(row["candidate"])
    candidate["review_status"] = "promoted"
    candidate["split"] = "train"
    candidate["approved_by"] = row.get("approved_by")
    candidate["promoted_from"] = build_promoted_from(row, input_path)
    candidate["meta"]["review_status"] = "promoted"
    candidate["meta"]["split"] = "train"
    candidate["meta"]["approved_by"] = row.get("approved_by")
    candidate["meta"]["promoted_from"] = build_promoted_from(row, input_path)
    return candidate


def promote_eval(row: dict, input_path: str) -> dict:
    candidate = dict(row["candidate"])
    candidate["review_status"] = "promoted"
    candidate["split"] = "eval"
    candidate["approved_by"] = row.get("approved_by")
    candidate["promoted_from"] = build_promoted_from(row, input_path)
    return candidate


def parse_args() -> Any:
    parser = make_parser("Promote human-reviewed teacher outputs into gold train/eval artifacts.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--train-output", required=True)
    parser.add_argument("--eval-output", required=True)
    parser.add_argument("--allow-codex-reviewed", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input
    rows = read_jsonl(Path(input_path))

    allowed_statuses = {"human_reviewed"}
    if args.allow_codex_reviewed:
        allowed_statuses.add("codex_reviewed")
    approved = [row for row in rows if row.get("review_status") in allowed_statuses]
    if not approved:
        raise SystemExit("No approved teacher outputs found to promote")

    blocking_failures: list[str] = []
    for row in approved:
        reasons = blocking_artifact_reasons(row)
        if reasons:
            blocking_failures.append(f"{row['output_id']}: " + "; ".join(reasons))
    if blocking_failures:
        raise SystemExit(
            "Cannot promote approved outputs with blocking artifacts:\n" + "\n".join(blocking_failures)
        )

    train_rows: list[dict] = []
    eval_rows: list[dict] = []
    train_chunk_ids: set[str] = set()
    eval_chunk_ids: set[str] = set()
    promoted_output_ids: set[str] = set()

    for row in approved:
        if row["output_id"] in promoted_output_ids:
            raise SystemExit(f"Duplicate promoted output_id {row['output_id']}")
        promoted_output_ids.add(row["output_id"])

        source_chunk_ids = set(row.get("source_chunk_ids", []))
        if row["record_type"] == "sft_sample":
            if source_chunk_ids & eval_chunk_ids:
                raise SystemExit(f"Train/eval chunk overlap during promotion: {row['output_id']}")
            train_chunk_ids.update(source_chunk_ids)
            train_rows.append(promote_sft(row, input_path))
        elif row["record_type"] == "eval_case":
            if source_chunk_ids & train_chunk_ids:
                raise SystemExit(f"Train/eval chunk overlap during promotion: {row['output_id']}")
            eval_chunk_ids.update(source_chunk_ids)
            eval_rows.append(promote_eval(row, input_path))
        else:
            raise SystemExit(f"Unknown record_type {row['record_type']}")

    write_jsonl(Path(args.train_output), train_rows)
    write_jsonl(Path(args.eval_output), eval_rows)
    print(
        f"Wrote promoted gold artifacts -> train={len(train_rows)} {args.train_output}, "
        f"eval={len(eval_rows)} {args.eval_output}"
    )


if __name__ == "__main__":
    main()

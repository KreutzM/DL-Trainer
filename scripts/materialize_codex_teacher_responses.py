from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json, write_jsonl


TRANSFORM_PIPELINE_VERSION = "0.6.0"
RAW_RESPONSE_FORMAT_VERSION = "teacher_response_v1"


def parse_args() -> Any:
    parser = make_parser(
        "Materialize structured Codex GPT-5.4 teacher responses from reviewed teacher candidates."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--job-ids-file", action="append", default=[])
    parser.add_argument("--output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--teacher-run-id", required=True)
    parser.add_argument("--teacher-model", default="gpt-5.4")
    parser.add_argument("--teacher-provider", default="codex")
    parser.add_argument("--generation-mode", default="codex_teacher_gpt54_wave1_v2")
    return parser.parse_args()


def load_selected_job_ids(paths: list[str]) -> set[str]:
    selected: set[str] = set()
    for path_str in paths:
        selected.update(
            line.strip()
            for line in Path(path_str).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return selected


def extract_assistant_text(candidate: dict) -> str:
    for message in candidate.get("messages", []):
        if message.get("role") == "assistant":
            text = str(message.get("content", "")).strip()
            if text:
                return text
    raise SystemExit("Missing assistant message in SFT candidate")


def extract_steps(answer: str) -> list[str]:
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    steps: list[str] = []
    for line in lines:
        match = re.match(r"^\d+\.\s+(.*)$", line)
        if match:
            steps.append(match.group(1).strip())
    return steps


def build_notes(task_type: str, record_type: str, section_title: str) -> list[str]:
    kind = "Eval-Referenz" if record_type == "eval_case" else "Supportantwort"
    return [f"{kind} aus dem Abschnitt {section_title}.", f"Codex-kuratierte Wave1-Antwort fuer {task_type}."]


def build_parsed_response(row: dict) -> dict:
    candidate = row["candidate"]
    task_type = row["task_type"]
    record_type = row["record_type"]
    section_title = row["provenance"]["source_records"][0].get("section_title", "Unbekannter Abschnitt")

    if record_type == "sft_sample":
        answer = extract_assistant_text(candidate)
    else:
        answer = candidate["reference_answer"].strip()

    parsed = {
        "answer": answer,
        "task_type": task_type,
        "needs_clarification": task_type == "clarification",
        "clarification_question": answer if task_type == "clarification" else None,
        "escalate": task_type == "uncertainty_escalation",
        "uncertainty_reason": (
            "Die Quelle belegt nur den beschriebenen Kontext und keine allgemeine Zusage."
            if task_type == "uncertainty_escalation"
            else None
        ),
        "steps": extract_steps(answer) if task_type == "step_by_step" else [],
        "source_chunk_ids": row["source_chunk_ids"],
        "notes": build_notes(task_type, record_type, section_title),
    }
    if record_type == "eval_case":
        parsed["case_description"] = candidate["case_description"]
        parsed["expected_behavior"] = candidate["expected_behavior"]
        parsed["reference_answer"] = candidate["reference_answer"]
        parsed["rubric"] = candidate["rubric"]
    return parsed


def main() -> None:
    args = parse_args()
    rows = read_jsonl(Path(args.input))
    selected_job_ids = load_selected_job_ids(args.job_ids_file)
    if selected_job_ids:
        rows = [row for row in rows if row["job_id"] in selected_job_ids]
    rows = [
        row
        for row in rows
        if row.get("review_status") == "human_reviewed" and row.get("approved_by")
    ]
    rows.sort(
        key=lambda row: (
            row["target_split"],
            row["task_type"],
            row["source_doc_ids"][0],
            row["job_id"],
        )
    )
    if not rows:
        raise SystemExit("No reviewed rows selected")

    source_job_path = str(Path(args.jobs)).replace("\\", "/")
    raw_rows: list[dict] = []
    for row in rows:
        candidate_provenance = row["candidate"]["provenance"]
        parsed = build_parsed_response(row)
        raw_rows.append(
            {
                "response_id": f"{args.teacher_run_id}::{row['job_id']}::response",
                "job_id": row["job_id"],
                "output_id": f"{args.teacher_run_id}::{row['job_id']}",
                "wave_id": row.get("wave_id"),
                "record_type": row["record_type"],
                "target_split": row["target_split"],
                "product": row["product"],
                "language": row["language"],
                "task_type": row["task_type"],
                "source_doc_ids": row["source_doc_ids"],
                "source_chunk_ids": row["source_chunk_ids"],
                "teacher_provider": args.teacher_provider,
                "teacher_model": args.teacher_model,
                "teacher_run_id": args.teacher_run_id,
                "teacher_prompt_version": row["teacher_prompt_version"],
                "generation_mode": args.generation_mode,
                "response_status": "completed",
                "response_format_version": RAW_RESPONSE_FORMAT_VERSION,
                "provider_response_id": None,
                "raw_text": json.dumps(parsed, ensure_ascii=False),
                "parsed_response": parsed,
                "usage": None,
                "provenance": {
                    "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
                    "source_job_path": source_job_path,
                    "behavior_spec_path": candidate_provenance["behavior_spec_path"],
                    "prompt_template_path": candidate_provenance["prompt_template_path"],
                    "source_records": candidate_provenance["source_records"],
                },
            }
        )

    write_jsonl(Path(args.output), raw_rows)
    report = {
        "batch_name": "wave1_codex_gpt54_real_batch_v1",
        "source_reviewed_outputs": args.input.replace("\\", "/"),
        "jobs_path": source_job_path,
        "teacher_run_id": args.teacher_run_id,
        "teacher_provider": args.teacher_provider,
        "teacher_model": args.teacher_model,
        "generation_mode": args.generation_mode,
        "raw_responses": len(raw_rows),
        "by_split": dict(Counter(row["target_split"] for row in raw_rows)),
        "by_task_type": dict(Counter(row["task_type"] for row in raw_rows)),
        "by_doc": dict(Counter(row["source_doc_ids"][0] for row in raw_rows)),
    }
    write_json(Path(args.report_output), report)

    print(f"Wrote {len(raw_rows)} raw teacher responses -> {args.output}")
    print(f"Wrote report -> {args.report_output}")


if __name__ == "__main__":
    main()

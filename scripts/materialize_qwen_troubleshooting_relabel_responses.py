from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json, write_jsonl


TRANSFORM_PIPELINE_VERSION = "0.7.0"
RAW_RESPONSE_FORMAT_VERSION = "teacher_response_v1"

SPAN_RANGE_RE = re.compile(r"(.+)#L(\d+)-L(\d+)$")
SPAN_SINGLE_RE = re.compile(r"(.+)#L(\d+)$")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def parse_args() -> Any:
    parser = make_parser(
        "Materialize codex-style raw teacher responses for the unresolved Qwen troubleshooting relabel wave."
    )
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--reviewed-input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--job-ids-output", required=True)
    parser.add_argument("--teacher-run-id", required=True)
    parser.add_argument("--teacher-model", default="gpt-5.4")
    parser.add_argument("--teacher-provider", default="codex")
    parser.add_argument("--generation-mode", default="codex_teacher_qwen_troubleshooting_relabel_v1")
    return parser.parse_args()


def normalized_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def strip_markdown(text: str) -> str:
    text = MARKDOWN_LINK_RE.sub(r"\1", text)
    text = text.replace("**", "")
    text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_line(text: str) -> str:
    text = strip_markdown(text)
    text = re.sub(r"^\d+\.\s*", "", text)
    return text.strip().strip("- ").strip()


def read_span_text(span: str) -> str:
    range_match = SPAN_RANGE_RE.match(span)
    single_match = SPAN_SINGLE_RE.match(span)
    if range_match:
        path_str, start_str, end_str = range_match.groups()
        start = int(start_str)
        end = int(end_str)
    elif single_match:
        path_str, start_str = single_match.groups()
        start = int(start_str)
        end = start
    else:
        return ""
    path = Path(path_str)
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[max(0, start - 1) : min(len(lines), end)])


def table_descriptions(lines: list[str]) -> list[str]:
    labels: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) < 2:
            continue
        first = clean_line(parts[0])
        if not first or first.lower() in {"beschreibung", "---"}:
            continue
        labels.append(first)
    return labels


def prose_sentences(lines: list[str]) -> list[str]:
    text = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            continue
        if stripped.lower().startswith("quelle:"):
            continue
        if stripped.lower().startswith("tabelle:"):
            continue
        text.append(stripped)
    joined = " ".join(text)
    joined = strip_markdown(joined)
    parts = re.split(r"(?<=[.!?])\s+", joined)
    sentences: list[str] = []
    seen: set[str] = set()
    for part in parts:
        sentence = clean_line(part)
        if not sentence:
            continue
        lowered = sentence.casefold()
        if lowered in seen:
            continue
        seen.add(lowered)
        sentences.append(sentence)
    return sentences


def join_with_und(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} und {items[1]}"
    return ", ".join(items[:-1]) + f" und {items[-1]}"


def build_answer(source_text: str) -> str:
    lines = source_text.splitlines()
    sentences = prose_sentences(lines)
    table_labels = table_descriptions(lines)

    if sentences:
        answer = " ".join(sentences[:2])
    else:
        answer = ""

    if table_labels:
        subset = table_labels[:4]
        table_sentence = f"Die Dokumentation listet dazu unter anderem {join_with_und(subset)}."
        if answer:
            if table_sentence.casefold() not in answer.casefold():
                answer = f"{answer} {table_sentence}"
        else:
            answer = table_sentence

    answer = re.sub(r"\s+", " ", answer).strip()
    answer = answer.replace(" ,", ",")
    return answer


def build_parsed_response(job: dict, answer: str) -> dict:
    section_title = job["provenance"]["source_records"][0].get("section_title", "Unbekannter Abschnitt")
    return {
        "answer": answer,
        "task_type": job["task_type"],
        "needs_clarification": False,
        "clarification_question": None,
        "escalate": False,
        "uncertainty_reason": None,
        "steps": [],
        "source_chunk_ids": job["source_chunk_ids"],
        "notes": [
            f"Codex-kuratierte FAQ-Antwort aus dem Abschnitt {section_title}.",
            "Aus den referenzierten normalized source spans ohne Stub-Truncation materialisiert.",
        ],
    }


def main() -> None:
    args = parse_args()
    jobs = read_jsonl(Path(args.jobs))
    reviewed_rows = read_jsonl(Path(args.reviewed_input))

    rejected_by_job_id = {
        row["job_id"]: row
        for row in reviewed_rows
        if row.get("review_status") == "rejected"
    }
    selected_jobs = [job for job in jobs if job["job_id"] in rejected_by_job_id]
    if not selected_jobs:
        raise SystemExit("No rejected relabel jobs found")

    raw_rows: list[dict] = []
    selected_job_ids: list[str] = []
    skipped_jobs: list[dict[str, str]] = []
    for job in selected_jobs:
        source_parts: list[str] = []
        for record in job["provenance"]["source_records"]:
            for span in record.get("source_spans", []):
                text = read_span_text(str(span))
                if text:
                    source_parts.append(text)
        source_text = "\n".join(part for part in source_parts if part).strip()
        if not source_text:
            skipped_jobs.append({"job_id": job["job_id"], "reason": "missing_source_text"})
            continue
        answer = build_answer(source_text)
        if not answer:
            skipped_jobs.append({"job_id": job["job_id"], "reason": "empty_answer"})
            continue

        parsed_response = build_parsed_response(job, answer)
        raw_rows.append(
            {
                "response_id": f"{args.teacher_run_id}::{job['job_id']}::response",
                "job_id": job["job_id"],
                "output_id": f"{args.teacher_run_id}::{job['job_id']}",
                "wave_id": job.get("wave_id"),
                "record_type": job["expected_output_kind"],
                "target_split": job["target_split"],
                "product": job["product"],
                "language": job["language"],
                "task_type": job["task_type"],
                "source_doc_ids": job["source_doc_ids"],
                "source_chunk_ids": job["source_chunk_ids"],
                "teacher_provider": args.teacher_provider,
                "teacher_model": args.teacher_model,
                "teacher_run_id": args.teacher_run_id,
                "teacher_prompt_version": job["teacher_prompt_version"],
                "generation_mode": args.generation_mode,
                "response_status": "completed",
                "response_format_version": RAW_RESPONSE_FORMAT_VERSION,
                "provider_response_id": None,
                "raw_text": json.dumps(parsed_response, ensure_ascii=False),
                "parsed_response": parsed_response,
                "usage": None,
                "provenance": {
                    "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
                    "source_job_path": normalized_path(args.jobs),
                    "behavior_spec_path": job["behavior_spec_path"],
                    "prompt_template_path": job["prompt_template_path"],
                    "source_records": job["provenance"]["source_records"],
                },
            }
        )
        selected_job_ids.append(job["job_id"])

    write_jsonl(Path(args.output), raw_rows)
    Path(args.job_ids_output).write_text(
        "\n".join(selected_job_ids) + ("\n" if selected_job_ids else ""), encoding="utf-8"
    )
    report = {
        "jobs_path": normalized_path(args.jobs),
        "reviewed_input": normalized_path(args.reviewed_input),
        "teacher_run_id": args.teacher_run_id,
        "teacher_provider": args.teacher_provider,
        "teacher_model": args.teacher_model,
        "generation_mode": args.generation_mode,
        "rejected_jobs_found": len(selected_jobs),
        "raw_responses_written": len(raw_rows),
        "skipped_jobs": skipped_jobs,
        "by_doc": dict(Counter(row["source_doc_ids"][0] for row in raw_rows)),
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(raw_rows)} raw responses -> {args.output}")
    print(f"Wrote {len(selected_job_ids)} job ids -> {args.job_ids_output}")
    print(f"Wrote report -> {args.report_output}")


if __name__ == "__main__":
    main()

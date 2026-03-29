from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from build_jaws_teacher_wave import BEHAVIOR_SPEC_PATH, build_job, build_faq_case, load_chunks
from common import make_parser, read_json, write_json, write_jsonl


DEFAULT_REVIEWED_PACKET = "data/derived/teacher_outputs/JAWS/DE/qwen_troubleshooting_cleanup_wave1_reviewed_packet.json"
DEFAULT_CHUNKS_ROOT = "data/derived/chunks/JAWS/DE"
DEFAULT_JOBS_OUTPUT = "data/derived/teacher_jobs/JAWS/DE/qwen_troubleshooting_relabel_wave1_generation_jobs.jsonl"
DEFAULT_REPORT_OUTPUT = "data/derived/teacher_jobs/JAWS/DE/qwen_troubleshooting_relabel_wave1_generation_report.json"
DEFAULT_IDS_OUTPUT = "data/derived/teacher_jobs/JAWS/DE/qwen_troubleshooting_relabel_wave1_job_ids.txt"
DEFAULT_WAVE_ID = "jaws_de_teacher_qwen_troubleshooting_relabel_wave_v1"


def parse_args() -> Any:
    parser = make_parser("Build a FAQ relabel wave from reviewed troubleshooting cleanup decisions.")
    parser.add_argument("--reviewed-packet", default=DEFAULT_REVIEWED_PACKET)
    parser.add_argument("--chunks-root", default=DEFAULT_CHUNKS_ROOT)
    parser.add_argument("--jobs-output", default=DEFAULT_JOBS_OUTPUT)
    parser.add_argument("--report-output", default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--ids-output", default=DEFAULT_IDS_OUTPUT)
    parser.add_argument("--wave-id", default=DEFAULT_WAVE_ID)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reviewed_packet = read_json(Path(args.reviewed_packet))
    reviewed_entries = reviewed_packet.get("entries", [])
    relabel_entries = [
        entry for entry in reviewed_entries if entry.get("final_decision") == "relabel_to_faq_direct_answer"
    ]
    if not relabel_entries:
        raise SystemExit("No relabel_to_faq_direct_answer entries found in reviewed packet")

    chunk_index = {chunk["chunk_id"]: chunk for chunk in load_chunks(Path(args.chunks_root))}
    system_prompt = Path(BEHAVIOR_SPEC_PATH).read_text(encoding="utf-8").strip()

    jobs: list[dict[str, Any]] = []
    missing_chunk_ids: list[str] = []
    skipped_ids: list[dict[str, str]] = []
    by_doc: Counter[str] = Counter()
    by_quality_score: Counter[int] = Counter()
    counters: Counter[str] = Counter()

    for entry in relabel_entries:
        chunk_id = entry["chunk_id"]
        chunk = chunk_index.get(chunk_id)
        if chunk is None:
            missing_chunk_ids.append(chunk_id)
            continue
        draft = build_faq_case(chunk)
        if draft is None:
            skipped_ids.append({"id": entry["id"], "chunk_id": chunk_id, "reason": "faq_case_not_buildable"})
            continue
        counters[draft.task_type] += 1
        job = build_job("train", counters[draft.task_type], chunk, draft, system_prompt, args.wave_id)
        job["relabel_source_id"] = entry["id"]
        job["relabel_source_line_number"] = entry.get("line_number")
        job["relabel_source_task_type"] = entry.get("task_type")
        job["relabel_reason"] = entry.get("review_note")
        jobs.append(job)
        by_doc.update([chunk["doc_id"]])
        by_quality_score.update([int(job.get("quality_score") or 0)])

    write_jsonl(Path(args.jobs_output), jobs)
    ids_output = Path(args.ids_output)
    ids_output.parent.mkdir(parents=True, exist_ok=True)
    ids_output.write_text("\n".join(job["job_id"] for job in jobs) + ("\n" if jobs else ""), encoding="utf-8")

    report = {
        "wave_id": args.wave_id,
        "source_reviewed_packet": args.reviewed_packet,
        "requested_relabels": len(relabel_entries),
        "selected_jobs": len(jobs),
        "selected_by_task_type": dict(Counter(job["task_type"] for job in jobs)),
        "selected_by_doc": dict(by_doc),
        "quality_score_range": {
            "min": min(by_quality_score) if by_quality_score else 0,
            "max": max(by_quality_score) if by_quality_score else 0,
        },
        "missing_chunk_ids": missing_chunk_ids,
        "skipped_entries": skipped_ids,
        "ids_output": args.ids_output,
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(jobs)} troubleshooting relabel jobs -> {args.jobs_output}")
    print(f"Wrote troubleshooting relabel report -> {args.report_output}")
    print(f"Wrote troubleshooting relabel ids -> {args.ids_output}")


if __name__ == "__main__":
    main()

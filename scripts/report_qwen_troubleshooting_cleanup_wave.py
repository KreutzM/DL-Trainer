from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from build_jaws_teacher_wave import load_chunks
from common import make_parser, write_json


DEFAULT_INPUT = "data/gold/train/sft/JAWS/DE/consolidated_gold_v2_qwen_expansion_sft_samples.jsonl"
DEFAULT_CHUNKS_ROOT = "data/derived/chunks/JAWS/DE"
DEFAULT_REPORT_OUTPUT = "data/derived/teacher_outputs/JAWS/DE/qwen_troubleshooting_cleanup_wave1_report.json"
DEFAULT_PACKET_OUTPUT = "data/derived/teacher_outputs/JAWS/DE/qwen_troubleshooting_cleanup_wave1_review_packet.json"
DEFAULT_IDS_OUTPUT = "data/derived/teacher_outputs/JAWS/DE/qwen_troubleshooting_cleanup_wave1_candidate_ids.txt"

GENERIC_PREFIX = "die dokumentation empfiehlt fuer diesen fall:"
ACTION_RE = re.compile(
    r"(?i)\b(druecken|drücken|waehlen|wählen|oeffnen|öffnen|aktivieren|deaktivieren|pruefen|prüfen|"
    r"stellen sie sicher|wechseln|konfigurieren|verwenden|geben sie|schalten sie|bewegen sie|"
    r"gehen sie|markieren|speichern)\b"
)
ARTIFACT_RE = re.compile(r"(?i)verwenden sie dazu \*\*hinweis:|\.\.\.|…")


def parse_args() -> Any:
    parser = make_parser("Report likely weak troubleshooting rows in the consolidated Qwen gold set.")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--chunks-root", default=DEFAULT_CHUNKS_ROOT)
    parser.add_argument("--report-output", default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--packet-output", default=DEFAULT_PACKET_OUTPUT)
    parser.add_argument("--ids-output", default=DEFAULT_IDS_OUTPUT)
    parser.add_argument("--min-score", type=int, default=4)
    parser.add_argument("--top-n", type=int, default=40)
    parser.add_argument("--review-limit", type=int, default=72)
    return parser.parse_args()


def load_jsonl_with_line_numbers(path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        rows.append((line_no, json.loads(line)))
    return rows


def first_message_content(row: dict[str, Any], role: str) -> str:
    for message in row.get("messages", []):
        if message.get("role") == role:
            return str(message.get("content", ""))
    return ""


def cleanup_reasons(row: dict[str, Any], chunk: dict[str, Any] | None) -> tuple[int, list[str]]:
    assistant = first_message_content(row, "assistant")
    score = 0
    reasons: list[str] = []

    chunk_type = chunk.get("chunk_type") if chunk else None
    if chunk_type == "concept":
        score += 3
        reasons.append("chunk_type_concept")
    elif chunk_type == "reference":
        score += 3
        reasons.append("chunk_type_reference")

    if assistant.lower().startswith(GENERIC_PREFIX):
        score += 1
        reasons.append("generic_troubleshooting_prefix")

    if not ACTION_RE.search(assistant):
        score += 2
        reasons.append("low_actionability")

    if len(assistant) < 180:
        score += 1
        reasons.append("short_answer")

    if ARTIFACT_RE.search(assistant):
        score += 2
        reasons.append("artifact_hint")

    if chunk and "|" in str(chunk.get("content", "")):
        score += 1
        reasons.append("tabular_or_listing_source")

    return score, reasons


def recommendation_for(chunk_type: str | None, reasons: list[str]) -> str:
    if "artifact_hint" in reasons:
        return "drop_from_training"
    if chunk_type in {"concept", "reference"}:
        return "relabel_to_faq_direct_answer"
    if "generic_troubleshooting_prefix" in reasons and "low_actionability" in reasons:
        return "drop_from_training"
    return "manual_review"


def build_entry(line_no: int, row: dict[str, Any], chunk: dict[str, Any] | None, cleanup_score: int, reasons: list[str]) -> dict[str, Any]:
    source_records = row.get("provenance", {}).get("source_records") or row.get("meta", {}).get("provenance", {}).get("source_records", [])
    source_record = source_records[0] if source_records else {}
    chunk_type = chunk.get("chunk_type") if chunk else None
    return {
        "id": row.get("id"),
        "line_number": line_no,
        "cleanup_score": cleanup_score,
        "cleanup_recommendation": recommendation_for(chunk_type, reasons),
        "cleanup_reasons": reasons,
        "task_type": row.get("task_type"),
        "doc_id": source_record.get("doc_id"),
        "chunk_id": source_record.get("chunk_id"),
        "section_id": source_record.get("section_id"),
        "section_title": source_record.get("section_title"),
        "chunk_type": chunk_type,
        "normalized_path": source_record.get("normalized_path"),
        "source_spans": source_record.get("source_spans"),
        "user_preview": first_message_content(row, "user")[:220],
        "assistant_preview": first_message_content(row, "assistant")[:420],
    }


def main() -> None:
    args = parse_args()
    if args.min_score <= 0:
        raise SystemExit("--min-score must be > 0")
    if args.top_n <= 0:
        raise SystemExit("--top-n must be > 0")
    if args.review_limit <= 0:
        raise SystemExit("--review-limit must be > 0")

    input_path = Path(args.input)
    rows = load_jsonl_with_line_numbers(input_path)
    chunk_index = {chunk["chunk_id"]: chunk for chunk in load_chunks(Path(args.chunks_root))}

    troubleshooting_rows = [(line_no, row) for line_no, row in rows if row.get("task_type") == "troubleshooting"]
    chunk_type_counter: Counter[str] = Counter()
    flagged_entries: list[dict[str, Any]] = []
    flagged_reason_counter: Counter[str] = Counter()
    flagged_doc_counter: Counter[str] = Counter()
    flagged_recommendation_counter: Counter[str] = Counter()
    flagged_score_counter: Counter[int] = Counter()

    for line_no, row in troubleshooting_rows:
        source_chunk_ids = row.get("source_chunk_ids") or row.get("meta", {}).get("source_chunk_ids") or []
        chunk = chunk_index.get(source_chunk_ids[0]) if source_chunk_ids else None
        chunk_type = chunk.get("chunk_type", "unknown") if chunk else "unknown"
        chunk_type_counter[chunk_type] += 1

        cleanup_score, reasons = cleanup_reasons(row, chunk)
        if cleanup_score < args.min_score:
            continue
        entry = build_entry(line_no, row, chunk, cleanup_score, reasons)
        flagged_entries.append(entry)
        flagged_reason_counter.update(reasons)
        flagged_doc_counter.update([entry["doc_id"] or "unknown"])
        flagged_recommendation_counter.update([entry["cleanup_recommendation"]])
        flagged_score_counter.update([cleanup_score])

    flagged_entries.sort(
        key=lambda item: (
            -int(item["cleanup_score"]),
            str(item["cleanup_recommendation"]),
            str(item["id"]),
        )
    )

    review_entries = flagged_entries[: args.review_limit]

    ids_output = Path(args.ids_output)
    ids_output.parent.mkdir(parents=True, exist_ok=True)
    ids_output.write_text(
        "\n".join(str(entry["id"]) for entry in review_entries) + ("\n" if review_entries else ""),
        encoding="utf-8",
    )

    report = {
        "report_name": "qwen_troubleshooting_cleanup_wave1",
        "input_path": args.input,
        "chunks_root": args.chunks_root,
        "task_type": "troubleshooting",
        "min_cleanup_score": args.min_score,
        "total_rows": len(rows),
        "troubleshooting_rows": len(troubleshooting_rows),
        "troubleshooting_rows_by_chunk_type": dict(chunk_type_counter),
        "flagged_candidates": len(flagged_entries),
        "review_wave_candidates": len(review_entries),
        "flagged_by_recommendation": dict(flagged_recommendation_counter),
        "flagged_by_reason": dict(flagged_reason_counter),
        "flagged_by_doc": dict(flagged_doc_counter),
        "flagged_by_score": dict(sorted(flagged_score_counter.items())),
        "top_candidates": flagged_entries[: args.top_n],
        "ids_output": args.ids_output,
        "review_packet_output": args.packet_output,
    }
    packet = {
        "packet_name": "qwen_troubleshooting_cleanup_wave1_review",
        "input_path": args.input,
        "rows": len(review_entries),
        "rows_by_recommendation": dict(Counter(entry["cleanup_recommendation"] for entry in review_entries)),
        "rows_by_doc": dict(Counter((entry["doc_id"] or "unknown") for entry in review_entries)),
        "reason_counts": dict(Counter(reason for entry in review_entries for reason in entry["cleanup_reasons"])),
        "entries": review_entries,
    }

    write_json(Path(args.report_output), report)
    write_json(Path(args.packet_output), packet)
    print(f"Wrote troubleshooting cleanup report -> {args.report_output}")
    print(f"Wrote troubleshooting cleanup review packet -> {args.packet_output}")
    print(f"Wrote troubleshooting cleanup ids -> {args.ids_output}")


if __name__ == "__main__":
    main()

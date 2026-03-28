from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json


def preview(text: str, limit: int = 220) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def extract_user_message(candidate: dict) -> str:
    if "messages" in candidate:
        for message in candidate["messages"]:
            if message.get("role") == "user":
                return str(message.get("content", ""))
    return str(candidate.get("prompt", ""))


def extract_assistant_message(row: dict) -> str:
    candidate = row["candidate"]
    if row["record_type"] == "sft_sample":
        for message in candidate.get("messages", []):
            if message.get("role") == "assistant":
                return str(message.get("content", ""))
        return ""
    return str(candidate.get("reference_answer", ""))


def parse_args() -> Any:
    parser = make_parser("Build a compact review packet JSON for teacher outputs.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--packet-name", required=True)
    parser.add_argument("--max-entries", type=int, default=80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.max_entries <= 0:
        raise SystemExit("--max-entries must be > 0")

    rows = read_jsonl(Path(args.input))
    rows.sort(
        key=lambda row: (
            row["target_split"],
            row["task_type"],
            row["source_doc_ids"][0],
            -int(row.get("quality_score", 0) or 0),
            row["output_id"],
        )
    )

    entries: list[dict[str, Any]] = []
    for row in rows[: args.max_entries]:
        source_record = row["provenance"]["source_records"][0]
        entries.append(
            {
                "output_id": row["output_id"],
                "target_split": row["target_split"],
                "task_type": row["task_type"],
                "record_type": row["record_type"],
                "doc_id": row["source_doc_ids"][0],
                "chunk_id": row["source_chunk_ids"][0],
                "quality_score": row.get("quality_score"),
                "review_status": row["review_status"],
                "section_title": source_record.get("section_title"),
                "normalized_path": source_record.get("normalized_path"),
                "source_spans": source_record.get("source_spans", []),
                "user_preview": preview(extract_user_message(row["candidate"])),
                "assistant_preview": preview(extract_assistant_message(row)),
            }
        )

    report = {
        "packet_name": args.packet_name,
        "input_path": args.input.replace("\\", "/"),
        "rows": len(rows),
        "rows_by_split": dict(Counter(row["target_split"] for row in rows)),
        "rows_by_task_type": dict(Counter(row["task_type"] for row in rows)),
        "rows_by_doc": dict(Counter(row["source_doc_ids"][0] for row in rows)),
        "quality_score_range": {
            "min": min((int(row.get("quality_score", 0) or 0) for row in rows), default=0),
            "max": max((int(row.get("quality_score", 0) or 0) for row in rows), default=0),
        },
        "entries": entries,
    }
    write_json(Path(args.output), report)
    print(f"Wrote review packet -> {args.output}")


if __name__ == "__main__":
    main()

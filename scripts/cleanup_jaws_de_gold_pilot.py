from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json, write_jsonl


RUN_PRIORITY = {
    "jaws_de_wave2_codex_gpt54_run_v1": 60,
    "jaws_de_wave1_codex_gpt54_run_v2": 50,
    "jaws_de_wave1_codex_gpt54_run_v1": 45,
}
PROVIDER_PRIORITY = {"codex": 3, "openai": 2, "local": 1, None: 0}
MODEL_PRIORITY = {"gpt-5.4": 3, "teacher-stub-no-llm": 1, "template-seed-no-llm": 0}
STUB_MARKERS = ("stub", "fixture")
WEAK_TROUBLESHOOTING_IDS = {
    "jaws_de_teacher_wave_v2_scaleup::train::troubleshooting::0182__candidate": "generic_ui_toggle_without_diagnostic_value",
    "jaws_de_teacher_wave_v2_scaleup::train::troubleshooting::0186__candidate": "minimal_dependency_note_without_actionable_diagnosis",
    "jaws_de_teacher_wave_v2_scaleup::train::troubleshooting::0195__candidate": "generic_dialog_button_instruction",
    "jaws_de_teacher_wave_v2_scaleup::train::troubleshooting::0208__candidate": "generic_dialog_button_instruction",
    "jaws_de_teacher_wave_v2_scaleup::train::troubleshooting::0214__candidate": "generic_ui_toggle_without_diagnostic_value",
    "jaws_de_teacher_wave_v2_topoff::train::troubleshooting::0002__candidate": "parameter_field_description_without_troubleshooting_depth",
    "jaws_de_teacher_wave_v2_topoff::train::troubleshooting::0006__candidate": "generic_dialog_button_instruction",
    "jaws_de_teacher_wave_v2_topoff::train::troubleshooting::0007__candidate": "generic_dialog_button_instruction",
    "jaws_de_teacher_wave_v2_topoff::train::troubleshooting::0012__candidate": "generic_dialog_button_instruction",
    "jaws_de_teacher_wave_v2_topoff::train::troubleshooting::0013__candidate": "parameter_field_description_without_troubleshooting_depth",
}


def parse_args() -> Any:
    parser = make_parser("Create a cleaned JAWS-DE pilot gold dataset from consolidated gold v1.")
    parser.add_argument("--train-input", required=True)
    parser.add_argument("--eval-input", required=True)
    parser.add_argument("--train-output", required=True)
    parser.add_argument("--eval-output", required=True)
    parser.add_argument("--report-output", required=True)
    return parser.parse_args()


def _normalize_text(value: str) -> str:
    return " ".join(value.split()).casefold()


def _message_text(row: dict, role: str) -> str:
    return "\n".join(
        str(message.get("content", "")).strip()
        for message in row.get("messages", [])
        if message.get("role") == role
    ).strip()


def _pair_key(row: dict) -> tuple[str, str]:
    if "messages" in row:
        return (_normalize_text(_message_text(row, "user")), _normalize_text(_message_text(row, "assistant")))
    return (_normalize_text(str(row.get("prompt", ""))), _normalize_text(str(row.get("reference_answer", ""))))


def _row_rank(row: dict) -> tuple[int, int, int, str]:
    return (
        MODEL_PRIORITY.get(row.get("teacher_model"), 0),
        PROVIDER_PRIORITY.get(row.get("teacher_provider"), 0),
        RUN_PRIORITY.get(row.get("teacher_run_id"), 0),
        row.get("id") or row.get("eval_id") or "",
    )


def _preview(value: str, limit: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1] + "…"


def _is_stub(row: dict) -> bool:
    candidate_values = [
        row.get("teacher_model"),
        row.get("generation_mode"),
        row.get("teacher_run_id"),
        (row.get("promoted_from") or {}).get("teacher_model"),
        (row.get("promoted_from") or {}).get("teacher_run_id"),
    ]
    lowered = " ".join(str(value or "").casefold() for value in candidate_values)
    return any(marker in lowered for marker in STUB_MARKERS)


def _row_id(row: dict) -> str:
    return str(row.get("id") or row.get("eval_id"))


def _task_name(row: dict, split: str) -> str:
    return str(row.get("task_type") if split == "train" else row.get("case_type"))


def _source_record(row: dict) -> dict:
    return dict((row.get("provenance") or {}).get("source_records", [{}])[0])


def _removal_entry(row: dict, split: str, reason: str, rule_type: str, kept_id: str | None = None) -> dict:
    source_record = _source_record(row)
    return {
        "split": split,
        "id": _row_id(row),
        "task_type": _task_name(row, split),
        "reason": reason,
        "rule_type": rule_type,
        "kept_id": kept_id,
        "teacher_model": row.get("teacher_model"),
        "teacher_run_id": row.get("teacher_run_id"),
        "source_doc_ids": row.get("source_doc_ids", []),
        "source_chunk_ids": row.get("source_chunk_ids", []),
        "source_section_title": source_record.get("section_title"),
        "source_spans": source_record.get("source_spans", []),
        "user_preview": _preview(_message_text(row, "user") or str(row.get("prompt", ""))),
        "assistant_preview": _preview(_message_text(row, "assistant") or str(row.get("reference_answer", ""))),
    }


def _validate_rows(rows: list[dict], split: str) -> None:
    ids: set[str] = set()
    for row in rows:
        row_id = _row_id(row)
        if not row_id:
            raise ValueError(f"Missing id in {split} rows")
        if row_id in ids:
            raise ValueError(f"Duplicate id {row_id} in {split} rows")
        ids.add(row_id)
        if row.get("split") != split:
            raise ValueError(f"{row_id} has split {row.get('split')} instead of {split}")
        if row.get("review_status") != "promoted":
            raise ValueError(f"{row_id} is not promoted")
        source_chunks = row.get("source_chunk_ids")
        if not isinstance(source_chunks, list) or not source_chunks:
            raise ValueError(f"{row_id} is missing source_chunk_ids")
        if "messages" in row:
            messages = row.get("messages")
            if not isinstance(messages, list) or len(messages) < 3:
                raise ValueError(f"{row_id} has invalid messages")
            if messages[-1].get("role") != "assistant":
                raise ValueError(f"{row_id} does not end with assistant")
            if not str(messages[-1].get("content", "")).strip():
                raise ValueError(f"{row_id} has empty assistant content")
        provenance = row.get("provenance") or {}
        source_records = provenance.get("source_records")
        if not isinstance(source_records, list) or not source_records:
            raise ValueError(f"{row_id} is missing provenance.source_records")
        if not provenance.get("transform_pipeline_version"):
            raise ValueError(f"{row_id} is missing provenance.transform_pipeline_version")


def _task_distribution(rows: list[dict], split: str) -> dict[str, int]:
    key = "task_type" if split == "train" else "case_type"
    return dict(sorted(Counter(str(row.get(key)) for row in rows).items()))


def _dedupe_rows(rows: list[dict], split: str, removals: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[_pair_key(row)].append(row)

    kept_rows: list[dict] = []
    for _, candidates in sorted(grouped.items(), key=lambda item: max(_row_rank(row) for row in item[1]), reverse=True):
        winner = max(candidates, key=_row_rank)
        kept_rows.append(winner)
        if len(candidates) == 1:
            continue
        for candidate in sorted(candidates, key=_row_rank):
            if candidate is winner:
                continue
            removals.append(
                _removal_entry(
                    candidate,
                    split=split,
                    reason="exact_or_near_exact_user_assistant_duplicate",
                    rule_type="serial_pattern_dedup",
                    kept_id=_row_id(winner),
                )
            )
    return sorted(kept_rows, key=_row_id)


def _filter_rows(rows: list[dict], split: str, removals: list[dict]) -> list[dict]:
    kept: list[dict] = []
    for row in rows:
        row_id = _row_id(row)
        if _is_stub(row):
            removals.append(_removal_entry(row, split=split, reason="stub_or_fixture_teacher_source", rule_type="stub_filter"))
            continue
        if split == "train" and row_id in WEAK_TROUBLESHOOTING_IDS:
            removals.append(
                _removal_entry(
                    row,
                    split=split,
                    reason=WEAK_TROUBLESHOOTING_IDS[row_id],
                    rule_type="weak_troubleshooting_filter",
                )
            )
            continue
        kept.append(row)
    return kept


def _split_chunk_overlap(train_rows: list[dict], eval_rows: list[dict]) -> list[str]:
    train_chunks = {chunk_id for row in train_rows for chunk_id in row.get("source_chunk_ids", [])}
    eval_chunks = {chunk_id for row in eval_rows for chunk_id in row.get("source_chunk_ids", [])}
    return sorted(train_chunks & eval_chunks)


def main() -> None:
    args = parse_args()
    train_input = Path(args.train_input)
    eval_input = Path(args.eval_input)
    train_rows = read_jsonl(train_input)
    eval_rows = read_jsonl(eval_input)

    _validate_rows(train_rows, "train")
    _validate_rows(eval_rows, "eval")

    removals: list[dict] = []
    filtered_train = _filter_rows(train_rows, "train", removals)
    filtered_eval = _filter_rows(eval_rows, "eval", removals)
    cleaned_train = _dedupe_rows(filtered_train, "train", removals)
    cleaned_eval = _dedupe_rows(filtered_eval, "eval", removals)

    overlap = _split_chunk_overlap(cleaned_train, cleaned_eval)
    if overlap:
        raise ValueError(f"Train/eval chunk overlap remains after cleanup: {overlap}")
    _validate_rows(cleaned_train, "train")
    _validate_rows(cleaned_eval, "eval")

    sorted_removals = sorted(
        removals,
        key=lambda row: (row["split"], row["rule_type"], row["reason"], row["id"]),
    )
    removals_by_rule_type = Counter(row["rule_type"] for row in sorted_removals)
    removals_by_split = Counter(row["split"] for row in sorted_removals)
    removal_ids = {row["id"] for row in sorted_removals}

    duplicate_group_sizes = Counter()
    for rows, split in ((train_rows, "train"), (eval_rows, "eval")):
        grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for row in rows:
            if _row_id(row) in removal_ids:
                continue
            grouped[_pair_key(row)].append(row)
        for candidates in grouped.values():
            if len(candidates) > 1:
                duplicate_group_sizes[split] += len(candidates) - 1

    report = {
        "cleanup_version": "jaws_de_gold_pilot_cleanup_v1",
        "source_train_path": train_input.as_posix(),
        "source_eval_path": eval_input.as_posix(),
        "output_train_path": Path(args.train_output).as_posix(),
        "output_eval_path": Path(args.eval_output).as_posix(),
        "removal_rules": {
            "stub_filter": "Exclude rows whose teacher/model generation metadata contains stub or fixture markers.",
            "serial_pattern_dedup": "Keep a single deterministic winner for each normalized user+assistant pair; drop the rest.",
            "weak_troubleshooting_filter": "Exclude a short manually reviewed list of troubleshooting rows that are generic UI/button descriptions or otherwise diagnostically weak.",
        },
        "manual_weak_troubleshooting_ids": WEAK_TROUBLESHOOTING_IDS,
        "before": {
            "train_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "train_by_task_type": _task_distribution(train_rows, "train"),
            "eval_by_case_type": _task_distribution(eval_rows, "eval"),
        },
        "after": {
            "train_rows": len(cleaned_train),
            "eval_rows": len(cleaned_eval),
            "train_by_task_type": _task_distribution(cleaned_train, "train"),
            "eval_by_case_type": _task_distribution(cleaned_eval, "eval"),
        },
        "removals": {
            "total": len(removals),
            "by_rule_type": dict(sorted(removals_by_rule_type.items())),
            "by_split": dict(sorted(removals_by_split.items())),
            "stub_removed": sum(1 for row in sorted_removals if row["rule_type"] == "stub_filter"),
            "serial_pattern_removed": sum(1 for row in sorted_removals if row["rule_type"] == "serial_pattern_dedup"),
            "weak_troubleshooting_removed": sum(1 for row in sorted_removals if row["rule_type"] == "weak_troubleshooting_filter"),
        },
        "validation": {
            "remaining_stub_rows": sum(1 for row in cleaned_train + cleaned_eval if _is_stub(row)),
            "remaining_exact_duplicate_rows": dict(sorted(duplicate_group_sizes.items())),
            "split_chunk_overlap": overlap,
            "messages_structure_checked": True,
            "provenance_checked": True,
        },
        "removed_rows": sorted_removals,
        "removal_examples": sorted_removals[:40],
    }

    write_jsonl(Path(args.train_output), cleaned_train)
    write_jsonl(Path(args.eval_output), cleaned_eval)
    write_json(Path(args.report_output), report)

    print(f"Wrote cleaned train -> {args.train_output}")
    print(f"Wrote cleaned eval -> {args.eval_output}")
    print(f"Wrote cleanup report -> {args.report_output}")


if __name__ == "__main__":
    main()

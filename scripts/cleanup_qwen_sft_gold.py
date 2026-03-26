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
ASSISTANT_ARTIFACT_MARKERS = (
    "Verwenden Sie dazu **Hinweis:**",
    "Verwenden Sie dazu **Tipp:**",
    "Die Dokumentation empfiehlt fuer diesen Fall: Hinweis:",
    "Die Dokumentation empfiehlt fuer diesen Fall: Tipp:",
)
PROMPT_REPEAT_LIMITS = {
    "clarification": 3,
    "uncertainty_escalation": 2,
}


def parse_args() -> Any:
    parser = make_parser("Create a cleaned Qwen-SFT gold dataset from consolidated promoted gold files.")
    parser.add_argument("--train-input", required=True)
    parser.add_argument("--eval-input", required=True)
    parser.add_argument("--train-output", required=True)
    parser.add_argument("--eval-output", required=True)
    parser.add_argument("--report-output", required=True)
    return parser.parse_args()


def _row_id(row: dict) -> str:
    return str(row.get("id") or row.get("eval_id") or "")


def _normalize_text(value: str) -> str:
    return " ".join(str(value).split()).casefold()


def _message_text(row: dict, role: str) -> str:
    return "\n".join(
        str(message.get("content", "")).strip()
        for message in row.get("messages", [])
        if message.get("role") == role
    ).strip()


def _prompt_text(row: dict) -> str:
    if "messages" in row:
        return _message_text(row, "user")
    return str(row.get("prompt", "")).strip()


def _assistant_text(row: dict) -> str:
    if "messages" in row:
        return _message_text(row, "assistant")
    return str(row.get("reference_answer", "")).strip()


def _task_name(row: dict, split: str) -> str:
    return str(row.get("task_type") if split == "train" else row.get("case_type"))


def _preview(value: str, limit: int = 180) -> str:
    normalized = " ".join(str(value).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _row_rank(row: dict) -> tuple[int, int, int, int, str]:
    assistant_len = len(_assistant_text(row))
    return (
        MODEL_PRIORITY.get(row.get("teacher_model"), 0),
        PROVIDER_PRIORITY.get(row.get("teacher_provider"), 0),
        RUN_PRIORITY.get(row.get("teacher_run_id"), 0),
        assistant_len,
        _row_id(row),
    )


def _pair_key(row: dict) -> tuple[str, str]:
    return (_normalize_text(_prompt_text(row)), _normalize_text(_assistant_text(row)))


def _prompt_key(row: dict, split: str) -> tuple[str, str]:
    return (_task_name(row, split), _normalize_text(_prompt_text(row)))


def _source_record(row: dict) -> dict:
    source_records = (row.get("provenance") or {}).get("source_records") or []
    return dict(source_records[0]) if source_records else {}


def _artifact_markers(row: dict) -> list[str]:
    assistant = _assistant_text(row)
    markers = [marker for marker in ASSISTANT_ARTIFACT_MARKERS if marker in assistant]
    if assistant.endswith("…") or assistant.endswith("..."):
        markers.append("terminal_ellipsis")
    return markers


def _is_stub(row: dict) -> bool:
    values = [
        row.get("teacher_model"),
        row.get("generation_mode"),
        row.get("teacher_run_id"),
        row.get("teacher_provider"),
        (row.get("promoted_from") or {}).get("teacher_model"),
        (row.get("promoted_from") or {}).get("teacher_run_id"),
    ]
    lowered = " ".join(str(value or "").casefold() for value in values)
    return any(marker in lowered for marker in STUB_MARKERS)


def _removal_entry(row: dict, split: str, reason: str, rule_type: str, kept_id: str | None = None) -> dict:
    source_record = _source_record(row)
    return {
        "split": split,
        "id": _row_id(row),
        "task_name": _task_name(row, split),
        "rule_type": rule_type,
        "reason": reason,
        "kept_id": kept_id,
        "teacher_model": row.get("teacher_model"),
        "teacher_run_id": row.get("teacher_run_id"),
        "source_doc_ids": row.get("source_doc_ids", []),
        "source_chunk_ids": row.get("source_chunk_ids", []),
        "source_section_title": source_record.get("section_title"),
        "source_spans": source_record.get("source_spans", []),
        "prompt_preview": _preview(_prompt_text(row)),
        "assistant_preview": _preview(_assistant_text(row)),
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
        if not row.get("source_chunk_ids"):
            raise ValueError(f"{row_id} is missing source_chunk_ids")
        if split == "train":
            if "messages" not in row or len(row["messages"]) < 3:
                raise ValueError(f"{row_id} has invalid messages")
            if row["messages"][-1].get("role") != "assistant":
                raise ValueError(f"{row_id} does not end with assistant")
            if not _assistant_text(row):
                raise ValueError(f"{row_id} has empty assistant content")
        else:
            if not str(row.get("prompt", "")).strip():
                raise ValueError(f"{row_id} has empty prompt")
            if not str(row.get("reference_answer", "")).strip():
                raise ValueError(f"{row_id} has empty reference_answer")
        provenance = row.get("provenance") or {}
        source_records = provenance.get("source_records")
        if not isinstance(source_records, list) or not source_records:
            raise ValueError(f"{row_id} is missing provenance.source_records")
        if not provenance.get("transform_pipeline_version"):
            raise ValueError(f"{row_id} is missing provenance.transform_pipeline_version")


def _task_distribution(rows: list[dict], split: str) -> dict[str, int]:
    return dict(sorted(Counter(_task_name(row, split) for row in rows).items()))


def _filter_rows(rows: list[dict], split: str, removals: list[dict]) -> list[dict]:
    kept: list[dict] = []
    for row in rows:
        if _is_stub(row):
            removals.append(
                _removal_entry(
                    row,
                    split=split,
                    reason="stub_or_fixture_teacher_source",
                    rule_type="stub_filter",
                )
            )
            continue
        markers = _artifact_markers(row)
        if markers:
            removals.append(
                _removal_entry(
                    row,
                    split=split,
                    reason="assistant_template_artifact:" + "|".join(markers),
                    rule_type="artifact_filter",
                )
            )
            continue
        kept.append(row)
    return kept


def _dedupe_pairs(rows: list[dict], split: str, removals: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[_pair_key(row)].append(row)

    kept: list[dict] = []
    for candidates in grouped.values():
        ordered = sorted(candidates, key=_row_rank, reverse=True)
        winner = ordered[0]
        kept.append(winner)
        for candidate in ordered[1:]:
            removals.append(
                _removal_entry(
                    candidate,
                    split=split,
                    reason="exact_or_near_exact_user_assistant_duplicate",
                    rule_type="pair_dedup",
                    kept_id=_row_id(winner),
                )
            )
    return sorted(kept, key=_row_id)


def _cap_repeated_prompts(rows: list[dict], split: str, removals: list[dict]) -> list[dict]:
    if split != "train":
        return sorted(rows, key=_row_id)

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[_prompt_key(row, split)].append(row)

    kept: list[dict] = []
    for (task_name, _), candidates in sorted(grouped.items(), key=lambda item: item[0]):
        limit = PROMPT_REPEAT_LIMITS.get(task_name)
        ordered = sorted(candidates, key=_row_rank, reverse=True)
        if not limit or len(ordered) <= limit:
            kept.extend(ordered)
            continue
        winners = ordered[:limit]
        kept.extend(winners)
        for candidate in ordered[limit:]:
            removals.append(
                _removal_entry(
                    candidate,
                    split=split,
                    reason=f"normalized_prompt_repeat_cap_exceeded:{task_name}:{limit}",
                    rule_type="prompt_repeat_cap",
                    kept_id=_row_id(winners[-1]),
                )
            )
    return sorted(kept, key=_row_id)


def _split_chunk_overlap(train_rows: list[dict], eval_rows: list[dict]) -> list[str]:
    train_chunks = {chunk for row in train_rows for chunk in row.get("source_chunk_ids", [])}
    eval_chunks = {chunk for row in eval_rows for chunk in row.get("source_chunk_ids", [])}
    return sorted(train_chunks & eval_chunks)


def main() -> None:
    args = parse_args()

    train_rows = read_jsonl(Path(args.train_input))
    eval_rows = read_jsonl(Path(args.eval_input))
    _validate_rows(train_rows, "train")
    _validate_rows(eval_rows, "eval")

    removals: list[dict] = []

    filtered_train = _filter_rows(train_rows, "train", removals)
    filtered_eval = _filter_rows(eval_rows, "eval", removals)
    deduped_train = _dedupe_pairs(filtered_train, "train", removals)
    deduped_eval = _dedupe_pairs(filtered_eval, "eval", removals)
    cleaned_train = _cap_repeated_prompts(deduped_train, "train", removals)
    cleaned_eval = _cap_repeated_prompts(deduped_eval, "eval", removals)

    overlap = _split_chunk_overlap(cleaned_train, cleaned_eval)
    if overlap:
        raise ValueError(f"Train/eval chunk overlap remains after cleanup: {overlap}")

    _validate_rows(cleaned_train, "train")
    _validate_rows(cleaned_eval, "eval")

    sorted_removals = sorted(removals, key=lambda item: (item["split"], item["rule_type"], item["reason"], item["id"]))

    report = {
        "cleanup_version": "qwen_sft_gold_cleanup_v1",
        "source_train_path": Path(args.train_input).as_posix(),
        "source_eval_path": Path(args.eval_input).as_posix(),
        "output_train_path": Path(args.train_output).as_posix(),
        "output_eval_path": Path(args.eval_output).as_posix(),
        "rules": {
            "stub_filter": "Exclude rows whose teacher metadata indicates stub or fixture generation.",
            "artifact_filter": "Exclude rows with assistant-side template artifacts such as trailing Hinweis/Tipp placeholders.",
            "pair_dedup": "Keep one deterministic winner per normalized prompt+assistant pair.",
            "prompt_repeat_cap": {
                "clarification": PROMPT_REPEAT_LIMITS["clarification"],
                "uncertainty_escalation": PROMPT_REPEAT_LIMITS["uncertainty_escalation"],
            },
        },
        "before": {
            "train_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "train_task_distribution": _task_distribution(train_rows, "train"),
            "eval_task_distribution": _task_distribution(eval_rows, "eval"),
        },
        "after": {
            "train_rows": len(cleaned_train),
            "eval_rows": len(cleaned_eval),
            "train_task_distribution": _task_distribution(cleaned_train, "train"),
            "eval_task_distribution": _task_distribution(cleaned_eval, "eval"),
        },
        "removals": {
            "total": len(sorted_removals),
            "by_rule_type": dict(sorted(Counter(item["rule_type"] for item in sorted_removals).items())),
            "by_split": dict(sorted(Counter(item["split"] for item in sorted_removals).items())),
        },
        "validation": {
            "remaining_stub_rows": sum(1 for row in cleaned_train + cleaned_eval if _is_stub(row)),
            "remaining_artifact_rows": sum(1 for row in cleaned_train + cleaned_eval if _artifact_markers(row)),
            "split_chunk_overlap": overlap,
        },
        "removed_rows": sorted_removals,
        "removal_examples": sorted_removals[:60],
    }

    write_jsonl(Path(args.train_output), cleaned_train)
    write_jsonl(Path(args.eval_output), cleaned_eval)
    write_json(Path(args.report_output), report)

    print(f"Wrote cleaned train -> {args.train_output}")
    print(f"Wrote cleaned eval -> {args.eval_output}")
    print(f"Wrote cleanup report -> {args.report_output}")


if __name__ == "__main__":
    main()

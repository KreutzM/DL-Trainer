from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json, write_jsonl


DEFAULT_INPUTS = [
    "data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_codex_gpt54_reviewed_outputs.jsonl",
    "data/derived/teacher_outputs/JAWS/DE/wave2_topoff_codex_gpt54_reviewed_outputs.jsonl",
]
DEFAULT_EXCLUDE_JSONL = [
    "data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl",
    "data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl",
]
DEFAULT_TRAIN_TARGETS = {
    "clarification": 20,
    "faq_direct_answer": 28,
    "step_by_step": 16,
    "troubleshooting": 10,
    "uncertainty_escalation": 8,
}
DEFAULT_EVAL_TARGETS = {
    "clarification": 4,
    "faq_direct_answer": 6,
    "step_by_step": 4,
    "troubleshooting": 4,
    "uncertainty_escalation": 4,
}
TASK_ORDER = [
    "clarification",
    "faq_direct_answer",
    "step_by_step",
    "troubleshooting",
    "uncertainty_escalation",
]
FOCUS_DOC_IDS = {
    "jaws_de_braille",
    "jaws_de_hilfe_kernfunktionen",
    "jaws_de_settingscenter",
    "jaws_de_tutorial_basics",
}
ELLIPSIS_SUFFIXES = ("...", "\u2026")


def parse_target_args(values: list[str], defaults: dict[str, int]) -> dict[str, int]:
    targets = dict(defaults)
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid target override '{value}', expected task=count")
        task_type, count_text = value.split("=", 1)
        if task_type not in targets:
            raise SystemExit(f"Unknown task type in override: {task_type}")
        try:
            count = int(count_text)
        except ValueError as exc:
            raise SystemExit(f"Invalid count in override '{value}'") from exc
        if count < 0:
            raise SystemExit(f"Target count must be non-negative: {value}")
        targets[task_type] = count
    return targets


def load_excluded_chunk_ids(paths: list[str]) -> set[str]:
    chunk_ids: set[str] = set()
    for path_str in paths:
        for row in read_jsonl(Path(path_str)):
            chunk_ids.update(row.get("source_chunk_ids", []))
    return chunk_ids


def candidate_text(row: dict) -> str:
    candidate = row.get("candidate", {})
    if row.get("record_type") == "sft_sample":
        messages = candidate.get("messages", [])
        if messages:
            return str(messages[-1].get("content", "")).strip()
    return str(candidate.get("reference_answer", "")).strip()


def prompt_text(row: dict) -> str:
    candidate = row.get("candidate", {})
    if row.get("record_type") == "sft_sample":
        messages = candidate.get("messages", [])
        if len(messages) >= 2:
            return str(messages[1].get("content", "")).strip()
    return str(candidate.get("prompt", "")).strip()


def reject_reason(row: dict) -> str | None:
    if row.get("review_status") != "human_reviewed" or not row.get("approved_by"):
        return "not_human_reviewed"
    if row.get("promoted_to"):
        return "already_promoted"
    task_type = row.get("task_type")
    if task_type not in TASK_ORDER:
        return "unsupported_task_type"
    doc_ids = row.get("source_doc_ids", [])
    if not doc_ids or doc_ids[0] not in FOCUS_DOC_IDS:
        return "outside_focus_docs"
    text = candidate_text(row)
    if not text:
        return "empty_answer"
    if text.rstrip().endswith(ELLIPSIS_SUFFIXES):
        return "terminal_ellipsis"
    if task_type == "clarification":
        if text.count("?") != 1:
            return "clarification_question_count"
        if not text.endswith("?"):
            return "clarification_missing_terminal_question_mark"
    if task_type == "step_by_step" and not text.lstrip().startswith("1."):
        return "step_by_step_missing_enumeration"
    return None


def round_robin_select(
    grouped: dict[str, list[dict]],
    target: int,
    used_chunks: set[str],
    used_pairs: set[tuple[str, str]],
) -> list[dict]:
    selected: list[dict] = []
    ordered_docs = sorted(grouped)
    for doc_id in ordered_docs:
        grouped[doc_id].sort(
            key=lambda row: (
                -int(row.get("quality_score", 0)),
                row.get("output_id", ""),
            )
        )

    while len(selected) < target:
        progressed = False
        for doc_id in ordered_docs:
            bucket = grouped.get(doc_id, [])
            while bucket:
                row = bucket[0]
                chunk_ids = set(row.get("source_chunk_ids", []))
                pair = (prompt_text(row), candidate_text(row))
                if chunk_ids & used_chunks:
                    bucket.pop(0)
                    continue
                if pair in used_pairs:
                    bucket.pop(0)
                    continue
                selected.append(bucket.pop(0))
                used_chunks.update(chunk_ids)
                used_pairs.add(pair)
                progressed = True
                break
            if len(selected) >= target:
                break
        if not progressed:
            break
    return selected


def parse_args() -> Any:
    parser = make_parser(
        "Select a promotable Qwen data-expansion subset from reviewed Wave2 teacher outputs."
    )
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--exclude-jsonl", action="append", default=[])
    parser.add_argument(
        "--output-jsonl",
        default="data/derived/teacher_outputs/JAWS/DE/qwen_data_expansion_wave1_reviewed_outputs.jsonl",
    )
    parser.add_argument(
        "--output-ids",
        default="data/derived/teacher_outputs/JAWS/DE/qwen_data_expansion_wave1_output_ids.txt",
    )
    parser.add_argument(
        "--report-output",
        default="data/derived/teacher_outputs/JAWS/DE/qwen_data_expansion_wave1_report.json",
    )
    parser.add_argument("--train-target", action="append", default=[])
    parser.add_argument("--eval-target", action="append", default=[])
    parser.add_argument("--min-quality-score", type=int, default=36)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_paths = args.input or list(DEFAULT_INPUTS)
    exclude_paths = args.exclude_jsonl or list(DEFAULT_EXCLUDE_JSONL)
    train_targets = parse_target_args(args.train_target, DEFAULT_TRAIN_TARGETS)
    eval_targets = parse_target_args(args.eval_target, DEFAULT_EVAL_TARGETS)

    excluded_chunk_ids = load_excluded_chunk_ids(exclude_paths)
    rows: list[dict] = []
    for path_str in input_paths:
        rows.extend(read_jsonl(Path(path_str)))

    filtered: dict[str, dict[str, list[dict]]] = {
        "train": defaultdict(list),
        "eval": defaultdict(list),
    }
    rejection_counts = Counter()
    available_by_split_task = {"train": Counter(), "eval": Counter()}
    available_by_split_doc = {"train": Counter(), "eval": Counter()}

    for row in rows:
        reason = reject_reason(row)
        if reason:
            rejection_counts[reason] += 1
            continue
        if int(row.get("quality_score", 0)) < args.min_quality_score:
            rejection_counts["below_min_quality_score"] += 1
            continue

        split = row.get("target_split")
        if split not in {"train", "eval"}:
            rejection_counts["unsupported_split"] += 1
            continue

        source_chunk_ids = set(row.get("source_chunk_ids", []))
        if source_chunk_ids & excluded_chunk_ids:
            rejection_counts["chunk_already_in_gold"] += 1
            continue

        task_type = row["task_type"]
        doc_id = row["source_doc_ids"][0]
        filtered[split][task_type].append(row)
        available_by_split_task[split][task_type] += 1
        available_by_split_doc[split][doc_id] += 1

    used_chunks = set(excluded_chunk_ids)
    used_pairs: set[tuple[str, str]] = set()
    selected_rows: list[dict] = []
    shortages = {"train": {}, "eval": {}}

    for split, targets in (("train", train_targets), ("eval", eval_targets)):
        for task_type in TASK_ORDER:
            grouped: dict[str, list[dict]] = defaultdict(list)
            for row in filtered[split][task_type]:
                grouped[row["source_doc_ids"][0]].append(row)
            chosen = round_robin_select(grouped, targets[task_type], used_chunks, used_pairs)
            selected_rows.extend(chosen)
            shortages[split][task_type] = max(0, targets[task_type] - len(chosen))

    selected_rows.sort(
        key=lambda row: (
            row["target_split"],
            row["task_type"],
            row["source_doc_ids"][0],
            row["output_id"],
        )
    )

    output_ids = [row["output_id"] for row in selected_rows]
    write_jsonl(Path(args.output_jsonl), selected_rows)
    output_ids_path = Path(args.output_ids)
    output_ids_path.parent.mkdir(parents=True, exist_ok=True)
    output_ids_path.write_text("\n".join(output_ids) + ("\n" if output_ids else ""), encoding="utf-8")

    report = {
        "selection_name": "qwen_data_expansion_wave1",
        "input_paths": [path.replace("\\", "/") for path in input_paths],
        "exclude_jsonl": [path.replace("\\", "/") for path in exclude_paths],
        "focus_doc_ids": sorted(FOCUS_DOC_IDS),
        "min_quality_score": args.min_quality_score,
        "selected_rows": len(selected_rows),
        "selected_by_split": dict(Counter(row["target_split"] for row in selected_rows)),
        "selected_by_task_type": dict(Counter(row["task_type"] for row in selected_rows)),
        "selected_by_doc": dict(Counter(row["source_doc_ids"][0] for row in selected_rows)),
        "train_targets": train_targets,
        "eval_targets": eval_targets,
        "shortages": shortages,
        "available_by_split_task": {
            split: dict(counter) for split, counter in available_by_split_task.items()
        },
        "available_by_split_doc": {
            split: dict(counter) for split, counter in available_by_split_doc.items()
        },
        "rejection_counts": dict(rejection_counts),
        "output_jsonl": args.output_jsonl.replace("\\", "/"),
        "output_ids": args.output_ids.replace("\\", "/"),
    }
    write_json(Path(args.report_output), report)

    print(f"Wrote {len(selected_rows)} reviewed expansion rows -> {args.output_jsonl}")
    print(f"Wrote {len(output_ids)} output ids -> {args.output_ids}")
    print(f"Wrote report -> {args.report_output}")


if __name__ == "__main__":
    main()

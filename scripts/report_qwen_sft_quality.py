from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common import find_repo_root, make_parser, read_jsonl, write_json

GENERIC_STARTERS = (
    "Dafuer gibt der vorliegende Abschnitt keine allgemeine Zusage.",
    "Geht es Ihnen um",
    "Die Dokumentation empfiehlt fuer diesen Fall:",
)
ASSISTANT_ARTIFACT_MARKERS = (
    "Verwenden Sie dazu **Hinweis:**",
    "Verwenden Sie dazu **Tipp:**",
    "Die Dokumentation empfiehlt fuer diesen Fall: Hinweis:",
    "Die Dokumentation empfiehlt fuer diesen Fall: Tipp:",
)
STUB_MARKERS = ("stub", "fixture")


@dataclass(frozen=True)
class Example:
    row_id: str
    split: str
    task_name: str
    prompt: str
    assistant: str
    system: str
    messages: list[dict] | None
    source_doc_ids: tuple[str, ...]
    source_chunk_ids: tuple[str, ...]
    teacher_model: str | None
    teacher_run_id: str | None
    teacher_provider: str | None
    generation_mode: str | None
    review_status: str | None
    behavior_spec_path: str | None


def parse_args() -> Any:
    parser = make_parser("Generate a deterministic quality report for Qwen-SFT style datasets.")
    parser.add_argument("--train-input", required=True)
    parser.add_argument("--eval-input", required=True)
    parser.add_argument("--train-metadata-input")
    parser.add_argument("--eval-metadata-input")
    parser.add_argument("--tokenizer-name-or-path")
    parser.add_argument("--output")
    return parser.parse_args()


def _normalize_whitespace(value: str) -> str:
    return " ".join(str(value).split())


def _normalized_key(value: str) -> str:
    return _normalize_whitespace(value).casefold()


def _preview(value: str, limit: int = 180) -> str:
    normalized = _normalize_whitespace(value)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _message_content(row: dict, role: str) -> str:
    if "messages" not in row:
        return ""
    values = [
        str(message.get("content", "")).strip()
        for message in row.get("messages", [])
        if message.get("role") == role
    ]
    return "\n".join(value for value in values if value).strip()


def _row_id(row: dict) -> str:
    row_id = row.get("id") or row.get("eval_id")
    if not isinstance(row_id, str) or not row_id:
        raise ValueError("Row is missing id/eval_id")
    return row_id


def _meta_by_id(path_str: str | None) -> dict[str, dict]:
    if not path_str:
        return {}
    rows = read_jsonl(Path(path_str))
    meta: dict[str, dict] = {}
    for row in rows:
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise ValueError(f"Metadata row in {path_str} is missing id")
        if row_id in meta:
            raise ValueError(f"Duplicate metadata id {row_id} in {path_str}")
        meta[row_id] = row
    return meta


def _task_name(split: str, row: dict, meta: dict | None) -> str:
    if split == "train":
        return str((meta or {}).get("task_type") or row.get("task_type") or (row.get("meta") or {}).get("task_type") or "unknown")
    return str((meta or {}).get("case_type") or row.get("case_type") or "unknown")


def _behavior_spec_path(row: dict, meta: dict | None) -> str | None:
    provenance = (meta or {}).get("provenance") or row.get("provenance") or (row.get("meta") or {}).get("provenance") or {}
    path_value = provenance.get("behavior_spec_path")
    return str(path_value) if isinstance(path_value, str) and path_value else None


def _canonical_examples(rows: list[dict], split: str, meta_by_id: dict[str, dict]) -> list[Example]:
    examples: list[Example] = []
    for row in rows:
        row_id = _row_id(row)
        meta = meta_by_id.get(row_id)
        if meta_by_id and meta is None:
            raise ValueError(f"Missing metadata row for {row_id}")
        prompt = _message_content(row, "user") if "messages" in row else str(row.get("prompt", "")).strip()
        assistant = _message_content(row, "assistant") if "messages" in row else str(row.get("reference_answer", "")).strip()
        system = _message_content(row, "system")
        source_doc_ids = tuple((meta or {}).get("source_doc_ids") or row.get("source_doc_ids", []) or (row.get("meta") or {}).get("source_doc_ids", []))
        source_chunk_ids = tuple((meta or {}).get("source_chunk_ids") or row.get("source_chunk_ids", []) or (row.get("meta") or {}).get("source_chunk_ids", []))
        examples.append(
            Example(
                row_id=row_id,
                split=split,
                task_name=_task_name(split, row, meta),
                prompt=prompt,
                assistant=assistant,
                system=system,
                messages=row.get("messages") if "messages" in row else None,
                source_doc_ids=tuple(str(item) for item in source_doc_ids),
                source_chunk_ids=tuple(str(item) for item in source_chunk_ids),
                teacher_model=(meta or {}).get("teacher_model") or row.get("teacher_model") or (row.get("meta") or {}).get("teacher_model"),
                teacher_run_id=(meta or {}).get("teacher_run_id") or row.get("teacher_run_id") or (row.get("meta") or {}).get("teacher_run_id"),
                teacher_provider=(meta or {}).get("teacher_provider") or row.get("teacher_provider") or (row.get("meta") or {}).get("teacher_provider"),
                generation_mode=(meta or {}).get("generation_mode") or row.get("generation_mode") or (row.get("meta") or {}).get("generation_mode"),
                review_status=(meta or {}).get("review_status") or row.get("review_status") or (row.get("meta") or {}).get("review_status"),
                behavior_spec_path=_behavior_spec_path(row, meta),
            )
        )
    return examples


def _median(values: list[int]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def _percentile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * fraction) - 1)
    return int(ordered[index])


def _char_stats(values: list[int]) -> dict[str, int | float]:
    if not values:
        return {"median": 0.0, "p95": 0, "p99": 0, "max": 0}
    return {
        "median": _median(values),
        "p95": _percentile(values, 0.95),
        "p99": _percentile(values, 0.99),
        "max": max(values),
    }


def _is_stub(example: Example) -> bool:
    values = (
        example.teacher_model,
        example.teacher_run_id,
        example.teacher_provider,
        example.generation_mode,
    )
    lowered = " ".join(str(value or "").casefold() for value in values)
    return any(marker in lowered for marker in STUB_MARKERS)


def _artifact_matches(example: Example) -> list[str]:
    matches = [marker for marker in ASSISTANT_ARTIFACT_MARKERS if marker in example.assistant]
    if example.assistant.endswith("…") or example.assistant.endswith("..."):
        matches.append("terminal_ellipsis")
    return matches


def _messages_for_tokenizer(repo_root: Path, example: Example) -> list[dict]:
    if example.messages:
        return example.messages

    messages: list[dict] = []
    if example.behavior_spec_path:
        path = Path(example.behavior_spec_path)
        if not path.is_absolute():
            path = repo_root / path
        if path.exists():
            messages.append({"role": "system", "content": path.read_text(encoding="utf-8").strip()})
    messages.append({"role": "user", "content": example.prompt})
    messages.append({"role": "assistant", "content": example.assistant})
    return messages


def _token_stats(repo_root: Path, examples: list[Example], tokenizer_name_or_path: str | None) -> dict[str, Any] | None:
    if not tokenizer_name_or_path:
        return None

    try:
        from transformers import AutoTokenizer
    except ImportError as exc:  # pragma: no cover - depends on optional dependency
        return {"enabled": False, "error": f"transformers_import_failed: {exc}"}

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path, trust_remote_code=True)
    token_lengths: list[int] = []
    for example in examples:
        text = tokenizer.apply_chat_template(
            _messages_for_tokenizer(repo_root, example),
            tokenize=False,
            add_generation_prompt=False,
        )
        token_lengths.append(len(tokenizer(text, add_special_tokens=False)["input_ids"]))

    return {
        "enabled": True,
        "tokenizer_name_or_path": tokenizer_name_or_path,
        "lengths": _char_stats(token_lengths),
    }


def _duplicate_groups(examples: list[Example], key_fn: Any) -> list[tuple[str, list[Example]]]:
    grouped: dict[str, list[Example]] = defaultdict(list)
    for example in examples:
        grouped[key_fn(example)].append(example)
    return [
        (key, sorted(items, key=lambda item: item.row_id))
        for key, items in grouped.items()
        if len(items) > 1
    ]


def _repeated_prompt_candidates(examples: list[Example], limit: int = 20) -> list[dict]:
    grouped: dict[str, list[Example]] = defaultdict(list)
    for example in examples:
        grouped[_normalized_key(example.prompt)].append(example)

    candidates = []
    for _, items in grouped.items():
        if len(items) <= 1:
            continue
        task_distribution = Counter(item.task_name for item in items)
        assistant_variants = Counter(_normalized_key(item.assistant) for item in items)
        candidates.append(
            {
                "prompt_preview": _preview(items[0].prompt),
                "count": len(items),
                "task_distribution": dict(sorted(task_distribution.items())),
                "unique_assistant_count": len(assistant_variants),
                "example_ids": [item.row_id for item in sorted(items, key=lambda item: item.row_id)[:10]],
            }
        )

    candidates.sort(key=lambda item: (-item["count"], item["prompt_preview"]))
    return candidates[:limit]


def _duplicate_pair_candidates(examples: list[Example], limit: int = 20) -> list[dict]:
    groups = _duplicate_groups(examples, lambda item: f"{_normalized_key(item.prompt)}|||{_normalized_key(item.assistant)}")
    candidates = []
    for _, items in groups:
        candidates.append(
            {
                "count": len(items),
                "prompt_preview": _preview(items[0].prompt),
                "assistant_preview": _preview(items[0].assistant),
                "example_ids": [item.row_id for item in items[:10]],
            }
        )
    candidates.sort(key=lambda item: (-item["count"], item["prompt_preview"], item["assistant_preview"]))
    return candidates[:limit]


def _split_metrics(repo_root: Path, examples: list[Example], tokenizer_name_or_path: str | None) -> dict[str, Any]:
    prompt_counter = Counter(_normalized_key(example.prompt) for example in examples)
    assistant_counter = Counter(_normalized_key(example.assistant) for example in examples)
    pair_counter = Counter(
        (_normalized_key(example.prompt), _normalized_key(example.assistant))
        for example in examples
    )
    task_distribution = Counter(example.task_name for example in examples)
    teacher_model_distribution = Counter(str(example.teacher_model or "unknown") for example in examples)
    source_doc_distribution = Counter(doc_id for example in examples for doc_id in example.source_doc_ids)
    assistant_prefixes = Counter(_normalize_whitespace(example.assistant)[:64] for example in examples)
    starter_counts = Counter(
        starter
        for example in examples
        for starter in GENERIC_STARTERS
        if example.assistant.startswith(starter)
    )
    prompt_lengths = [len(example.prompt) for example in examples]
    assistant_lengths = [len(example.assistant) for example in examples]
    total_lengths = [len(example.system) + len(example.prompt) + len(example.assistant) for example in examples]

    artifact_rows = []
    for example in examples:
        matches = _artifact_matches(example)
        if matches:
            artifact_rows.append(
                {
                    "id": example.row_id,
                    "task_name": example.task_name,
                    "markers": matches,
                    "assistant_preview": _preview(example.assistant),
                }
            )

    stub_rows = [
        {
            "id": example.row_id,
            "task_name": example.task_name,
            "teacher_model": example.teacher_model,
            "teacher_run_id": example.teacher_run_id,
        }
        for example in examples
        if _is_stub(example)
    ]

    return {
        "rows": len(examples),
        "unique_prompt_count": len(prompt_counter),
        "unique_assistant_count": len(assistant_counter),
        "unique_pair_count": len(pair_counter),
        "duplicate_excess": {
            "prompt": sum(count - 1 for count in prompt_counter.values() if count > 1),
            "assistant": sum(count - 1 for count in assistant_counter.values() if count > 1),
            "pair": sum(count - 1 for count in pair_counter.values() if count > 1),
        },
        "task_distribution": dict(sorted(task_distribution.items())),
        "teacher_model_distribution": dict(sorted(teacher_model_distribution.items())),
        "source_doc_distribution": dict(sorted(source_doc_distribution.items())),
        "assistant_starter_counts": dict(sorted(starter_counts.items())),
        "top_assistant_prefixes": [
            {"prefix": prefix, "count": count}
            for prefix, count in assistant_prefixes.most_common(12)
        ],
        "char_lengths": {
            "prompt": _char_stats(prompt_lengths),
            "assistant": _char_stats(assistant_lengths),
            "total": _char_stats(total_lengths),
        },
        "token_lengths": _token_stats(repo_root, examples, tokenizer_name_or_path),
        "artifact_rows": artifact_rows,
        "stub_rows": stub_rows,
        "repeated_prompt_candidates": _repeated_prompt_candidates(examples),
        "duplicate_pair_candidates": _duplicate_pair_candidates(examples),
    }


def _overlap_metrics(train_examples: list[Example], eval_examples: list[Example]) -> dict[str, Any]:
    train_prompt_keys = {_normalized_key(example.prompt) for example in train_examples}
    eval_prompt_keys = {_normalized_key(example.prompt) for example in eval_examples}
    train_assistant_keys = {_normalized_key(example.assistant) for example in train_examples}
    eval_assistant_keys = {_normalized_key(example.assistant) for example in eval_examples}
    train_pair_keys = {
        (_normalized_key(example.prompt), _normalized_key(example.assistant))
        for example in train_examples
    }
    eval_pair_keys = {
        (_normalized_key(example.prompt), _normalized_key(example.assistant))
        for example in eval_examples
    }
    train_chunks = {chunk_id for example in train_examples for chunk_id in example.source_chunk_ids}
    eval_chunks = {chunk_id for example in eval_examples for chunk_id in example.source_chunk_ids}
    return {
        "prompt_overlap_count": len(train_prompt_keys & eval_prompt_keys),
        "assistant_overlap_count": len(train_assistant_keys & eval_assistant_keys),
        "pair_overlap_count": len(train_pair_keys & eval_pair_keys),
        "chunk_overlap_count": len(train_chunks & eval_chunks),
        "chunk_overlap_examples": sorted(train_chunks & eval_chunks)[:20],
    }


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())

    train_rows = read_jsonl(Path(args.train_input))
    eval_rows = read_jsonl(Path(args.eval_input))
    train_meta = _meta_by_id(args.train_metadata_input)
    eval_meta = _meta_by_id(args.eval_metadata_input)

    train_examples = _canonical_examples(train_rows, "train", train_meta)
    eval_examples = _canonical_examples(eval_rows, "eval", eval_meta)

    report = {
        "report_version": "qwen_sft_quality_v1",
        "inputs": {
            "train_input": Path(args.train_input).as_posix(),
            "eval_input": Path(args.eval_input).as_posix(),
            "train_metadata_input": Path(args.train_metadata_input).as_posix() if args.train_metadata_input else None,
            "eval_metadata_input": Path(args.eval_metadata_input).as_posix() if args.eval_metadata_input else None,
            "tokenizer_name_or_path": args.tokenizer_name_or_path,
        },
        "train": _split_metrics(repo_root, train_examples, args.tokenizer_name_or_path),
        "eval": _split_metrics(repo_root, eval_examples, args.tokenizer_name_or_path),
        "train_eval_overlap": _overlap_metrics(train_examples, eval_examples),
    }

    if args.output:
        write_json(Path(args.output), report)
        print(f"Wrote quality report -> {args.output}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

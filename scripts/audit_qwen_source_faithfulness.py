from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import find_repo_root, make_parser, read_jsonl, write_json

TASK_THRESHOLDS = {
    "faq_direct_answer": 0.35,
    "troubleshooting": 0.22,
    "step_by_step": 0.22,
    "clarification": 0.10,
    "uncertainty_escalation": 0.10,
}
STOPWORDS = {
    "der",
    "die",
    "das",
    "und",
    "oder",
    "ein",
    "eine",
    "einer",
    "eines",
    "einem",
    "den",
    "dem",
    "des",
    "zu",
    "in",
    "auf",
    "mit",
    "fuer",
    "für",
    "von",
    "ist",
    "sind",
    "wird",
    "werden",
    "sie",
    "ich",
    "es",
    "dass",
    "am",
    "an",
    "im",
    "um",
    "als",
    "auch",
    "nicht",
    "nur",
    "dann",
    "wenn",
    "bei",
    "wie",
    "was",
    "welche",
    "welcher",
    "welches",
    "sich",
    "kann",
    "koennen",
    "können",
    "soll",
    "sollen",
    "laut",
    "dokumentation",
    "hilfe",
    "jaws",
}
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß0-9+\-]{3,}")


def parse_args() -> Any:
    parser = make_parser("Audit source-faithfulness heuristics for Qwen/Gold SFT datasets.")
    parser.add_argument("--train-input", required=True)
    parser.add_argument("--eval-input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-train-flagged-rows", type=int)
    parser.add_argument("--max-eval-flagged-rows", type=int)
    return parser.parse_args()


def _row_id(row: dict) -> str:
    row_id = row.get("id") or row.get("eval_id")
    if not isinstance(row_id, str) or not row_id:
        raise ValueError("Row is missing id/eval_id")
    return row_id


def _task_name(row: dict, split: str) -> str:
    return str(row.get("task_type") if split == "train" else row.get("case_type"))


def _prompt_text(row: dict) -> str:
    if "messages" in row:
        return "\n".join(
            str(message.get("content", "")).strip()
            for message in row.get("messages", [])
            if message.get("role") == "user"
        ).strip()
    return str(row.get("prompt", "")).strip()


def _assistant_text(row: dict) -> str:
    if "messages" in row:
        return "\n".join(
            str(message.get("content", "")).strip()
            for message in row.get("messages", [])
            if message.get("role") == "assistant"
        ).strip()
    return str(row.get("reference_answer", "")).strip()


def _source_records(row: dict) -> list[dict]:
    return list((row.get("provenance") or {}).get("source_records") or [])


def _preview(value: str, limit: int = 220) -> str:
    normalized = " ".join(str(value).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _words(value: str) -> set[str]:
    return {
        token.casefold()
        for token in WORD_RE.findall(value)
        if token.casefold() not in STOPWORDS
    }


def _read_span(repo_root: Path, span: str) -> str:
    range_match = re.match(r"(.+)#L(\d+)-L(\d+)$", span)
    single_match = re.match(r"(.+)#L(\d+)$", span)
    if range_match:
        path_str, start_str, end_str = range_match.groups()
        start, end = int(start_str), int(end_str)
    elif single_match:
        path_str, start_str = single_match.groups()
        start = end = int(start_str)
    else:
        return ""

    path = repo_root / Path(path_str)
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    start_index = max(0, start - 1)
    end_index = min(len(lines), end)
    return "\n".join(lines[start_index:end_index])


def _source_text(repo_root: Path, row: dict) -> str:
    parts: list[str] = []
    for record in _source_records(row):
        for span in record.get("source_spans", []):
            text = _read_span(repo_root, str(span))
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def _row_metrics(repo_root: Path, row: dict, split: str) -> dict[str, Any]:
    task_name = _task_name(row, split)
    assistant = _assistant_text(row)
    prompt = _prompt_text(row)
    source_text = _source_text(repo_root, row)
    assistant_words = _words(assistant)
    source_words = _words(source_text)
    prompt_words = _words(prompt)
    overlap = assistant_words & source_words
    overlap_ratio = len(overlap) / max(1, len(assistant_words))
    threshold = TASK_THRESHOLDS.get(task_name, 0.2)
    novel_ratio = len(assistant_words - source_words - prompt_words) / max(1, len(assistant_words))

    flags: list[str] = []
    if overlap_ratio < threshold:
        flags.append("low_lexical_overlap")
    if novel_ratio > 0.75 and task_name in {"faq_direct_answer", "troubleshooting", "step_by_step"}:
        flags.append("high_novel_word_ratio")
    if assistant.endswith("...") or assistant.endswith("…"):
        flags.append("assistant_ends_with_ellipsis")
    if not source_text:
        flags.append("missing_source_text")

    first_record = _source_records(row)[0] if _source_records(row) else {}
    return {
        "id": _row_id(row),
        "split": split,
        "task_name": task_name,
        "overlap_ratio": round(overlap_ratio, 4),
        "novel_word_ratio": round(novel_ratio, 4),
        "assistant_word_count": len(assistant_words),
        "source_word_count": len(source_words),
        "threshold": threshold,
        "flags": flags,
        "source_doc_ids": row.get("source_doc_ids", []),
        "source_chunk_ids": row.get("source_chunk_ids", []),
        "source_section_title": first_record.get("section_title"),
        "source_spans": first_record.get("source_spans", []),
        "prompt_preview": _preview(prompt),
        "assistant_preview": _preview(assistant),
        "source_preview": _preview(source_text),
    }


def _split_report(repo_root: Path, rows: list[dict], split: str) -> dict[str, Any]:
    metrics = [_row_metrics(repo_root, row, split) for row in rows]
    flagged = [item for item in metrics if item["flags"]]
    lowest_overlap = sorted(metrics, key=lambda item: (item["overlap_ratio"], item["id"]))[:25]
    return {
        "rows": len(rows),
        "flagged_rows": len(flagged),
        "flags_by_type": dict(sorted(Counter(flag for item in flagged for flag in item["flags"]).items())),
        "rows_by_task": dict(sorted(Counter(item["task_name"] for item in metrics).items())),
        "flagged_examples": sorted(
            flagged,
            key=lambda item: (len(item["flags"]) * -1, item["overlap_ratio"], item["id"]),
        )[:50],
        "lowest_overlap_examples": lowest_overlap,
    }


def _gate_result(flagged_rows: int, max_allowed: int | None) -> dict[str, Any]:
    if max_allowed is None:
        return {
            "enabled": False,
            "max_allowed_flagged_rows": None,
            "flagged_rows": flagged_rows,
            "passed": True,
        }
    return {
        "enabled": True,
        "max_allowed_flagged_rows": max_allowed,
        "flagged_rows": flagged_rows,
        "passed": flagged_rows <= max_allowed,
    }


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())

    train_rows = read_jsonl(Path(args.train_input))
    eval_rows = read_jsonl(Path(args.eval_input))
    train_report = _split_report(repo_root, train_rows, "train")
    eval_report = _split_report(repo_root, eval_rows, "eval")

    report = {
        "audit_version": "qwen_source_faithfulness_v2",
        "inputs": {
            "train_input": Path(args.train_input).as_posix(),
            "eval_input": Path(args.eval_input).as_posix(),
        },
        "thresholds": TASK_THRESHOLDS,
        "heuristic_notes": [
            "Lexical overlap is a heuristic and may under-score good clarification or escalation answers.",
            "Flags are intended for review prioritization unless max flagged-row thresholds are provided.",
        ],
        "train": train_report,
        "eval": eval_report,
        "gate": {
            "train": _gate_result(train_report["flagged_rows"], args.max_train_flagged_rows),
            "eval": _gate_result(eval_report["flagged_rows"], args.max_eval_flagged_rows),
        },
    }

    write_json(Path(args.output), report)
    print(f"Wrote source-faithfulness audit -> {args.output}")

    failures = []
    for split in ("train", "eval"):
        gate = report["gate"][split]
        if gate["enabled"] and not gate["passed"]:
            failures.append(
                f"{split} flagged_rows={gate['flagged_rows']} exceeds max_allowed={gate['max_allowed_flagged_rows']}"
            )
    if failures:
        raise SystemExit("Audit gate failed: " + "; ".join(failures))


if __name__ == "__main__":
    main()

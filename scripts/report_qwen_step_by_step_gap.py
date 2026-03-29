from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_jaws_teacher_wave import generate_drafts_for_chunk, load_chunk_exclusions, load_chunks, stable_hash
from common import make_parser, write_json


DEFAULT_REPORT_OUTPUT = "data/derived/teacher_jobs/JAWS/DE/qwen_step_by_step_gap_report.json"
DEFAULT_IDS_OUTPUT = "data/derived/teacher_jobs/JAWS/DE/qwen_step_by_step_candidate_chunk_ids.txt"


def parse_args() -> Any:
    parser = make_parser("Report remaining Qwen step-by-step candidate coverage after gold/output exclusions.")
    parser.add_argument("--chunks-root", default="data/derived/chunks/JAWS/DE")
    parser.add_argument("--report-output", default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--ids-output", default=DEFAULT_IDS_OUTPUT)
    parser.add_argument("--exclude-jsonl", action="append", default=[])
    parser.add_argument("--exclude-dir", action="append", default=[])
    parser.add_argument("--eval-modulo", type=int, default=8)
    parser.add_argument("--eval-remainder", type=int, default=0)
    parser.add_argument("--top-n", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.eval_modulo <= 1:
        raise SystemExit("--eval-modulo must be > 1")
    if not 0 <= args.eval_remainder < args.eval_modulo:
        raise SystemExit("--eval-remainder must be between 0 and eval-modulo-1")
    if args.top_n <= 0:
        raise SystemExit("--top-n must be > 0")

    chunks = load_chunks(Path(args.chunks_root))
    excluded_chunk_ids = load_chunk_exclusions(args.exclude_jsonl, args.exclude_dir)

    by_split_doc: dict[str, Counter[str]] = {"train": Counter(), "eval": Counter()}
    candidates: list[dict[str, Any]] = []

    for chunk in chunks:
        if chunk["chunk_id"] in excluded_chunk_ids:
            continue
        draft = next((item for item in generate_drafts_for_chunk(chunk) if item.task_type == "step_by_step"), None)
        if draft is None:
            continue
        split = "eval" if stable_hash(chunk["chunk_id"]) % args.eval_modulo == args.eval_remainder else "train"
        by_split_doc[split][chunk["doc_id"]] += 1
        candidates.append(
            {
                "split": split,
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "section_id": chunk["section_id"],
                "section_title": chunk["section_title"],
                "section_path_text": chunk.get("section_path_text"),
                "normalized_path": chunk["normalized_path"],
                "source_spans": chunk["source_spans"],
                "char_count": chunk["char_count"],
                "quality_score": draft.score,
                "selection_reason": draft.selection_reason,
            }
        )

    candidates.sort(key=lambda item: (-item["quality_score"], item["chunk_id"]))
    top_candidates = candidates[: args.top_n]
    ids_output = Path(args.ids_output)
    ids_output.parent.mkdir(parents=True, exist_ok=True)
    ids_output.write_text("\n".join(item["chunk_id"] for item in candidates) + ("\n" if candidates else ""), encoding="utf-8")

    report = {
        "report_name": "qwen_step_by_step_gap",
        "exclude_jsonl": args.exclude_jsonl,
        "exclude_dir": args.exclude_dir,
        "excluded_chunk_ids": len(excluded_chunk_ids),
        "eval_split_rule": {"modulo": args.eval_modulo, "remainder": args.eval_remainder},
        "remaining_candidates": len(candidates),
        "remaining_by_split": dict(Counter(item["split"] for item in candidates)),
        "remaining_by_doc": {split: dict(by_split_doc[split]) for split in ["train", "eval"]},
        "top_candidates": top_candidates,
        "ids_output": args.ids_output,
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote step-by-step gap report -> {args.report_output}")
    print(f"Wrote candidate chunk ids -> {args.ids_output}")


if __name__ == "__main__":
    main()

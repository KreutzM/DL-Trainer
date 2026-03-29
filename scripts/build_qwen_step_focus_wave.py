from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_jaws_teacher_wave import (
    BEHAVIOR_SPEC_PATH,
    build_job,
    generate_drafts_for_chunk,
    load_chunks,
    stable_hash,
)
from common import make_parser, read_jsonl, write_json, write_jsonl


DEFAULT_WAVE_ID = "jaws_de_teacher_qwen_step_focus_wave_v1"
DEFAULT_JOBS_OUTPUT = "data/derived/teacher_jobs/JAWS/DE/qwen_step_focus_wave_v1_generation_jobs.jsonl"
DEFAULT_REPORT_OUTPUT = "data/derived/teacher_jobs/JAWS/DE/qwen_step_focus_wave_v1_generation_report.json"
DEFAULT_IDS_OUTPUT = "data/derived/teacher_jobs/JAWS/DE/qwen_step_focus_wave_v1_job_ids.txt"
DEFAULT_EXCLUDE_TASKS = {"step_by_step"}


def round_robin_select(
    candidates_by_doc: dict[str, list[tuple[dict, Any]]],
    target_count: int,
    used_chunks: set[str],
) -> list[tuple[dict, Any]]:
    ordered_docs = sorted(candidates_by_doc, key=lambda doc_id: (stable_hash(doc_id) % 1000, doc_id))
    selected: list[tuple[dict, Any]] = []
    while len(selected) < target_count:
        progressed = False
        for doc_id in ordered_docs:
            pool = candidates_by_doc[doc_id]
            while pool and pool[0][0]["chunk_id"] in used_chunks:
                pool.pop(0)
            if not pool:
                continue
            chunk, draft = pool.pop(0)
            used_chunks.add(chunk["chunk_id"])
            selected.append((chunk, draft))
            progressed = True
            if len(selected) >= target_count:
                break
        if not progressed:
            break
    return selected


def parse_args() -> Any:
    parser = make_parser("Build a targeted Qwen step-by-step teacher wave using step-specific exclusions.")
    parser.add_argument("--chunks-root", default="data/derived/chunks/JAWS/DE")
    parser.add_argument("--jobs-output", default=DEFAULT_JOBS_OUTPUT)
    parser.add_argument("--report-output", default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--ids-output", default=DEFAULT_IDS_OUTPUT)
    parser.add_argument("--wave-id", default=DEFAULT_WAVE_ID)
    parser.add_argument("--exclude-jsonl", action="append", default=[])
    parser.add_argument("--exclude-task-type", action="append", default=[])
    parser.add_argument("--focus-doc", action="append", default=[])
    parser.add_argument("--max-train", type=int, default=24)
    parser.add_argument("--max-eval", type=int, default=6)
    parser.add_argument("--eval-modulo", type=int, default=8)
    parser.add_argument("--eval-remainder", type=int, default=0)
    return parser.parse_args()


def load_task_specific_exclusions(paths: list[str], allowed_task_types: set[str]) -> set[str]:
    chunk_ids: set[str] = set()
    for path_str in paths:
        for row in read_jsonl(Path(path_str)):
            task_type = row.get("task_type") or row.get("case_type")
            if task_type not in allowed_task_types:
                continue
            chunk_ids.update(row.get("source_chunk_ids", []))
    return chunk_ids


def main() -> None:
    args = parse_args()
    if args.eval_modulo <= 1:
        raise SystemExit("--eval-modulo must be > 1")
    if not 0 <= args.eval_remainder < args.eval_modulo:
        raise SystemExit("--eval-remainder must be between 0 and eval-modulo-1")
    if args.max_train < 0 or args.max_eval < 0:
        raise SystemExit("--max-train and --max-eval must be >= 0")

    focus_docs = set(args.focus_doc)
    exclude_task_types = set(args.exclude_task_type) if args.exclude_task_type else set(DEFAULT_EXCLUDE_TASKS)
    chunks = load_chunks(Path(args.chunks_root))
    system_prompt = Path(BEHAVIOR_SPEC_PATH).read_text(encoding="utf-8").strip()
    excluded_chunk_ids = load_task_specific_exclusions(args.exclude_jsonl, exclude_task_types)

    available_by_split_doc: dict[str, Counter[str]] = {"train": Counter(), "eval": Counter()}
    available_by_split_reason: dict[str, Counter[str]] = {"train": Counter(), "eval": Counter()}
    candidates_by_split_doc: dict[str, dict[str, list[tuple[dict, Any]]]] = {
        "train": defaultdict(list),
        "eval": defaultdict(list),
    }

    for chunk in chunks:
        if focus_docs and chunk["doc_id"] not in focus_docs:
            continue
        if chunk["chunk_id"] in excluded_chunk_ids:
            continue
        draft = next((item for item in generate_drafts_for_chunk(chunk) if item.task_type == "step_by_step"), None)
        if draft is None:
            continue
        split = "eval" if stable_hash(chunk["chunk_id"]) % args.eval_modulo == args.eval_remainder else "train"
        candidates_by_split_doc[split][chunk["doc_id"]].append((chunk, draft))
        available_by_split_doc[split][chunk["doc_id"]] += 1
        available_by_split_reason[split][draft.selection_reason] += 1

    for split in ["train", "eval"]:
        for doc_id, items in candidates_by_split_doc[split].items():
            items.sort(key=lambda item: (-item[1].score, stable_hash(item[0]["chunk_id"])))
            candidates_by_split_doc[split][doc_id] = items

    used_chunks: set[str] = set()
    eval_selected = round_robin_select(candidates_by_split_doc["eval"], args.max_eval, used_chunks)
    train_selected = round_robin_select(candidates_by_split_doc["train"], args.max_train, used_chunks)

    jobs: list[dict] = []
    counter = 0
    selected = [("eval", *item) for item in eval_selected] + [("train", *item) for item in train_selected]
    for split, chunk, draft in selected:
        counter += 1
        jobs.append(build_job(split, counter, chunk, draft, system_prompt, args.wave_id))

    write_jsonl(Path(args.jobs_output), jobs)
    Path(args.ids_output).write_text(
        "\n".join(job["job_id"] for job in jobs) + ("\n" if jobs else ""),
        encoding="utf-8",
    )
    report = {
        "wave_id": args.wave_id,
        "exclude_jsonl": args.exclude_jsonl,
        "exclude_task_types": sorted(exclude_task_types),
        "focus_doc_ids": sorted(focus_docs) if focus_docs else [],
        "excluded_chunk_ids": len(excluded_chunk_ids),
        "eval_split_rule": {"modulo": args.eval_modulo, "remainder": args.eval_remainder},
        "targets": {"train": args.max_train, "eval": args.max_eval},
        "available_by_split_doc": {split: dict(available_by_split_doc[split]) for split in ["train", "eval"]},
        "available_by_split_reason": {split: dict(available_by_split_reason[split]) for split in ["train", "eval"]},
        "selected_jobs": len(jobs),
        "selected_by_split": dict(Counter(job["target_split"] for job in jobs)),
        "selected_by_doc": dict(Counter(job["source_doc_ids"][0] for job in jobs)),
        "shortages": {
            "train": max(0, args.max_train - len(train_selected)),
            "eval": max(0, args.max_eval - len(eval_selected)),
        },
        "jobs_output": args.jobs_output,
        "ids_output": args.ids_output,
    }
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(jobs)} step-focus teacher jobs -> {args.jobs_output}")
    print(f"Wrote selection report -> {args.report_output}")
    print(f"Wrote job ids -> {args.ids_output}")


if __name__ == "__main__":
    main()

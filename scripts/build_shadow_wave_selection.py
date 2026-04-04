from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from common import make_parser, read_json, read_jsonl, write_json

TASK_ORDER = [
    "clarification",
    "faq_direct_answer",
    "step_by_step",
    "troubleshooting",
    "uncertainty_escalation",
]
DEFAULT_TOTAL_TARGETS = {
    "clarification": 6,
    "faq_direct_answer": 6,
    "step_by_step": 8,
    "troubleshooting": 6,
    "uncertainty_escalation": 6,
}
DEFAULT_SPLIT_TASK_TOP_OFF = {
    ("eval", "clarification"): 1,
    ("eval", "faq_direct_answer"): 1,
    ("eval", "step_by_step"): 2,
    ("eval", "troubleshooting"): 1,
    ("eval", "uncertainty_escalation"): 1,
    ("train", "clarification"): 1,
    ("train", "faq_direct_answer"): 1,
    ("train", "step_by_step"): 2,
    ("train", "troubleshooting"): 1,
    ("train", "uncertainty_escalation"): 1,
}


def parse_task_count_overrides(values: list[str], *, label: str) -> dict[str, int]:
    overrides: dict[str, int] = {}
    for raw_value in values:
        try:
            key, count_text = raw_value.split("=", 1)
        except ValueError as exc:
            raise SystemExit(f"Invalid {label} override '{raw_value}'. Expected key=count.") from exc
        key = key.strip()
        if key not in TASK_ORDER:
            raise SystemExit(f"Invalid {label} task '{key}'. Expected one of: {', '.join(TASK_ORDER)}")
        try:
            count = int(count_text)
        except ValueError as exc:
            raise SystemExit(f"Invalid {label} count '{raw_value}'. Count must be an integer.") from exc
        if count < 0:
            raise SystemExit(f"Invalid {label} count '{raw_value}'. Count must be >= 0.")
        overrides[key] = count
    return overrides


def parse_split_task_count_overrides(values: list[str]) -> dict[tuple[str, str], int]:
    overrides: dict[tuple[str, str], int] = {}
    for raw_value in values:
        try:
            split_task, count_text = raw_value.split("=", 1)
            split, task_type = split_task.split(":", 1)
        except ValueError as exc:
            raise SystemExit(
                f"Invalid --target-split-task-count '{raw_value}'. Expected split:task_type=count."
            ) from exc
        split = split.strip()
        task_type = task_type.strip()
        if split not in {"train", "eval"}:
            raise SystemExit(f"Invalid split '{split}' in '{raw_value}'. Expected train or eval.")
        if task_type not in TASK_ORDER:
            raise SystemExit(f"Invalid task_type '{task_type}' in '{raw_value}'. Expected one of: {', '.join(TASK_ORDER)}")
        try:
            count = int(count_text)
        except ValueError as exc:
            raise SystemExit(f"Invalid split/task count '{raw_value}'. Count must be an integer.") from exc
        if count < 0:
            raise SystemExit(f"Invalid split/task count '{raw_value}'. Count must be >= 0.")
        overrides[(split, task_type)] = count
    return overrides


def parse_args() -> Any:
    parser = make_parser("Build a larger deterministic JAWS-DE OpenRouter shadow selection from the current 20-job seed.")
    parser.add_argument("--jobs", default="data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl")
    parser.add_argument(
        "--seed-selection",
        default="data/derived/teacher_jobs/JAWS/DE/current_generation_selection.json",
    )
    parser.add_argument(
        "--output-job-ids",
        default="data/derived/teacher_jobs/JAWS/DE/shadow_wave_2026_04_04_user_answer_v1_job_ids.txt",
    )
    parser.add_argument(
        "--output-selection",
        default="data/derived/teacher_jobs/JAWS/DE/shadow_wave_2026_04_04_user_answer_v1_selection.json",
    )
    parser.add_argument(
        "--selection-id",
        default="jaws_de_shadow_wave_2026_04_04_user_answer_v1",
    )
    parser.add_argument(
        "--workflow-role",
        default="shadow_wave_user_answer_gpt54_v1",
    )
    parser.add_argument(
        "--target-total-count",
        action="append",
        default=[],
        help="Override per-task totals as task_type=count. May be passed multiple times.",
    )
    parser.add_argument(
        "--target-split-task-count",
        action="append",
        default=[],
        help="Override per-split/per-task totals as split:task_type=count. May be passed multiple times.",
    )
    return parser.parse_args()


def normalized_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def load_seed_job_ids(selection_manifest: dict[str, Any], repo_root: Path) -> list[str]:
    job_ids_file = selection_manifest.get("job_ids_file")
    if not job_ids_file:
        raise SystemExit("Seed selection manifest is missing job_ids_file")
    path = repo_root / job_ids_file
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def resolved_total_targets(args: Any) -> dict[str, int]:
    targets = dict(DEFAULT_TOTAL_TARGETS)
    targets.update(parse_task_count_overrides(args.target_total_count, label="target-total-count"))
    return targets


def resolved_split_task_targets(args: Any) -> dict[tuple[str, str], int]:
    targets = {(split, task_type): 2 for split in ("eval", "train") for task_type in TASK_ORDER}
    for split_task, count in DEFAULT_SPLIT_TASK_TOP_OFF.items():
        targets[split_task] += count
    targets.update(parse_split_task_count_overrides(args.target_split_task_count))
    return targets


def choose_top_off_rows(
    rows: list[dict[str, Any]],
    selected_ids: set[str],
    seen_chunk_ids: set[str],
    selected_doc_counts: Counter[str],
    split_task_counts: Counter[tuple[str, str]],
    split_task_targets: dict[tuple[str, str], int],
) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    for split in ("eval", "train"):
        for task_type in TASK_ORDER:
            target_count = split_task_targets[(split, task_type)] - split_task_counts[(split, task_type)]
            if target_count <= 0:
                continue
            candidates = [
                row
                for row in rows
                if row["job_id"] not in selected_ids
                and row["target_split"] == split
                and row["task_type"] == task_type
                and not set(row["source_chunk_ids"]) & seen_chunk_ids
            ]
            candidates.sort(
                key=lambda row: (
                    selected_doc_counts[row["source_doc_ids"][0]],
                    split_task_counts[(row["target_split"], row["task_type"])],
                    -int(row.get("quality_score") or 0),
                    row["source_doc_ids"][0],
                    row["job_id"],
                )
            )
            if len(candidates) < target_count:
                raise SystemExit(
                    f"Not enough candidates for {split}/{task_type}: need {target_count}, found {len(candidates)}"
                )
            for row in candidates[:target_count]:
                chosen.append(row)
                selected_ids.add(row["job_id"])
                seen_chunk_ids.update(row["source_chunk_ids"])
                selected_doc_counts[row["source_doc_ids"][0]] += 1
                split_task_counts[(row["target_split"], row["task_type"])] += 1
    return chosen


def build_report(
    *,
    args: Any,
    seed_manifest: dict[str, Any],
    selected_rows: list[dict[str, Any]],
    added_rows: list[dict[str, Any]],
    total_targets: dict[str, int],
    split_task_targets: dict[tuple[str, str], int],
) -> dict[str, Any]:
    task_counts = Counter(row["task_type"] for row in selected_rows)
    split_counts = Counter(row["target_split"] for row in selected_rows)
    split_task_counts: dict[str, dict[str, int]] = {}
    for split in sorted(split_counts):
        split_task_counts[split] = {
            task_type: sum(1 for row in selected_rows if row["target_split"] == split and row["task_type"] == task_type)
            for task_type in TASK_ORDER
            if any(row["target_split"] == split and row["task_type"] == task_type for row in selected_rows)
        }

    return {
        "selection_id": args.selection_id,
        "workflow_role": args.workflow_role,
        "jobs_file": normalized_path(Path(args.jobs)),
        "job_ids_file": normalized_path(Path(args.output_job_ids)),
        "selected_job_count": len(selected_rows),
        "selection_summary": {
            "train_examples": split_counts.get("train", 0),
            "eval_examples": split_counts.get("eval", 0),
            "task_types": TASK_ORDER,
            "task_type_counts": dict(sorted(task_counts.items())),
            "target_task_type_counts": dict(sorted(total_targets.items())),
            "split_task_counts": split_task_counts,
            "target_split_task_counts": {
                split: {
                    task_type: split_task_targets[(split, task_type)]
                    for task_type in TASK_ORDER
                    if split_task_targets[(split, task_type)] > 0
                }
                for split in ("eval", "train")
            },
            "seed_job_count": seed_manifest.get("selected_job_count"),
            "top_off_job_count": len(added_rows),
            "selection_strategy": (
                "Starts from the existing current_generation_selection seed, then deterministically tops off wave1 jobs "
                "without reusing source_chunk_ids. Additional jobs are chosen by split/task target, preferring lower "
                "already-selected document counts, then higher fixture quality_score, then stable doc_id/job_id ordering."
            ),
        },
        "historical_source": {
            "selection_manifest": seed_manifest,
        },
        "job_ids": [row["job_id"] for row in selected_rows],
        "top_off_job_ids": [row["job_id"] for row in added_rows],
    }


def build_selection(
    rows: list[dict[str, Any]],
    seed_job_ids: list[str],
    *,
    split_task_targets: dict[tuple[str, str], int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Counter[tuple[str, str]]]:
    by_job_id = {row["job_id"]: row for row in rows}
    selected_rows: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    seen_chunk_ids: set[str] = set()
    selected_doc_counts: Counter[str] = Counter()
    split_task_counts: Counter[tuple[str, str]] = Counter()

    for job_id in seed_job_ids:
        row = by_job_id.get(job_id)
        if row is None:
            raise SystemExit(f"Seed job ID not found in jobs file: {job_id}")
        selected_rows.append(row)
        selected_ids.add(job_id)
        seen_chunk_ids.update(row["source_chunk_ids"])
        selected_doc_counts[row["source_doc_ids"][0]] += 1
        split_task_counts[(row["target_split"], row["task_type"])] += 1

    added_rows = choose_top_off_rows(
        rows,
        selected_ids,
        seen_chunk_ids,
        selected_doc_counts,
        split_task_counts,
        split_task_targets,
    )
    selected_rows.extend(added_rows)
    selected_rows.sort(key=lambda row: row["job_id"])
    return selected_rows, added_rows, split_task_counts


def main() -> None:
    args = parse_args()
    repo_root = Path.cwd()
    total_targets = resolved_total_targets(args)
    split_task_targets = resolved_split_task_targets(args)
    rows = read_jsonl(repo_root / args.jobs)
    seed_manifest = read_json(repo_root / args.seed_selection)
    seed_job_ids = load_seed_job_ids(seed_manifest, repo_root)
    selected_rows, added_rows, split_task_counts = build_selection(
        rows,
        seed_job_ids,
        split_task_targets=split_task_targets,
    )

    task_counts = Counter(row["task_type"] for row in selected_rows)
    if dict(sorted(task_counts.items())) != total_targets:
        raise SystemExit(
            "Selected task counts do not match targets: "
            f"{dict(sorted(task_counts.items()))} != {total_targets}"
        )
    expected_split_task_counts = {
        split: {task_type: split_task_targets[(split, task_type)] for task_type in TASK_ORDER}
        for split in ("eval", "train")
    }
    actual_split_task_counts = {
        split: {task_type: split_task_counts[(split, task_type)] for task_type in TASK_ORDER}
        for split in ("eval", "train")
    }
    if actual_split_task_counts != expected_split_task_counts:
        raise SystemExit(
            "Selected split/task counts do not match targets: "
            f"{actual_split_task_counts} != {expected_split_task_counts}"
        )

    output_job_ids = Path(args.output_job_ids)
    output_job_ids.parent.mkdir(parents=True, exist_ok=True)
    output_job_ids.write_text(
        "\n".join(row["job_id"] for row in selected_rows) + "\n",
        encoding="utf-8",
    )

    report = build_report(
        args=args,
        seed_manifest=seed_manifest,
        selected_rows=selected_rows,
        added_rows=added_rows,
        total_targets=total_targets,
        split_task_targets=split_task_targets,
    )
    write_json(Path(args.output_selection), report)
    print(f"Wrote {len(selected_rows)} job IDs -> {args.output_job_ids}")
    print(f"Wrote selection manifest -> {args.output_selection}")


if __name__ == "__main__":
    main()

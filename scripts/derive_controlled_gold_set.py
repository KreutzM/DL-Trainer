from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import find_repo_root, make_parser, read_json, read_jsonl, sha256_file, write_json, write_jsonl

EXPORT_PIPELINE_VERSION = "0.1.0"
DEFAULT_SOURCE_PRE_GOLD_DIR = Path("data/derived/pre_gold/JAWS/DE/openrouter_gpt54_curated_pre_gold_v16")
DEFAULT_GOLD_OUTPUT_DIR = Path("data/derived/gold/JAWS/DE/openrouter_gpt54_controlled_gold_v16")
DEFAULT_GOLD_TRAIN_OUTPUT = Path("data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl")
DEFAULT_GOLD_EVAL_OUTPUT = Path("data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl")


def normalized_path(path: Path) -> str:
    return path.as_posix()


def build_promoted_from(row: dict[str, Any], source_path: Path) -> dict[str, Any]:
    return {
        "teacher_output_path": normalized_path(source_path),
        "output_id": row["output_id"],
        "job_id": row["job_id"],
        "teacher_provider": row.get("teacher_provider"),
        "teacher_model": row.get("teacher_model"),
        "teacher_run_id": row["teacher_run_id"],
    }


def build_train_meta(
    *,
    candidate: dict[str, Any],
    gold_path: Path,
    source_pre_gold_dir: Path,
    source_pre_gold_summary: Path,
    source_pre_gold_manifest: Path,
) -> dict[str, Any]:
    meta = {
        "id": candidate["id"],
        "split": "train",
        "record_type": "sft_train",
        "product": candidate.get("product"),
        "language": candidate.get("language"),
        "task_type": candidate.get("task_type"),
        "case_type": candidate.get("case_type"),
        "source_doc_ids": candidate.get("source_doc_ids", []),
        "source_chunk_ids": candidate.get("source_chunk_ids", []),
        "teacher_provider": candidate.get("teacher_provider"),
        "teacher_model": candidate.get("teacher_model"),
        "teacher_run_id": candidate.get("teacher_run_id"),
        "teacher_prompt_version": candidate.get("teacher_prompt_version"),
        "generation_mode": candidate.get("generation_mode"),
        "review_status": "promoted",
        "approved_by": candidate.get("approved_by"),
        "gold_source_path": normalized_path(gold_path),
        "promoted_from": candidate.get("promoted_from"),
        "provenance": candidate.get("provenance", {}),
        "expected_behavior": candidate.get("expected_behavior"),
        "reference_answer": candidate.get("reference_answer"),
        "rubric": candidate.get("rubric"),
        "pre_gold_source_path": normalized_path(source_pre_gold_dir),
        "pre_gold_summary_path": normalized_path(source_pre_gold_summary),
        "pre_gold_manifest_path": normalized_path(source_pre_gold_manifest),
        "candidate_selection_status": "approved_only",
    }
    if candidate.get("task_type") == "clarification":
        meta["needs_clarification"] = True
    return meta


def build_eval_meta(
    *,
    candidate: dict[str, Any],
    gold_path: Path,
    source_pre_gold_dir: Path,
    source_pre_gold_summary: Path,
    source_pre_gold_manifest: Path,
) -> dict[str, Any]:
    return {
        "id": candidate["eval_id"],
        "split": "eval",
        "record_type": "sft_eval",
        "product": candidate.get("product"),
        "language": candidate.get("language"),
        "task_type": candidate.get("case_type"),
        "case_type": candidate.get("case_type"),
        "source_doc_ids": candidate.get("source_doc_ids", []),
        "source_chunk_ids": candidate.get("source_chunk_ids", []),
        "teacher_provider": candidate.get("teacher_provider"),
        "teacher_model": candidate.get("teacher_model"),
        "teacher_run_id": candidate.get("teacher_run_id"),
        "teacher_prompt_version": candidate.get("teacher_prompt_version"),
        "generation_mode": candidate.get("generation_mode"),
        "review_status": "promoted",
        "approved_by": candidate.get("approved_by"),
        "gold_source_path": normalized_path(gold_path),
        "promoted_from": candidate.get("promoted_from"),
        "provenance": candidate.get("provenance", {}),
        "expected_behavior": candidate.get("expected_behavior"),
        "reference_answer": candidate.get("reference_answer"),
        "rubric": candidate.get("rubric"),
        "pre_gold_source_path": normalized_path(source_pre_gold_dir),
        "pre_gold_summary_path": normalized_path(source_pre_gold_summary),
        "pre_gold_manifest_path": normalized_path(source_pre_gold_manifest),
        "candidate_selection_status": "approved_only",
    }


def build_summary(
    *,
    export_id: str,
    source_pre_gold_dir: Path,
    source_pre_gold_summary: Path,
    source_pre_gold_manifest: Path,
    source_reviewed_path: Path,
    train_rows: list[dict[str, Any]],
    eval_rows: list[dict[str, Any]],
    rejected_rows: list[dict[str, Any]],
    output_dir: Path,
) -> dict[str, Any]:
    train_task_counts = Counter(row["task_type"] for row in train_rows)
    eval_task_counts = Counter(row["case_type"] for row in eval_rows)
    source_doc_counts = Counter(
        doc_id for row in [*train_rows, *eval_rows] for doc_id in row.get("source_doc_ids", [])
    )
    rejected_task_counts = Counter(row["task_type"] for row in rejected_rows)
    rejected_decision_counts = Counter((row.get("auto_review") or {}).get("decision") for row in rejected_rows)

    return {
        "export_id": export_id,
        "output_dir": normalized_path(output_dir),
        "export_generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "export_pipeline_version": EXPORT_PIPELINE_VERSION,
        "source_pre_gold_dir": normalized_path(source_pre_gold_dir),
        "source_pre_gold_summary": normalized_path(source_pre_gold_summary),
        "source_pre_gold_manifest": normalized_path(source_pre_gold_manifest),
        "source_reviewed_path": normalized_path(source_reviewed_path),
        "derived_train_rows": len(train_rows),
        "derived_eval_rows": len(eval_rows),
        "derived_rows": len(train_rows) + len(eval_rows),
        "derived_train_task_type_counts": dict(sorted(train_task_counts.items())),
        "derived_eval_task_type_counts": dict(sorted(eval_task_counts.items())),
        "source_doc_distribution": dict(sorted(source_doc_counts.items())),
        "rejected_rows": len(rejected_rows),
        "rejected_task_type_counts": dict(sorted(rejected_task_counts.items())),
        "rejected_decision_counts": dict(sorted(rejected_decision_counts.items())),
        "excluded_rows": [
            {
                "job_id": row["job_id"],
                "task_type": row["task_type"],
                "record_type": row["record_type"],
                "decision": (row.get("auto_review") or {}).get("decision"),
                "quality_score": row.get("auto_review", {}).get("quality_score"),
                "summary": row.get("auto_review", {}).get("summary"),
            }
            for row in rejected_rows
        ],
        "sensitive_rest_areas": {
            "step_by_step": [
                {
                    "job_id": row["job_id"],
                    "task_type": row["task_type"],
                    "record_type": row["record_type"],
                    "decision": (row.get("auto_review") or {}).get("decision"),
                    "quality_score": row.get("auto_review", {}).get("quality_score"),
                    "summary": row.get("auto_review", {}).get("summary"),
                }
                for row in rejected_rows
                if row["task_type"] == "step_by_step"
            ],
            "clarification": [
                {
                    "job_id": row["job_id"],
                    "task_type": row["task_type"],
                    "record_type": row["record_type"],
                    "decision": (row.get("auto_review") or {}).get("decision"),
                    "quality_score": row.get("auto_review", {}).get("quality_score"),
                    "summary": row.get("auto_review", {}).get("summary"),
                }
                for row in rejected_rows
                if row["task_type"] == "clarification"
            ],
        },
        "decision": {
            "status": "controlled_gold_derived",
            "no_new_gold_promotion": True,
            "statement": (
                "This gold stand is derived offline from the approved rows of the v16 pre-gold candidate set. "
                "The rejected step_by_step and clarification rows remain excluded and visible in the summary."
            ),
        },
    }


def build_manifest(
    *,
    export_id: str,
    output_dir: Path,
    source_pre_gold_dir: Path,
    source_pre_gold_summary: Path,
    source_pre_gold_manifest: Path,
    source_reviewed_path: Path,
    train_path: Path,
    eval_path: Path,
    train_meta_path: Path,
    eval_meta_path: Path,
    summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "export_id": export_id,
        "export_generated_at_utc": summary["export_generated_at_utc"],
        "format": "qwen_openai_messages",
        "export_pipeline_version": EXPORT_PIPELINE_VERSION,
        "output_dir": normalized_path(output_dir),
        "source_pre_gold_dir": normalized_path(source_pre_gold_dir),
        "source_pre_gold_summary": normalized_path(source_pre_gold_summary),
        "source_pre_gold_manifest": normalized_path(source_pre_gold_manifest),
        "source_reviewed_path": normalized_path(source_reviewed_path),
        "derived_train_rows": summary["derived_train_rows"],
        "derived_eval_rows": summary["derived_eval_rows"],
        "train_file": normalized_path(train_path),
        "eval_file": normalized_path(eval_path),
        "train_metadata_file": normalized_path(train_meta_path),
        "eval_metadata_file": normalized_path(eval_meta_path),
        "file_sizes_bytes": {
            "train_file": train_path.stat().st_size,
            "eval_file": eval_path.stat().st_size,
            "train_metadata_file": train_meta_path.stat().st_size,
            "eval_metadata_file": eval_meta_path.stat().st_size,
        },
        "hashes": {
            "train_file_sha256": sha256_file(train_path),
            "eval_file_sha256": sha256_file(eval_path),
            "train_metadata_file_sha256": sha256_file(train_meta_path),
            "eval_metadata_file_sha256": sha256_file(eval_meta_path),
        },
        "source_doc_distribution": summary["source_doc_distribution"],
        "split_chunk_overlap": [],
        "source_pre_gold_summary_sha256": sha256_file(source_pre_gold_summary),
        "source_pre_gold_manifest_sha256": sha256_file(source_pre_gold_manifest),
        "source_reviewed_path_sha256": sha256_file(source_reviewed_path),
    }


def write_notes(notes_path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Controlled Gold Derivation",
        "",
        "## Bottom Line",
        "",
        summary["decision"]["statement"],
        "",
        "## Included",
        "",
        f"- Derived train rows: {summary['derived_train_rows']}",
        f"- Derived eval rows: {summary['derived_eval_rows']}",
        "",
        "## Excluded",
        "",
        f"- Rejected source rows: {summary['rejected_rows']}",
        f"- Rejected clarification rows: {len(summary['sensitive_rest_areas']['clarification'])}",
        f"- Rejected step_by_step rows: {len(summary['sensitive_rest_areas']['step_by_step'])}",
        "",
        "## Interpretation",
        "",
        "- The gold stand is taken only from approved rows of the pre-gold candidate set.",
        "- `step_by_step` and `clarification` remain visible in the excluded source rows and are not silently promoted.",
        "- The derivation is offline and controlled; it is not a fresh review cycle.",
    ]
    notes_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> Any:
    parser = make_parser("Derive a controlled gold stand from the approved pre-gold candidate set.")
    parser.add_argument("--source-pre-gold-dir", default=str(DEFAULT_SOURCE_PRE_GOLD_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_GOLD_OUTPUT_DIR))
    parser.add_argument("--gold-train-output", default=str(DEFAULT_GOLD_TRAIN_OUTPUT))
    parser.add_argument("--gold-eval-output", default=str(DEFAULT_GOLD_EVAL_OUTPUT))
    parser.add_argument("--export-id", default="jaws_de_openrouter_gpt54_controlled_gold_v16")
    parser.add_argument("--summary-output")
    parser.add_argument("--manifest-output")
    parser.add_argument("--notes-output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    source_pre_gold_dir = repo_root / Path(args.source_pre_gold_dir)
    output_dir = repo_root / Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_pre_gold_summary = source_pre_gold_dir / "summary.json"
    source_pre_gold_manifest = source_pre_gold_dir / "manifest.json"
    source_pre_gold_train = source_pre_gold_dir / "train.jsonl"
    source_pre_gold_eval = source_pre_gold_dir / "eval.jsonl"
    if not source_pre_gold_summary.exists():
        raise SystemExit(f"Missing pre-gold summary: {source_pre_gold_summary.as_posix()}")
    if not source_pre_gold_manifest.exists():
        raise SystemExit(f"Missing pre-gold manifest: {source_pre_gold_manifest.as_posix()}")
    if not source_pre_gold_train.exists():
        raise SystemExit(f"Missing pre-gold train file: {source_pre_gold_train.as_posix()}")
    if not source_pre_gold_eval.exists():
        raise SystemExit(f"Missing pre-gold eval file: {source_pre_gold_eval.as_posix()}")

    source_pre_gold_summary_data = read_json(source_pre_gold_summary)
    source_reviewed_path = Path(source_pre_gold_summary_data["source_reviewed_path"])
    if not source_reviewed_path.is_absolute():
        source_reviewed_path = repo_root / source_reviewed_path
    if not source_reviewed_path.exists():
        raise SystemExit(f"Missing reviewed source: {source_reviewed_path.as_posix()}")

    train_selection = {row["id"] for row in read_jsonl(source_pre_gold_train)}
    eval_selection = {row["id"] for row in read_jsonl(source_pre_gold_eval)}
    reviewed_rows = read_jsonl(source_reviewed_path)

    selected_train: list[dict[str, Any]] = []
    selected_eval: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []

    for row in reviewed_rows:
        candidate = row.get("candidate")
        if not isinstance(candidate, dict):
            rejected_rows.append(row)
            continue
        if (row.get("auto_review") or {}).get("decision") != "approve" or row.get("review_status") != "codex_reviewed":
            rejected_rows.append(row)
            continue
        if row["record_type"] == "sft_sample" and candidate.get("id") in train_selection:
            selected_train.append(row)
        elif row["record_type"] == "eval_case" and candidate.get("eval_id") in eval_selection:
            selected_eval.append(row)
        else:
            rejected_rows.append(row)

    if len(selected_train) != len(train_selection):
        raise SystemExit(
            f"Train selection mismatch: expected {len(train_selection)} approved rows, got {len(selected_train)}"
        )
    if len(selected_eval) != len(eval_selection):
        raise SystemExit(
            f"Eval selection mismatch: expected {len(eval_selection)} approved rows, got {len(selected_eval)}"
        )

    gold_train_path = repo_root / Path(args.gold_train_output)
    gold_eval_path = repo_root / Path(args.gold_eval_output)
    gold_train_path.parent.mkdir(parents=True, exist_ok=True)
    gold_eval_path.parent.mkdir(parents=True, exist_ok=True)

    gold_train_rows: list[dict[str, Any]] = []
    gold_eval_rows: list[dict[str, Any]] = []
    train_meta_rows: list[dict[str, Any]] = []
    eval_meta_rows: list[dict[str, Any]] = []

    for row in selected_train:
        candidate = dict(row["candidate"])
        candidate["review_status"] = "promoted"
        candidate["split"] = "train"
        candidate["approved_by"] = row.get("approved_by")
        candidate["promoted_from"] = build_promoted_from(row, source_reviewed_path)
        candidate["meta"] = build_train_meta(
            candidate=candidate,
            gold_path=gold_train_path,
            source_pre_gold_dir=source_pre_gold_dir,
            source_pre_gold_summary=source_pre_gold_summary,
            source_pre_gold_manifest=source_pre_gold_manifest,
        )
        gold_train_rows.append(candidate)
        train_meta_rows.append(candidate["meta"])

    for row in selected_eval:
        candidate = dict(row["candidate"])
        candidate["review_status"] = "promoted"
        candidate["split"] = "eval"
        candidate["approved_by"] = row.get("approved_by")
        candidate["promoted_from"] = build_promoted_from(row, source_reviewed_path)
        gold_eval_rows.append(candidate)
        eval_meta_rows.append(
            build_eval_meta(
                candidate=candidate,
                gold_path=gold_eval_path,
                source_pre_gold_dir=source_pre_gold_dir,
                source_pre_gold_summary=source_pre_gold_summary,
                source_pre_gold_manifest=source_pre_gold_manifest,
            )
        )

    train_path = gold_train_path
    eval_path = gold_eval_path
    train_meta_path = output_dir / "train.metadata.jsonl"
    eval_meta_path = output_dir / "eval.metadata.jsonl"
    summary_path = output_dir / "summary.json"
    manifest_path = output_dir / "manifest.json"
    notes_path = output_dir / "notes.md"

    write_jsonl(train_path, gold_train_rows)
    write_jsonl(eval_path, gold_eval_rows)
    write_jsonl(train_meta_path, train_meta_rows)
    write_jsonl(eval_meta_path, eval_meta_rows)

    summary = build_summary(
        export_id=args.export_id,
        source_pre_gold_dir=source_pre_gold_dir,
        source_pre_gold_summary=source_pre_gold_summary,
        source_pre_gold_manifest=source_pre_gold_manifest,
        source_reviewed_path=source_reviewed_path,
        train_rows=gold_train_rows,
        eval_rows=gold_eval_rows,
        rejected_rows=rejected_rows,
        output_dir=output_dir,
    )
    write_json(summary_path, summary)

    manifest = build_manifest(
        export_id=args.export_id,
        output_dir=output_dir,
        source_pre_gold_dir=source_pre_gold_dir,
        source_pre_gold_summary=source_pre_gold_summary,
        source_pre_gold_manifest=source_pre_gold_manifest,
        source_reviewed_path=source_reviewed_path,
        train_path=train_path,
        eval_path=eval_path,
        train_meta_path=train_meta_path,
        eval_meta_path=eval_meta_path,
        summary=summary,
    )
    write_json(manifest_path, manifest)
    write_notes(notes_path, summary)

    print(
        f"Derived {len(gold_train_rows)} gold train and {len(gold_eval_rows)} gold eval rows "
        f"to {output_dir.as_posix()}"
    )


if __name__ == "__main__":
    main()

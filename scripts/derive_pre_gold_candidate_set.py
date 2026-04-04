from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import find_repo_root, make_parser, read_json, read_jsonl, sha256_file, write_json, write_jsonl

DEFAULT_SOURCE_REVIEWED = (
    "data/derived/teacher_outputs/JAWS/DE/"
    "jaws_de_shadow_2026_04_04_user_answer_v16_openrouter_gpt54_curated_pre_gold_wave_reviewed_teacher_outputs.jsonl"
)
DEFAULT_OUTPUT_DIR = Path("data/derived/pre_gold/JAWS/DE/openrouter_gpt54_curated_pre_gold_v16")
EXPORT_PIPELINE_VERSION = "0.1.0"


def parse_args() -> Any:
    parser = make_parser("Derive a controlled pre-gold candidate set from approved OpenRouter pre-gold reviews.")
    parser.add_argument("--source-reviewed", default=DEFAULT_SOURCE_REVIEWED)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--export-id", default="jaws_de_openrouter_gpt54_curated_pre_gold_v16")
    parser.add_argument("--summary-output")
    parser.add_argument("--manifest-output")
    parser.add_argument("--notes-output")
    return parser.parse_args()


def normalized_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def load_behavior_spec(repo_root: Path, path_str: str | None) -> str:
    if not path_str:
        return ""
    path = Path(path_str)
    if not path.is_absolute():
        path = repo_root / path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def approved_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    approved: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for row in rows:
        if ((row.get("auto_review") or {}).get("decision") == "approve") and row.get("review_status") == "codex_reviewed":
            approved.append(row)
        else:
            rejected.append(row)
    return approved, rejected


def export_train_row(candidate: dict[str, Any]) -> dict[str, Any]:
    messages = candidate["messages"]
    if not isinstance(messages, list) or len(messages) < 2:
        raise SystemExit(f"{candidate['id']} has no exportable messages")
    if messages[-1]["role"] != "assistant":
        raise SystemExit(f"{candidate['id']} does not end with assistant")
    if not messages[-1]["content"].strip():
        raise SystemExit(f"{candidate['id']} has empty assistant message")
    return {"id": candidate["id"], "messages": messages}


def export_eval_row(repo_root: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    behavior_spec = load_behavior_spec(repo_root, candidate.get("provenance", {}).get("behavior_spec_path"))
    messages = []
    if behavior_spec:
        messages.append({"role": "system", "content": behavior_spec})
    messages.append({"role": "user", "content": candidate["prompt"]})
    messages.append({"role": "assistant", "content": candidate["reference_answer"]})
    if not messages[-1]["content"].strip():
        raise SystemExit(f"{candidate['eval_id']} has empty reference answer")
    return {"id": candidate["eval_id"], "messages": messages}


def metadata_row(
    *,
    candidate: dict[str, Any],
    source_path: Path,
    split: str,
    record_type: str,
    exported_id: str,
) -> dict[str, Any]:
    meta = {
        "id": exported_id,
        "split": split,
        "record_type": record_type,
        "product": candidate.get("product"),
        "language": candidate.get("language"),
        "task_type": candidate.get("task_type"),
        "case_type": candidate.get("case_type"),
        "source_doc_ids": candidate.get("source_doc_ids", []),
        "source_chunk_ids": candidate.get("source_chunk_ids", []),
        "teacher_model": candidate.get("teacher_model"),
        "teacher_run_id": candidate.get("teacher_run_id"),
        "teacher_prompt_version": candidate.get("teacher_prompt_version"),
        "generation_mode": candidate.get("generation_mode"),
        "review_status": "human_reviewed",
        "approved_by": candidate.get("approved_by"),
        "gold_source_path": source_path.as_posix(),
        "promoted_from": None,
        "provenance": candidate.get("provenance", {}),
        "expected_behavior": candidate.get("expected_behavior"),
        "reference_answer": candidate.get("reference_answer"),
        "rubric": candidate.get("rubric"),
        "candidate_source_path": source_path.as_posix(),
        "candidate_selection_status": "approved_only",
    }
    return meta


def build_summary(
    *,
    export_id: str,
    source_reviewed_path: Path,
    output_dir: Path,
    approved: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    eval_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    approved_task_counts = Counter(row["task_type"] for row in approved)
    approved_split_counts = Counter(row["record_type"] for row in approved)
    approved_doc_counts = Counter(doc_id for row in approved for doc_id in row.get("source_doc_ids", []))
    rejected_task_counts = Counter(row["task_type"] for row in rejected)
    rejected_decisions = Counter((row.get("auto_review") or {}).get("decision") for row in rejected)

    excluded_rows = [
        {
            "job_id": row["job_id"],
            "task_type": row["task_type"],
            "record_type": row["record_type"],
            "decision": (row.get("auto_review") or {}).get("decision"),
            "quality_score": row.get("auto_review", {}).get("quality_score"),
            "summary": row.get("auto_review", {}).get("summary"),
        }
        for row in rejected
    ]
    return {
        "export_id": export_id,
        "source_reviewed_path": normalized_path(source_reviewed_path),
        "output_dir": normalized_path(output_dir),
        "export_generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "export_pipeline_version": EXPORT_PIPELINE_VERSION,
        "approved_rows": len(approved),
        "rejected_rows": len(rejected),
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "approved_task_type_counts": dict(sorted(approved_task_counts.items())),
        "approved_record_type_counts": dict(sorted(approved_split_counts.items())),
        "source_doc_distribution": dict(sorted(approved_doc_counts.items())),
        "rejected_task_type_counts": dict(sorted(rejected_task_counts.items())),
        "rejected_decision_counts": dict(sorted(rejected_decisions.items())),
        "excluded_rows": excluded_rows,
        "sensitive_rest_areas": {
            "step_by_step": [
                row for row in excluded_rows if row["task_type"] == "step_by_step"
            ],
            "clarification": [
                row for row in excluded_rows if row["task_type"] == "clarification"
            ],
        },
        "decision": {
            "status": "candidate_only",
            "no_gold_promotion": True,
            "statement": (
                "This output set is a pre-gold candidate derived only from approved rows in the v16 curated wave. "
                "Rejected clarification and step_by_step rows remain excluded and visible in the summary."
            ),
        },
        "source_hash": sha256_file(source_reviewed_path),
    }


def build_manifest(
    *,
    export_id: str,
    output_dir: Path,
    source_reviewed_path: Path,
    train_path: Path,
    eval_path: Path,
    train_meta_path: Path,
    eval_meta_path: Path,
    summary: dict[str, Any],
) -> dict[str, Any]:
    manifest = {
        "export_id": export_id,
        "export_generated_at_utc": summary["export_generated_at_utc"],
        "format": "qwen_openai_messages",
        "export_pipeline_version": EXPORT_PIPELINE_VERSION,
        "output_dir": normalized_path(output_dir),
        "source_reviewed_path": normalized_path(source_reviewed_path),
        "approved_rows": summary["approved_rows"],
        "rejected_rows": summary["rejected_rows"],
        "train_records": summary["train_rows"],
        "eval_records": summary["eval_rows"],
        "train_metadata_records": summary["train_rows"],
        "eval_metadata_records": summary["eval_rows"],
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
        "split_chunk_overlap": [],
        "source_reviewed_path_sha256": summary["source_hash"],
        "source_doc_distribution": summary["source_doc_distribution"],
    }
    return manifest


def write_notes(notes_path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Pre-Gold Candidate Derivation",
        "",
        "## Bottom Line",
        "",
        summary["decision"]["statement"],
        "",
        "## Included",
        "",
        f"- Approved rows: {summary['approved_rows']}",
        f"- Train rows: {summary['train_rows']}",
        f"- Eval rows: {summary['eval_rows']}",
        "",
        "## Excluded",
        "",
        f"- Rejected rows: {summary['rejected_rows']}",
        f"- Rejected clarification rows: {len(summary['sensitive_rest_areas']['clarification'])}",
        f"- Rejected step_by_step rows: {len(summary['sensitive_rest_areas']['step_by_step'])}",
        "",
        "## Interpretation",
        "",
        "- `faq_direct_answer`, `troubleshooting`, and `uncertainty_escalation` are fully green in the source wave.",
        "- `step_by_step` remains the only broader residual risk, and the excluded rows keep that risk visible.",
        "- The output set is suitable as a controlled pre-gold candidate pool, not as a promoted gold freeze.",
    ]
    notes_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    source_reviewed_path = repo_root / args.source_reviewed
    output_dir = repo_root / Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    reviewed_rows = read_jsonl(source_reviewed_path)
    approved, rejected = approved_rows(reviewed_rows)
    if not approved:
        raise SystemExit("No approved rows found in source reviewed outputs")

    train_candidates = [row["candidate"] for row in approved if row["record_type"] == "sft_sample"]
    eval_candidates = [row["candidate"] for row in approved if row["record_type"] == "eval_case"]

    train_export_rows = [export_train_row(candidate) for candidate in train_candidates]
    eval_export_rows = [export_eval_row(repo_root, candidate) for candidate in eval_candidates]
    train_metadata_rows = [
        metadata_row(
            candidate=candidate,
            source_path=source_reviewed_path,
            split="train",
            record_type="sft_train",
            exported_id=candidate["id"],
        )
        for candidate in train_candidates
    ]
    eval_metadata_rows = [
        metadata_row(
            candidate=candidate,
            source_path=source_reviewed_path,
            split="eval",
            record_type="sft_eval",
            exported_id=candidate["eval_id"],
        )
        for candidate in eval_candidates
    ]

    train_path = output_dir / "train.jsonl"
    eval_path = output_dir / "eval.jsonl"
    train_meta_path = output_dir / "train.metadata.jsonl"
    eval_meta_path = output_dir / "eval.metadata.jsonl"
    summary_path = output_dir / "summary.json"
    manifest_path = output_dir / "manifest.json"
    notes_path = output_dir / "notes.md"

    write_jsonl(train_path, train_export_rows)
    write_jsonl(eval_path, eval_export_rows)
    write_jsonl(train_meta_path, train_metadata_rows)
    write_jsonl(eval_meta_path, eval_metadata_rows)

    summary = build_summary(
        export_id=args.export_id,
        source_reviewed_path=source_reviewed_path,
        output_dir=output_dir,
        approved=approved,
        rejected=rejected,
        train_rows=train_export_rows,
        eval_rows=eval_export_rows,
    )
    write_json(summary_path, summary)

    manifest = build_manifest(
        export_id=args.export_id,
        output_dir=output_dir,
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
        f"Derived {len(train_export_rows)} train and {len(eval_export_rows)} eval candidate rows "
        f"to {output_dir.as_posix()}"
    )


if __name__ == "__main__":
    main()

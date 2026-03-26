from __future__ import annotations

import argparse
import json
import mimetypes
import os
import tempfile
import webbrowser
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from jsonschema import Draft202012Validator

from common import find_repo_root, read_json, read_jsonl, sha256_file
from promote_teacher_outputs import promote_eval, promote_sft


@dataclass(frozen=True)
class FileClass:
    category: str
    editable: bool
    schema_name: str | None
    label: str


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = find_repo_root(SCRIPT_DIR)
UI_ROOT = REPO_ROOT / "tools" / "jsonl_editor"
SCHEMA_DIR = REPO_ROOT / "schemas"
EDITABLE_ROOTS = [
    REPO_ROOT / "data" / "derived" / "teacher_outputs",
    REPO_ROOT / "data" / "gold" / "train",
    REPO_ROOT / "data" / "gold" / "eval",
]

FILE_CLASSIFICATIONS: list[tuple[str, FileClass]] = [
    (
        "data/derived/teacher_outputs/",
        FileClass("teacher_outputs", True, "teacher_output.schema.json", "Teacher Outputs"),
    ),
    ("data/gold/train/", FileClass("gold_train", True, "sft_sample.schema.json", "Gold Train")),
    ("data/gold/eval/", FileClass("gold_eval", True, "eval_case.schema.json", "Gold Eval")),
    ("data/exports/", FileClass("exports", False, None, "Exports")),
    ("data/derived/chunks/", FileClass("chunks", False, "chunk.schema.json", "Chunks")),
    ("data/derived/task_cards/", FileClass("task_cards", False, "task_card.schema.json", "Task Cards")),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local JSONL review editor.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open-browser", action="store_true")
    return parser.parse_args()


def repo_relative_posix(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def file_class_for_path(path: Path) -> FileClass | None:
    if path.suffix != ".jsonl":
        return None
    rel = repo_relative_posix(path)
    for prefix, info in FILE_CLASSIFICATIONS:
        if rel.startswith(prefix):
            if prefix == "data/derived/teacher_outputs/":
                if rel.endswith("_raw_responses.jsonl"):
                    return FileClass("raw_responses", False, None, "Raw Responses")
                if "reviewed" in path.name:
                    return FileClass(
                        "reviewed_teacher_outputs",
                        True,
                        "teacher_output.schema.json",
                        "Reviewed Teacher Outputs",
                    )
                if rel.endswith("teacher_outputs.jsonl"):
                    return info
                return FileClass("teacher_preview", False, None, "Teacher Previews")
            return info
    return None


def ensure_safe_repo_path(path_str: str) -> Path:
    candidate = (REPO_ROOT / path_str).resolve()
    if not candidate.is_relative_to(REPO_ROOT):
        raise ValueError("Path escapes repository root")
    return candidate


def ensure_editable_path(path_str: str) -> tuple[Path, FileClass]:
    path = ensure_safe_repo_path(path_str)
    info = file_class_for_path(path)
    if info is None or not info.editable:
        raise ValueError("Path is not editable in the editor")
    return path, info


def ensure_readable_source_path(path_str: str) -> Path:
    path = ensure_safe_repo_path(path_str)
    allowed_roots = EDITABLE_ROOTS + [
        REPO_ROOT / "data" / "normalized",
        REPO_ROOT / "data" / "exports",
        REPO_ROOT / "data" / "derived" / "chunks",
        REPO_ROOT / "data" / "derived" / "task_cards",
    ]
    if not any(path.is_relative_to(root) for root in allowed_roots):
        raise ValueError("Path is not readable in the editor")
    return path


def load_validator(schema_name: str) -> Draft202012Validator:
    return Draft202012Validator(read_json(SCHEMA_DIR / schema_name))


VALIDATORS = {
    "teacher_output.schema.json": load_validator("teacher_output.schema.json"),
    "sft_sample.schema.json": load_validator("sft_sample.schema.json"),
    "eval_case.schema.json": load_validator("eval_case.schema.json"),
    "chunk.schema.json": load_validator("chunk.schema.json"),
    "task_card.schema.json": load_validator("task_card.schema.json"),
}
REVIEW_CATEGORIES = {"teacher_outputs", "reviewed_teacher_outputs"}
PROMOTION_CATEGORIES = {"reviewed_teacher_outputs"}


def list_jsonl_files(include_read_only: bool) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted((REPO_ROOT / "data").rglob("*.jsonl")):
        info = file_class_for_path(path)
        if info is None:
            continue
        if not include_read_only and not info.editable:
            continue
        row_count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        files.append(
            {
                "path": repo_relative_posix(path),
                "category": info.category,
                "label": info.label,
                "editable": info.editable,
                "rows": row_count,
            }
        )
    return files


def derive_row_id(row: dict[str, Any]) -> str:
    for key in ("output_id", "id", "eval_id", "chunk_id", "task_card_id"):
        value = row.get(key)
        if value:
            return str(value)
    return "<unknown>"


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = row.get("review_status") or "<none>"
        counts[status] = counts.get(status, 0) + 1
    return counts


def suggested_review_output_path(path: Path) -> str:
    info = file_class_for_path(path)
    if info and info.category == "reviewed_teacher_outputs":
        return repo_relative_posix(path)

    name = path.name
    if "_teacher_outputs.jsonl" in name:
        output_name = name.replace("_teacher_outputs.jsonl", "_reviewed_teacher_outputs.jsonl")
    elif name.endswith(".jsonl"):
        output_name = f"{path.stem}_reviewed.jsonl"
    else:
        output_name = name
    return repo_relative_posix(path.with_name(output_name))


def strip_review_suffix(stem: str) -> str:
    for suffix in ("_reviewed_teacher_outputs", "_reviewed_outputs", "_teacher_outputs"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def suggested_gold_output_paths(path: Path) -> dict[str, str]:
    relative_parent = path.parent.relative_to(REPO_ROOT / "data" / "derived" / "teacher_outputs")
    stem = strip_review_suffix(path.stem)
    train_path = (
        REPO_ROOT / "data" / "gold" / "train" / "sft" / relative_parent / f"promoted_{stem}_sft_samples.jsonl"
    )
    eval_path = REPO_ROOT / "data" / "gold" / "eval" / relative_parent / f"promoted_{stem}_eval_cases.jsonl"
    return {
        "train_output_path": repo_relative_posix(train_path),
        "eval_output_path": repo_relative_posix(eval_path),
    }


def build_review_context(path: Path, rows: list[dict[str, Any]], info: FileClass | None) -> dict[str, Any] | None:
    if info is None or info.category not in REVIEW_CATEGORIES:
        return None

    counts = status_counts(rows)
    pending_count = sum(counts.get(status, 0) for status in ("draft", "seed", "teacher_generated"))
    decided_count = sum(counts.get(status, 0) for status in ("human_reviewed", "rejected"))
    suggested_output = suggested_review_output_path(path)
    suggested_output_path = ensure_safe_repo_path(suggested_output)
    existing_output_exists = suggested_output_path.exists()
    existing_rows = read_jsonl(suggested_output_path) if existing_output_exists else []
    existing_counts = status_counts(existing_rows) if existing_output_exists else {}
    merge_summary = summarize_review_merge(rows, existing_rows) if existing_output_exists else None
    return {
        "enabled": True,
        "default_status_filter": "teacher_generated" if info.category == "teacher_outputs" else "",
        "suggested_output_path": suggested_output,
        "existing_output_exists": existing_output_exists,
        "existing_output_path": suggested_output if existing_output_exists else None,
        "existing_status_counts": existing_counts,
        "existing_merge_summary": merge_summary,
        "status_counts": counts,
        "pending_count": pending_count,
        "decided_count": decided_count,
    }


def build_promotion_context(path: Path, rows: list[dict[str, Any]], info: FileClass | None) -> dict[str, Any] | None:
    if info is None or info.category not in PROMOTION_CATEGORIES:
        return None

    suggested = suggested_gold_output_paths(path)
    human_reviewed = [row for row in rows if row.get("review_status") == "human_reviewed"]
    train_count = sum(1 for row in human_reviewed if row.get("record_type") == "sft_sample")
    eval_count = sum(1 for row in human_reviewed if row.get("record_type") == "eval_case")
    return {
        "enabled": True,
        "train_output_path": suggested["train_output_path"],
        "eval_output_path": suggested["eval_output_path"],
        "eligible_count": len(human_reviewed),
        "train_count": train_count,
        "eval_count": eval_count,
    }


def schema_name_for_row(row: dict[str, Any], fallback: str | None) -> str | None:
    if "output_id" in row and "candidate" in row:
        return "teacher_output.schema.json"
    if "messages" in row and "meta" in row:
        return "sft_sample.schema.json"
    if "prompt" in row and "source_doc_ids" in row:
        return "eval_case.schema.json"
    return fallback


def minimal_provenance_errors(row: dict[str, Any], index: int) -> list[str]:
    failures: list[str] = []
    provenance = row.get("provenance", {})
    has_source_records = bool(provenance.get("source_records"))

    if "messages" in row and "meta" in row:
        meta = row["meta"]
        if not meta.get("source_doc_ids"):
            failures.append(f"Row {index}: missing meta.source_doc_ids")
        if not meta.get("review_status"):
            failures.append(f"Row {index}: missing meta.review_status")
        if not has_source_records:
            failures.append(f"Row {index}: missing provenance.source_records")
        return failures

    if "prompt" in row and "source_doc_ids" in row:
        if not row.get("source_doc_ids"):
            failures.append(f"Row {index}: missing source_doc_ids")
        if not row.get("review_status"):
            failures.append(f"Row {index}: missing review_status")
        if not has_source_records:
            failures.append(f"Row {index}: missing provenance.source_records")
        return failures

    if "output_id" in row and "candidate" in row:
        if not row.get("source_doc_ids"):
            failures.append(f"Row {index}: missing source_doc_ids")
        if not row.get("source_chunk_ids"):
            failures.append(f"Row {index}: missing source_chunk_ids")
        if not row.get("review_status"):
            failures.append(f"Row {index}: missing review_status")
        if not has_source_records:
            failures.append(f"Row {index}: missing provenance.source_records")
        return failures

    if "gold_source_path" in row:
        if not row.get("source_doc_ids"):
            failures.append(f"Row {index}: missing source_doc_ids")
        if not row.get("review_status"):
            failures.append(f"Row {index}: missing review_status")
        if not has_source_records:
            failures.append(f"Row {index}: missing provenance.source_records")
        return failures

    for key in ("doc_id", "source_spans", "review_status"):
        if row.get(key) in (None, "", []):
            failures.append(f"Row {index}: missing {key}")
    return failures


def schema_errors_for_rows(rows: list[dict[str, Any]], fallback_schema: str | None) -> list[str]:
    errors: list[str] = []
    sft_validator = VALIDATORS["sft_sample.schema.json"]
    eval_validator = VALIDATORS["eval_case.schema.json"]

    for index, row in enumerate(rows, start=1):
        schema_name = schema_name_for_row(row, fallback_schema)
        if schema_name:
            validator = VALIDATORS.get(schema_name)
            if validator is None:
                errors.append(f"Row {index}: no validator for {schema_name}")
            else:
                for issue in validator.iter_errors(row):
                    errors.append(f"Row {index}: {issue.message}")

        if "output_id" in row and isinstance(row.get("candidate"), dict):
            candidate = row["candidate"]
            record_type = row.get("record_type")
            candidate_validator = sft_validator if record_type == "sft_sample" else eval_validator
            for issue in candidate_validator.iter_errors(candidate):
                errors.append(f"Row {index} candidate: {issue.message}")

    return errors


def provenance_errors_for_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        errors.extend(minimal_provenance_errors(row, index))
    return errors


def normalize_row_for_save(row: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(row))

    if "output_id" in normalized and isinstance(normalized.get("candidate"), dict):
        candidate = normalized["candidate"]
        if normalized.get("review_status"):
            candidate["review_status"] = normalized["review_status"]
        if "approved_by" in normalized:
            candidate["approved_by"] = normalized.get("approved_by")
        if isinstance(candidate.get("meta"), dict):
            if normalized.get("review_status"):
                candidate["meta"]["review_status"] = normalized["review_status"]
            if "approved_by" in normalized:
                candidate["meta"]["approved_by"] = normalized.get("approved_by")
        return normalized

    if "messages" in normalized and isinstance(normalized.get("meta"), dict):
        meta = normalized["meta"]
        for key in ("review_status", "approved_by", "split", "promoted_from"):
            if key in normalized:
                meta[key] = normalized.get(key)
        return normalized

    return normalized


def review_merge_signature(row: dict[str, Any]) -> dict[str, Any]:
    candidate = row.get("candidate", {})
    return {
        "job_id": row.get("job_id"),
        "record_type": row.get("record_type"),
        "target_split": row.get("target_split"),
        "task_type": row.get("task_type"),
        "source_doc_ids": row.get("source_doc_ids"),
        "source_chunk_ids": row.get("source_chunk_ids"),
        "candidate_id": candidate.get("id") or candidate.get("eval_id"),
        "candidate_source_doc_ids": candidate.get("source_doc_ids"),
        "candidate_source_chunk_ids": candidate.get("source_chunk_ids"),
    }


def summarize_review_merge(source_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_by_id = {row["output_id"]: row for row in source_rows}
    reviewed_by_id = {row["output_id"]: row for row in reviewed_rows}

    missing_ids = sorted(set(source_by_id) - set(reviewed_by_id))
    extra_ids = sorted(set(reviewed_by_id) - set(source_by_id))
    conflicting_ids = sorted(
        output_id
        for output_id in (set(source_by_id) & set(reviewed_by_id))
        if review_merge_signature(source_by_id[output_id]) != review_merge_signature(reviewed_by_id[output_id])
    )
    mergeable_ids = sorted((set(source_by_id) & set(reviewed_by_id)) - set(conflicting_ids))
    return {
        "source_count": len(source_rows),
        "reviewed_count": len(reviewed_rows),
        "mergeable_count": len(mergeable_ids),
        "missing_count": len(missing_ids),
        "extra_count": len(extra_ids),
        "conflict_count": len(conflicting_ids),
        "missing_ids_preview": missing_ids[:10],
        "extra_ids_preview": extra_ids[:10],
        "conflict_ids_preview": conflicting_ids[:10],
    }


def merge_reviewed_overlay(source_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_by_id = {row["output_id"]: row for row in source_rows}
    reviewed_by_id = {row["output_id"]: row for row in reviewed_rows}
    summary = summarize_review_merge(source_rows, reviewed_rows)

    rows: list[dict[str, Any]] = []
    merged_count = 0
    for source_row in source_rows:
        output_id = source_row["output_id"]
        overlay = reviewed_by_id.get(output_id)
        if overlay is None or review_merge_signature(source_row) != review_merge_signature(overlay):
            rows.append(json.loads(json.dumps(source_row)))
            continue

        merged_count += 1
        merged = json.loads(json.dumps(source_row))
        merged["review_status"] = overlay.get("review_status")
        merged["approved_by"] = overlay.get("approved_by")
        if "promoted_to" in overlay:
            merged["promoted_to"] = overlay.get("promoted_to")
        if overlay.get("candidate"):
            merged["candidate"] = json.loads(json.dumps(overlay["candidate"]))
        rows.append(merged)

    summary["merged_count"] = merged_count
    return rows, summary


def gold_post_checks(path: Path, rows: list[dict[str, Any]], schema_name: str) -> dict[str, Any]:
    if not rows:
        return {
            "path": repo_relative_posix(path),
            "rows": 0,
            "schema_ok": True,
            "provenance_ok": True,
            "messages": ["schema skipped (0 rows)", "provenance skipped (0 rows)"],
            "errors": [],
        }

    schema_errors = schema_errors_for_rows(rows, schema_name)
    provenance_errors = provenance_errors_for_rows(rows)
    messages = []
    if not schema_errors:
        messages.append(f"schema ok ({len(rows)} rows)")
    if not provenance_errors:
        messages.append(f"provenance ok ({len(rows)} rows)")
    return {
        "path": repo_relative_posix(path),
        "rows": len(rows),
        "schema_ok": not schema_errors,
        "provenance_ok": not provenance_errors,
        "messages": messages,
        "errors": schema_errors + provenance_errors,
    }


def validate_rows(path: Path, rows: list[dict[str, Any]], fallback_schema: str | None) -> list[str]:
    errors = schema_errors_for_rows(rows, fallback_schema)
    errors.extend(provenance_errors_for_rows(rows))

    if not rows:
        errors.append(f"{repo_relative_posix(path)} is empty")

    return errors


def atomic_write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f"{path.stem}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temp_path = Path(handle.name)
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(temp_path, path)


def load_jsonl_payload(path: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    info = file_class_for_path(path)
    schema_name = info.schema_name if info else None
    return {
        "path": repo_relative_posix(path),
        "category": info.category if info else "unknown",
        "editable": info.editable if info else False,
        "schema": schema_name,
        "hash": sha256_file(path),
        "rows": rows,
        "review": build_review_context(path, rows, info),
        "promotion": build_promotion_context(path, rows, info),
        "validation_errors": validate_rows(path, rows, schema_name),
    }


def validate_review_export(
    source_path: Path,
    output_path: Path,
    rows: list[dict[str, Any]],
    source_info: FileClass,
) -> list[str]:
    errors: list[str] = []
    if source_info.category not in REVIEW_CATEGORIES:
        errors.append("Review export is only supported for teacher output files.")
        return errors

    if source_info.category == "teacher_outputs" and output_path == source_path:
        errors.append("Teacher output sources must be exported to a reviewed output path.")

    output_info = file_class_for_path(output_path)
    if output_info is None or output_info.category not in REVIEW_CATEGORIES:
        errors.append("Reviewed output path must stay under data/derived/teacher_outputs and include a reviewed filename.")
        return errors

    counts = status_counts(rows)
    decided_count = counts.get("human_reviewed", 0) + counts.get("rejected", 0)
    if decided_count == 0:
        errors.append("No review decisions found; set at least one row to human_reviewed or rejected.")

    for index, row in enumerate(rows, start=1):
        status = row.get("review_status")
        if status in {"human_reviewed", "rejected"} and not row.get("approved_by"):
            errors.append(f"Row {index}: approved_by is required for reviewed decisions")

    errors.extend(validate_rows(output_path, rows, output_info.schema_name))
    return errors


def build_promoted_rows(input_path: str, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    approved = [row for row in rows if row.get("review_status") == "human_reviewed"]
    if not approved:
        raise ValueError("No human_reviewed teacher outputs found to promote")

    train_rows: list[dict[str, Any]] = []
    eval_rows: list[dict[str, Any]] = []
    train_chunk_ids: set[str] = set()
    eval_chunk_ids: set[str] = set()
    promoted_output_ids: set[str] = set()

    for row in approved:
        if row["output_id"] in promoted_output_ids:
            raise ValueError(f"Duplicate promoted output_id {row['output_id']}")
        promoted_output_ids.add(row["output_id"])

        source_chunk_ids = set(row.get("source_chunk_ids", []))
        if row["record_type"] == "sft_sample":
            if source_chunk_ids & eval_chunk_ids:
                raise ValueError(f"Train/eval chunk overlap during promotion: {row['output_id']}")
            train_chunk_ids.update(source_chunk_ids)
            train_rows.append(promote_sft(row, input_path))
        elif row["record_type"] == "eval_case":
            if source_chunk_ids & train_chunk_ids:
                raise ValueError(f"Train/eval chunk overlap during promotion: {row['output_id']}")
            eval_chunk_ids.update(source_chunk_ids)
            eval_rows.append(promote_eval(row, input_path))
        else:
            raise ValueError(f"Unknown record_type {row['record_type']}")

    return train_rows, eval_rows


def validate_promotion_export(
    source_path: Path,
    train_output_path: Path,
    eval_output_path: Path,
    rows: list[dict[str, Any]],
    source_info: FileClass,
) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[str] = []
    train_rows: list[dict[str, Any]] = []
    eval_rows: list[dict[str, Any]] = []

    if source_info.category not in PROMOTION_CATEGORIES:
        errors.append("Promotion is only supported for reviewed teacher output files.")
        return errors, train_rows, eval_rows

    train_info = file_class_for_path(train_output_path)
    eval_info = file_class_for_path(eval_output_path)
    if train_info is None or train_info.category != "gold_train":
        errors.append("Train output path must stay under data/gold/train and end with .jsonl.")
    if eval_info is None or eval_info.category != "gold_eval":
        errors.append("Eval output path must stay under data/gold/eval and end with .jsonl.")
    if errors:
        return errors, train_rows, eval_rows

    try:
        train_rows, eval_rows = build_promoted_rows(repo_relative_posix(source_path), rows)
    except ValueError as exc:
        errors.append(str(exc))
        return errors, train_rows, eval_rows

    if train_rows:
        errors.extend(validate_rows(train_output_path, train_rows, "sft_sample.schema.json"))
    if eval_rows:
        errors.extend(validate_rows(eval_output_path, eval_rows, "eval_case.schema.json"))
    return errors, train_rows, eval_rows


def extract_source_excerpt(path: Path, start: int, end: int, context: int) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    line_count = len(lines)
    start = max(1, start)
    end = min(line_count, max(start, end))
    excerpt_start = max(1, start - context)
    excerpt_end = min(line_count, end + context)
    excerpt = [
        {"number": line_no, "text": lines[line_no - 1]}
        for line_no in range(excerpt_start, excerpt_end + 1)
    ]
    return {
        "path": repo_relative_posix(path),
        "line_count": line_count,
        "start": start,
        "end": end,
        "excerpt_start": excerpt_start,
        "excerpt_end": excerpt_end,
        "lines": excerpt,
    }


class EditorRequestHandler(BaseHTTPRequestHandler):
    server_version = "JSONLEditor/0.1"

    def do_GET(self) -> None:
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/api/files":
                include_read_only = parse_qs(parsed.query).get("all", ["0"])[0] == "1"
                self.send_json({"files": list_jsonl_files(include_read_only)})
                return

            if parsed.path == "/api/file":
                query = parse_qs(parsed.query)
                path = ensure_safe_repo_path(require_query_value(query, "path"))
                self.send_json(load_jsonl_payload(path))
                return

            if parsed.path == "/api/source":
                query = parse_qs(parsed.query)
                path = ensure_readable_source_path(require_query_value(query, "path"))
                start = int(query.get("start", ["1"])[0])
                end = int(query.get("end", [str(start)])[0])
                context = int(query.get("context", ["2"])[0])
                self.send_json(extract_source_excerpt(path, start, end, context))
                return

            if parsed.path == "/api/review-overlay":
                query = parse_qs(parsed.query)
                source_path = ensure_safe_repo_path(require_query_value(query, "source_path"))
                reviewed_path = ensure_safe_repo_path(require_query_value(query, "reviewed_path"))
                merged_rows, merge_summary = merge_reviewed_overlay(read_jsonl(source_path), read_jsonl(reviewed_path))
                self.send_json({"rows": merged_rows, "merge_summary": merge_summary})
                return

            if parsed.path in ("/", "/index.html"):
                self.serve_static("index.html")
                return

            self.serve_static(parsed.path.lstrip("/"))
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            payload = self.read_json_body()

            if parsed.path == "/api/validate":
                path = ensure_safe_repo_path(str(payload.get("path", "")))
                info = file_class_for_path(path)
                rows = [normalize_row_for_save(row) for row in payload.get("rows", [])]
                errors = validate_rows(path, rows, info.schema_name if info else None)
                self.send_json({"ok": not errors, "errors": errors})
                return

            if parsed.path == "/api/save":
                path, info = ensure_editable_path(str(payload.get("path", "")))
                rows = [normalize_row_for_save(row) for row in payload.get("rows", [])]
                base_hash = payload.get("base_hash")
                if base_hash and path.exists() and sha256_file(path) != base_hash:
                    self.send_json(
                        {"ok": False, "errors": ["File changed on disk; reload before saving."]},
                        status=HTTPStatus.CONFLICT,
                    )
                    return

                if info.category.startswith("gold") and not payload.get("allow_gold_write"):
                    self.send_json(
                        {"ok": False, "errors": ["Gold writes require explicit confirmation."]},
                        status=HTTPStatus.BAD_REQUEST,
                    )
                    return

                errors = validate_rows(path, rows, info.schema_name)
                if errors:
                    self.send_json({"ok": False, "errors": errors}, status=HTTPStatus.BAD_REQUEST)
                    return

                atomic_write_jsonl(path, rows)
                self.send_json({"ok": True, "hash": sha256_file(path)})
                return

            if parsed.path == "/api/save-reviewed":
                path, info = ensure_editable_path(str(payload.get("path", "")))
                rows = [normalize_row_for_save(row) for row in payload.get("rows", [])]
                output_path_str = str(payload.get("output_path") or suggested_review_output_path(path))
                output_path = ensure_safe_repo_path(output_path_str)
                base_hash = payload.get("base_hash")

                if base_hash and path.exists() and sha256_file(path) != base_hash:
                    self.send_json(
                        {"ok": False, "errors": ["Source file changed on disk; reload before exporting review results."]},
                        status=HTTPStatus.CONFLICT,
                    )
                    return

                if output_path.exists() and output_path != path and not payload.get("overwrite_output"):
                    self.send_json(
                        {"ok": False, "errors": [f"Reviewed output already exists: {repo_relative_posix(output_path)}"]},
                        status=HTTPStatus.CONFLICT,
                    )
                    return

                errors = validate_review_export(path, output_path, rows, info)
                if errors:
                    self.send_json({"ok": False, "errors": errors}, status=HTTPStatus.BAD_REQUEST)
                    return

                atomic_write_jsonl(output_path, rows)
                self.send_json(
                    {
                        "ok": True,
                        "output_path": repo_relative_posix(output_path),
                        "hash": sha256_file(output_path),
                    }
                )
                return

            if parsed.path == "/api/promote-gold":
                path, info = ensure_editable_path(str(payload.get("path", "")))
                rows = [normalize_row_for_save(row) for row in payload.get("rows", [])]
                train_output = ensure_safe_repo_path(str(payload.get("train_output_path", "")))
                eval_output = ensure_safe_repo_path(str(payload.get("eval_output_path", "")))
                overwrite = bool(payload.get("overwrite_outputs"))

                existing_conflicts = []
                if train_output.exists() and not overwrite:
                    existing_conflicts.append(repo_relative_posix(train_output))
                if eval_output.exists() and not overwrite:
                    existing_conflicts.append(repo_relative_posix(eval_output))
                if existing_conflicts:
                    self.send_json(
                        {"ok": False, "errors": [f"Gold output already exists: {', '.join(existing_conflicts)}"]},
                        status=HTTPStatus.CONFLICT,
                    )
                    return

                errors, train_rows, eval_rows = validate_promotion_export(path, train_output, eval_output, rows, info)
                if errors:
                    self.send_json({"ok": False, "errors": errors}, status=HTTPStatus.BAD_REQUEST)
                    return

                atomic_write_jsonl(train_output, train_rows)
                atomic_write_jsonl(eval_output, eval_rows)
                train_checks = gold_post_checks(train_output, train_rows, "sft_sample.schema.json")
                eval_checks = gold_post_checks(eval_output, eval_rows, "eval_case.schema.json")
                self.send_json(
                    {
                        "ok": True,
                        "train_output_path": repo_relative_posix(train_output),
                        "eval_output_path": repo_relative_posix(eval_output),
                        "train_count": len(train_rows),
                        "eval_count": len(eval_rows),
                        "checks": [train_checks, eval_checks],
                    }
                )
                return

            self.send_json({"error": "Unknown endpoint"}, status=HTTPStatus.NOT_FOUND)
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            self.send_json({"ok": False, "errors": [str(exc)]}, status=HTTPStatus.BAD_REQUEST)

    def serve_static(self, relative_path: str) -> None:
        safe_parts = [part for part in Path(relative_path).parts if part not in ("", ".", "..")]
        if not safe_parts:
            safe_parts = ["index.html"]
        path = (UI_ROOT / Path(*safe_parts)).resolve()
        if not path.is_file() or not path.is_relative_to(UI_ROOT):
            self.send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        return json.loads(body.decode("utf-8"))

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: Any) -> None:
        return


def require_query_value(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key)
    if not values or not values[0]:
        raise ValueError(f"Missing query parameter: {key}")
    return unquote(values[0])


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), EditorRequestHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"JSONL editor running at {url}")
    if args.open_browser:
        webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()

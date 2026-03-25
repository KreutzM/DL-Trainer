from __future__ import annotations

from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_jsonl


def update_candidate_status(candidate: dict, status: str, reviewer: str) -> None:
    candidate["review_status"] = status
    candidate["approved_by"] = reviewer
    if "meta" in candidate:
        candidate["meta"]["review_status"] = status
        candidate["meta"]["approved_by"] = reviewer


def parse_args() -> Any:
    parser = make_parser("Apply human review decisions to teacher outputs.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--approve-id", action="append", default=[])
    parser.add_argument("--reject-id", action="append", default=[])
    parser.add_argument("--approve-file", action="append", default=[])
    parser.add_argument("--reject-file", action="append", default=[])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    approve_ids = set(args.approve_id)
    reject_ids = set(args.reject_id)
    for path_str in args.approve_file:
        approve_ids.update(
            line.strip()
            for line in Path(path_str).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    for path_str in args.reject_file:
        reject_ids.update(
            line.strip()
            for line in Path(path_str).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    overlap = approve_ids & reject_ids
    if overlap:
        raise SystemExit("IDs cannot be both approved and rejected: " + ", ".join(sorted(overlap)))

    rows = read_jsonl(Path(args.input))
    seen_ids = {row["output_id"] for row in rows}
    missing = sorted((approve_ids | reject_ids) - seen_ids)
    if missing:
        raise SystemExit("Unknown output IDs: " + ", ".join(missing))

    for row in rows:
        output_id = row["output_id"]
        if output_id in approve_ids:
            row["review_status"] = "human_reviewed"
            row["approved_by"] = args.reviewer
            update_candidate_status(row["candidate"], "human_reviewed", args.reviewer)
        elif output_id in reject_ids:
            row["review_status"] = "rejected"
            row["approved_by"] = args.reviewer
            update_candidate_status(row["candidate"], "rejected", args.reviewer)

    write_jsonl(Path(args.output), rows)
    print(
        f"Wrote reviewed teacher outputs -> {args.output} "
        f"(approved={len(approve_ids)}, rejected={len(reject_ids)})"
    )


if __name__ == "__main__":
    main()

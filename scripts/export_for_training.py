from __future__ import annotations

from pathlib import Path

from common import make_parser, read_jsonl, write_jsonl


def main() -> None:
    parser = make_parser("Export approved SFT samples into a flat training JSONL.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--only-approved", action="store_true")
    args = parser.parse_args()

    rows = read_jsonl(Path(args.input))
    if args.only_approved:
        rows = [r for r in rows if r.get("meta", {}).get("review_status") == "approved"]

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(Path(args.output), rows)
    print(f"Exported {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()

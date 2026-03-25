from __future__ import annotations

from pathlib import Path

from common import make_parser, read_jsonl, write_jsonl


def main() -> None:
    parser = make_parser("Filter SFT samples by review status.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--review-status", default="approved")
    args = parser.parse_args()

    rows = read_jsonl(Path(args.input))
    filtered = [r for r in rows if r.get("meta", {}).get("review_status") == args.review_status]
    write_jsonl(Path(args.output), filtered)
    print(f"Wrote {len(filtered)} approved samples")


if __name__ == "__main__":
    main()

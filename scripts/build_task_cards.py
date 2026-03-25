from __future__ import annotations

from pathlib import Path

from common import make_parser, read_jsonl, write_jsonl


def main() -> None:
    parser = make_parser("Create placeholder task cards from chunks.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--doc-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    chunks = read_jsonl(Path(args.input))
    cards = []
    for i, chunk in enumerate(chunks, start=1):
        cards.append({
            "task_card_id": f"{args.doc_id}::task_{i:04d}",
            "doc_id": args.doc_id,
            "intent": "review_me",
            "title": chunk["title"],
            "answer": f"TODO: Aus diesem Chunk eine präzise Task-Card ableiten.\\n\\n{chunk['summary']}",
            "source_spans": chunk["source_spans"],
            "review_status": "draft"
        })
    write_jsonl(Path(args.output), cards)
    print(f"Wrote {len(cards)} task cards")


if __name__ == "__main__":
    main()

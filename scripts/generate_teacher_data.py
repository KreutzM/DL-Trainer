from __future__ import annotations

from pathlib import Path

from common import make_parser, read_jsonl, write_jsonl

SYSTEM_PROMPT = (
    "Du bist ein vorsichtiger, präziser Produktsupport-Assistent. "
    "Nutze nur belegbare Informationen. Stelle nur dann genau eine Rückfrage, "
    "wenn der Fall sonst nicht sicher lösbar ist."
)


def main() -> None:
    parser = make_parser("Create starter SFT samples from reviewed task cards.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--product", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--teacher-model", default="teacher-placeholder")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    cards = read_jsonl(Path(args.input))
    rows = []
    for i, card in enumerate(cards, start=1):
        rows.append({
            "id": f"{args.product}_{args.language}_{i:06d}",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": card["title"]},
                {"role": "assistant", "content": card["answer"]}
            ],
            "meta": {
                "product": args.product,
                "language": args.language,
                "teacher_model": args.teacher_model,
                "source_doc_ids": [card["doc_id"]],
                "source_spans": card["source_spans"],
                "review_status": "draft"
            }
        })
    write_jsonl(Path(args.output), rows)
    print(f"Wrote {len(rows)} SFT samples")


if __name__ == "__main__":
    main()

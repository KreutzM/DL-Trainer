from __future__ import annotations

from pathlib import Path

from common import make_parser, read_jsonl, write_jsonl


def main() -> None:
    parser = make_parser("Build simple retrieval chunks from section JSONL.")
    parser.add_argument("--input", required=True, help="Section JSONL")
    parser.add_argument("--doc-id", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = read_jsonl(Path(args.input))
    chunks = []
    for i, row in enumerate(rows, start=1):
        chunks.append({
            "chunk_id": f"{args.doc_id}::chunk_{i:04d}",
            "doc_id": args.doc_id,
            "section_id": row["section_id"],
            "title": row["title"],
            "summary": row["content"][:180].replace("\n", " ").strip(),
            "chunk_type": "reference",
            "content": row["content"],
            "language": args.language,
            "source_spans": [row["section_id"]],
            "review_status": "auto_generated"
        })
    write_jsonl(Path(args.output), chunks)
    print(f"Wrote {len(chunks)} chunks")


if __name__ == "__main__":
    main()

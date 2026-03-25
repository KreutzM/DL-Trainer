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
        source_chunk_ids = card.get("source_chunk_ids") or [f"{card['doc_id']}::task_card_source_{i:06d}"]
        provenance = {
            "transform_pipeline_version": "0.3.0",
            "prompt_template_path": "prompts/teacher/support_answer.md",
            "source_records": [
                {
                    "doc_id": card["doc_id"],
                    "chunk_id": source_chunk_ids[0],
                    "normalized_path": "",
                    "source_spans": card["source_spans"],
                }
            ],
        }
        rows.append({
            "id": f"{args.product}_{args.language}_{i:06d}",
            "product": args.product,
            "language": args.language,
            "task_type": "faq_direct_answer",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": card["title"]},
                {"role": "assistant", "content": card["answer"]},
            ],
            "source_doc_ids": [card["doc_id"]],
            "source_chunk_ids": source_chunk_ids,
            "teacher_model": args.teacher_model,
            "teacher_run_id": "task_card_template_run_v1",
            "teacher_prompt_version": "task_card_support_answer_v1",
            "generation_mode": "task_card_template_v1",
            "review_status": "draft",
            "split": "train",
            "approved_by": None,
            "promoted_from": None,
            "provenance": provenance,
            "meta": {
                "product": args.product,
                "language": args.language,
                "task_type": "faq_direct_answer",
                "teacher_model": args.teacher_model,
                "teacher_run_id": "task_card_template_run_v1",
                "source_doc_ids": [card["doc_id"]],
                "source_chunk_ids": source_chunk_ids,
                "teacher_prompt_version": "task_card_support_answer_v1",
                "generation_mode": "task_card_template_v1",
                "source_spans": card["source_spans"],
                "review_status": "draft",
                "split": "train",
                "approved_by": None,
                "promoted_from": None,
                "provenance": provenance,
            },
        })
    write_jsonl(Path(args.output), rows)
    print(f"Wrote {len(rows)} SFT samples")


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path

from common import make_parser, read_jsonl, write_jsonl


def main() -> None:
    parser = make_parser("Convert SFT samples into eval cases.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    samples = read_jsonl(Path(args.input))
    evals = []
    for i, sample in enumerate(samples, start=1):
        user_turns = [m["content"] for m in sample["messages"] if m["role"] == "user"]
        assistant_turns = [m["content"] for m in sample["messages"] if m["role"] == "assistant"]
        evals.append({
            "eval_id": f"eval_{i:06d}",
            "product": sample.get("product") or sample.get("meta", {}).get("product", ""),
            "language": sample.get("language") or sample.get("meta", {}).get("language", ""),
            "case_type": sample.get("task_type") or sample.get("meta", {}).get("task_type", "faq_direct_answer"),
            "prompt": user_turns[-1] if user_turns else "",
            "case_description": "Abgeleiteter Eval-Fall aus SFT-Sample.",
            "rubric": {
                "must_include": [],
                "must_not_include": ["erfundene Fakten"],
                "style": "präzise, vorsichtig, hilfreich",
            },
            "expected_behavior": "Antwortet nur mit belegbarer Information.",
            "source_doc_ids": sample.get("source_doc_ids") or sample.get("meta", {}).get("source_doc_ids", []),
            "source_chunk_ids": sample.get("source_chunk_ids") or sample.get("meta", {}).get("source_chunk_ids", []),
            "teacher_model": sample.get("teacher_model") or sample.get("meta", {}).get("teacher_model", "teacher-placeholder"),
            "teacher_run_id": sample.get("teacher_run_id") or sample.get("meta", {}).get("teacher_run_id", "derived_eval_from_sft_v1"),
            "teacher_prompt_version": sample.get("teacher_prompt_version") or sample.get("meta", {}).get("teacher_prompt_version", "derived_from_sft_v1"),
            "generation_mode": "derived_eval_from_sft_v1",
            "review_status": sample.get("review_status") or sample.get("meta", {}).get("review_status", "draft"),
            "split": "eval",
            "approved_by": sample.get("approved_by") or sample.get("meta", {}).get("approved_by"),
            "promoted_from": sample.get("promoted_from") or sample.get("meta", {}).get("promoted_from"),
            "provenance": sample.get("provenance") or sample.get("meta", {}).get("provenance", {}),
            "reference_answer": assistant_turns[-1] if assistant_turns else "",
        })
    write_jsonl(Path(args.output), evals)
    print(f"Wrote {len(evals)} eval cases")


if __name__ == "__main__":
    main()

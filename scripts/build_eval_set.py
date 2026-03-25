from __future__ import annotations

from pathlib import Path

from common import make_parser, read_jsonl, write_jsonl


def main() -> None:
    parser = make_parser("Convert SFT samples into simple eval cases.")
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
            "input": user_turns[-1] if user_turns else "",
            "rubric": {
                "must_include": [],
                "must_not_include": ["erfundene Fakten"],
                "style": "präzise, vorsichtig, hilfreich"
            },
            "expected_behavior": "Antwortet nur mit belegbarer Information.",
            "reference_answer": assistant_turns[-1] if assistant_turns else ""
        })
    write_jsonl(Path(args.output), evals)
    print(f"Wrote {len(evals)} eval cases")


if __name__ == "__main__":
    main()

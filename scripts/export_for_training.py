from __future__ import annotations

import shutil
from pathlib import Path

from common import make_parser


def main() -> None:
    parser = make_parser("Backward-compatible wrapper for the Qwen SFT export.")
    parser.add_argument("--train-input", action="append", dest="train_inputs")
    parser.add_argument("--eval-input", action="append", dest="eval_inputs")
    parser.add_argument("--output-dir")
    parser.add_argument("--export-id", default="legacy_export")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--only-approved", action="store_true")
    args = parser.parse_args()

    if args.input and args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.input, args.output)
        print(f"Copied legacy export input to {args.output}")
        return

    if not args.train_inputs or not args.eval_inputs or not args.output_dir:
        parser.error(
            "Use legacy --input/--output mode or provide --train-input, --eval-input, and --output-dir."
        )

    from export_qwen_sft import export_qwen_sft

    export_qwen_sft(
        train_inputs=[Path(path) for path in args.train_inputs],
        eval_inputs=[Path(path) for path in args.eval_inputs],
        output_dir=Path(args.output_dir),
        export_id=args.export_id,
    )


if __name__ == "__main__":
    main()

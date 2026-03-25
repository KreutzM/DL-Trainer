from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from common import make_parser, read_json, read_jsonl


def main() -> None:
    parser = make_parser("Validate a JSONL file against a JSON Schema.")
    parser.add_argument("--schema", required=True)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    schema = read_json(Path(args.schema))
    validator = Draft202012Validator(schema)
    rows = read_jsonl(Path(args.input))

    errors = []
    for idx, row in enumerate(rows, start=1):
        row_errors = list(validator.iter_errors(row))
        for err in row_errors:
            errors.append(f"Row {idx}: {err.message}")

    if errors:
        print("\n".join(errors))
        raise SystemExit(1)

    print(f"OK: {args.input} ({len(rows)} rows)")
    raise SystemExit(0)


if __name__ == "__main__":
    main()

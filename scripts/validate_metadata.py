from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from common import find_repo_root, make_parser, read_json


def main() -> None:
    parser = make_parser("Validate a metadata JSON file against schemas/manual_meta.schema.json")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    repo_root = find_repo_root(Path.cwd())
    schema_path = repo_root / "schemas" / "manual_meta.schema.json"

    validator = Draft202012Validator(read_json(schema_path))
    data = read_json(input_path)
    errors = list(validator.iter_errors(data))
    if errors:
        for err in errors:
            print(err.message)
        raise SystemExit(1)

    print(f"OK: {input_path}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()

from __future__ import annotations

import re
from pathlib import Path

from common import make_parser, write_jsonl

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def extract_sections(markdown_text: str, doc_id: str) -> list[dict]:
    sections = []
    current_title = "Document Start"
    current_lines: list[str] = []

    def flush(counter: int) -> None:
        nonlocal current_title, current_lines
        if not current_lines:
            return
        sections.append({
            "section_id": f"{doc_id}::sec_{counter:04d}",
            "title": current_title,
            "content": "\n".join(current_lines).strip()
        })
        current_lines = []

    counter = 0
    for line in markdown_text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            counter += 1
            flush(counter - 1)
            current_title = m.group(2).strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    counter += 1
    flush(counter - 1)
    return sections


def main() -> None:
    parser = make_parser("Extract simple sections from normalized markdown.")
    parser.add_argument("--input-md", required=True)
    parser.add_argument("--doc-id", required=True)
    parser.add_argument("--output-jsonl", required=True)
    args = parser.parse_args()

    text = Path(args.input_md).read_text(encoding="utf-8")
    sections = extract_sections(text, args.doc_id)
    write_jsonl(Path(args.output_jsonl), sections)
    print(f"Wrote {len(sections)} sections")


if __name__ == "__main__":
    main()

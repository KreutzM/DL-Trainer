from __future__ import annotations

import shutil
from pathlib import Path

from common import make_parser, sha256_file, write_json


def main() -> None:
    parser = make_parser("Copy a source manual into data/raw and create a minimal metadata file.")
    parser.add_argument("--source", required=True, help="Path to source file")
    parser.add_argument("--dest-dir", required=True, help="Destination directory under data/raw")
    parser.add_argument("--product", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--source-type", required=True, choices=["pdf", "html", "xml", "txt", "other"])
    parser.add_argument("--pipeline-version", default="0.1.0")
    args = parser.parse_args()

    source = Path(args.source)
    dest_dir = Path(args.dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / source.name
    shutil.copy2(source, dest)

    meta = {
        "doc_id": f"{args.product}_{args.language}_{source.stem}_{args.version}",
        "product": args.product,
        "language": args.language,
        "version": args.version,
        "source_type": args.source_type,
        "source_file": str(dest),
        "checksum": sha256_file(dest),
        "import_date": "TODO",
        "transform_pipeline_version": args.pipeline_version,
        "notes": "Initial ingest"
    }
    write_json(dest.with_suffix(dest.suffix + ".meta.json"), meta)
    print(f"Ingested: {dest}")


if __name__ == "__main__":
    main()

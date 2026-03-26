from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from common import find_repo_root, make_parser


def _run(repo_root: Path, args: list[str]) -> None:
    command = [sys.executable, *args]
    print("RUN", " ".join(args))
    subprocess.run(command, cwd=repo_root, check=True)


def main() -> None:
    parser = make_parser("Run the full clean Qwen dataset gate locally.")
    args = parser.parse_args()
    del args

    repo_root = find_repo_root(Path.cwd())
    tmp_root = repo_root / "tmp" / "qwen_quality" / "gate_export"
    tmp_export_dir = tmp_root / "qwen_sft_export"
    tmp_config_path = tmp_root / "qwen3_8b_jaws_de_lora_clean_dry_run.gate.yaml"
    tmp_root.mkdir(parents=True, exist_ok=True)

    _run(
        repo_root,
        [
            "scripts/cleanup_qwen_sft_gold.py",
            "--train-input",
            "data/gold/train/sft/JAWS/DE/consolidated_gold_v1_sft_samples.jsonl",
            "--eval-input",
            "data/gold/eval/JAWS/DE/consolidated_gold_v1_eval_cases.jsonl",
            "--train-output",
            "data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl",
            "--eval-output",
            "data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl",
            "--report-output",
            "tmp/qwen_quality/consolidated_gold_v1_lora_clean.cleanup.json",
        ],
    )
    _run(
        repo_root,
        [
            "scripts/validate_jsonl.py",
            "--schema",
            "schemas/sft_sample.schema.json",
            "--input",
            "data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl",
        ],
    )
    _run(
        repo_root,
        [
            "scripts/validate_jsonl.py",
            "--schema",
            "schemas/eval_case.schema.json",
            "--input",
            "data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl",
        ],
    )
    _run(
        repo_root,
        [
            "scripts/check_provenance.py",
            "--input",
            "data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl",
        ],
    )
    _run(
        repo_root,
        [
            "scripts/check_provenance.py",
            "--input",
            "data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl",
        ],
    )
    _run(
        repo_root,
        [
            "scripts/audit_qwen_source_faithfulness.py",
            "--train-input",
            "data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl",
            "--eval-input",
            "data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl",
            "--output",
            "tmp/qwen_quality/consolidated_gold_v1_lora_clean.source_audit.json",
            "--max-train-flagged-rows",
            "0",
            "--max-eval-flagged-rows",
            "0",
        ],
    )
    _run(
        repo_root,
        [
            "scripts/export_qwen_sft.py",
            "--train-input",
            "data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl",
            "--eval-input",
            "data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl",
            "--output-dir",
            tmp_export_dir.as_posix(),
            "--export-id",
            "jaws_de_consolidated_gold_v1_lora_clean_gate",
        ],
    )
    _run(
        repo_root,
        [
            "scripts/validate_qwen_sft_export.py",
            "--input-dir",
            tmp_export_dir.as_posix(),
        ],
    )

    config_path = repo_root / "training" / "ms-swift" / "qwen3_8b_jaws_de_lora_clean_dry_run.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["dataset"]["train_file"] = (tmp_export_dir / "train.jsonl").as_posix()
    config["dataset"]["eval_file"] = (tmp_export_dir / "eval.jsonl").as_posix()
    config["dataset"]["train_metadata_file"] = (tmp_export_dir / "train.metadata.jsonl").as_posix()
    config["dataset"]["eval_metadata_file"] = (tmp_export_dir / "eval.metadata.jsonl").as_posix()
    config["dataset"]["manifest_file"] = (tmp_export_dir / "manifest.json").as_posix()
    config["training"]["output_dir"] = (tmp_root / "ms_swift_outputs").as_posix()
    config["training"]["logging_dir"] = (tmp_root / "ms_swift_logs").as_posix()
    tmp_config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    _run(
        repo_root,
        [
            "scripts/smoke_test_qwen_sft.py",
            "--config",
            tmp_config_path.as_posix(),
        ],
    )


if __name__ == "__main__":
    main()

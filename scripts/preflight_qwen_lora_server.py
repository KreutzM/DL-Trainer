from __future__ import annotations

import importlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import yaml
from jsonschema import Draft202012Validator

from common import find_repo_root, make_parser, read_json, read_jsonl, sha256_file, write_json


PACKAGE_CHECKS = {
    "yaml": "PyYAML",
    "jsonschema": "jsonschema",
    "torch": "torch",
    "datasets": "datasets",
    "transformers": "transformers",
    "peft": "peft",
    "bitsandbytes": "bitsandbytes",
}


def _resolve(repo_root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return repo_root / path


def _parse_version(version_str: str) -> tuple[int, ...]:
    parts = []
    for part in version_str.split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def _load_and_validate_config(repo_root: Path, config_path: Path) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    schema = read_json(repo_root / "schemas" / "qwen_training_config.schema.json")
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(config))
    if errors:
        raise SystemExit("\n".join(err.message for err in errors))
    return config


def _ensure_imports() -> dict[str, str]:
    versions: dict[str, str] = {}
    missing: list[str] = []
    for module_name, package_name in PACKAGE_CHECKS.items():
        try:
            importlib.import_module(module_name)
            versions[package_name] = importlib.metadata.version(package_name)
        except (ImportError, importlib.metadata.PackageNotFoundError):
            missing.append(package_name)
    if missing:
        raise SystemExit(
            "Missing Python packages for server run: "
            + ", ".join(sorted(missing))
            + ". Install training/transformers/requirements-qwen-lora-server.txt and a CUDA-enabled PyTorch build."
        )
    return versions


def _collect_nvidia_smi() -> dict[str, Any] | None:
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return None
    result = subprocess.run(
        [
            nvidia_smi,
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip() or "nvidia-smi returned a non-zero exit code"}
    rows = []
    for line in result.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) == 3:
            rows.append(
                {
                    "name": parts[0],
                    "memory_total": parts[1],
                    "driver_version": parts[2],
                }
            )
    return {"gpus": rows}


def _assert_writeable_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    probe_path = path / ".write_probe"
    probe_path.write_text("ok\n", encoding="utf-8")
    probe_path.unlink()


def _assert_clean_or_resumable_output(path: Path, allow_existing_output: bool) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "entries": [], "checkpoints": []}

    entries = sorted(child.name for child in path.iterdir())
    checkpoints = sorted(
        child.name for child in path.iterdir() if child.is_dir() and child.name.startswith("checkpoint-")
    )
    final_adapter_exists = (path / "final_adapter").exists()
    run_summary_exists = (path / "run_summary.json").exists()
    substantive_entries = checkpoints or entries

    if substantive_entries and not allow_existing_output:
        raise SystemExit(
            f"Output directory is not empty: {path.as_posix()}. "
            "Use a fresh path or rerun the start script with --resume-latest/--resume-from."
        )

    return {
        "exists": True,
        "entries": entries,
        "checkpoints": checkpoints,
        "final_adapter_exists": final_adapter_exists,
        "run_summary_exists": run_summary_exists,
    }


def _assert_dataset_is_final(manifest: dict[str, Any]) -> None:
    suspicious_tokens = ("demo", "fixture", "stub")
    candidates = [
        manifest.get("export_id", ""),
        *manifest.get("source_train_files", []),
        *manifest.get("source_eval_files", []),
    ]
    for value in candidates:
        lowered = value.casefold()
        if any(token in lowered for token in suspicious_tokens):
            raise SystemExit(f"Dataset freeze points to a non-final source marker: {value}")


def main() -> None:
    parser = make_parser("Validate Linux/CUDA environment, dataset freeze, and output paths before starting the server run.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--allow-existing-output", action="store_true")
    parser.add_argument("--summary-output", default=None)
    args = parser.parse_args()

    repo_root = find_repo_root(Path.cwd())
    config_path = _resolve(repo_root, args.config)
    config = _load_and_validate_config(repo_root, config_path)
    package_versions = _ensure_imports()

    runtime_cfg = config["runtime"]
    dataset_cfg = config["dataset"]
    training_cfg = config["training"]

    expected_platform = runtime_cfg.get("expected_platform", "linux").casefold()
    actual_platform = platform.system().casefold()
    if actual_platform != expected_platform:
        raise SystemExit(f"Expected platform {expected_platform}, found {actual_platform}")

    python_min = runtime_cfg.get("expected_python_min", "3.10")
    if sys.version_info < _parse_version(python_min):
        raise SystemExit(f"Python {python_min}+ required, found {platform.python_version()}")

    train_path = _resolve(repo_root, dataset_cfg["train_file"])
    eval_path = _resolve(repo_root, dataset_cfg["eval_file"])
    train_meta_path = _resolve(repo_root, dataset_cfg["train_metadata_file"])
    eval_meta_path = _resolve(repo_root, dataset_cfg["eval_metadata_file"])
    manifest_path = _resolve(repo_root, dataset_cfg["manifest_file"])
    output_dir = _resolve(repo_root, training_cfg["output_dir"])
    logging_dir = _resolve(repo_root, training_cfg["logging_dir"])

    required_paths = [train_path, eval_path, train_meta_path, eval_meta_path, manifest_path]
    missing_paths = [path.as_posix() for path in required_paths if not path.exists()]
    if missing_paths:
        raise SystemExit("Missing dataset files: " + ", ".join(missing_paths))

    manifest = read_json(manifest_path)
    _assert_dataset_is_final(manifest)
    train_rows = read_jsonl(train_path)
    eval_rows = read_jsonl(eval_path)
    train_meta_rows = read_jsonl(train_meta_path)
    eval_meta_rows = read_jsonl(eval_meta_path)

    if not train_rows or not eval_rows:
        raise SystemExit("Train/eval export must not be empty")
    if len(train_rows) != len(train_meta_rows):
        raise SystemExit("Train export and train metadata counts differ")
    if len(eval_rows) != len(eval_meta_rows):
        raise SystemExit("Eval export and eval metadata counts differ")
    if manifest.get("train_records") != len(train_rows):
        raise SystemExit("Manifest train_records mismatch")
    if manifest.get("eval_records") != len(eval_rows):
        raise SystemExit("Manifest eval_records mismatch")

    manifest_hashes = manifest.get("hashes", {})
    expected_hashes = {
        "train_file_sha256": train_path,
        "eval_file_sha256": eval_path,
        "train_metadata_file_sha256": train_meta_path,
        "eval_metadata_file_sha256": eval_meta_path,
    }
    for key, path in expected_hashes.items():
        expected = manifest_hashes.get(key)
        actual = sha256_file(path)
        if expected and expected != actual:
            raise SystemExit(f"Hash mismatch for {path.as_posix()}: manifest={expected} actual={actual}")

    if manifest.get("split_chunk_overlap") not in ([], None):
        raise SystemExit("Manifest split_chunk_overlap must be empty")

    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available in the active PyTorch installation")
    gpu_count = torch.cuda.device_count()
    if gpu_count < int(runtime_cfg.get("min_cuda_devices", 1)):
        raise SystemExit(f"Expected at least {runtime_cfg.get('min_cuda_devices', 1)} CUDA device(s), found {gpu_count}")

    first_gpu_name = torch.cuda.get_device_name(0)
    first_gpu_memory_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
    expected_gpu_substring = runtime_cfg.get("expected_gpu_name_substring")
    if expected_gpu_substring and expected_gpu_substring.casefold() not in first_gpu_name.casefold():
        raise SystemExit(f"Expected GPU containing '{expected_gpu_substring}', found '{first_gpu_name}'")
    min_gpu_memory_gb = float(runtime_cfg.get("min_gpu_memory_gb", 0))
    if first_gpu_memory_gb < min_gpu_memory_gb:
        raise SystemExit(f"Expected at least {min_gpu_memory_gb} GB VRAM, found {first_gpu_memory_gb} GB")
    if training_cfg.get("bf16", False) and not torch.cuda.is_bf16_supported():
        raise SystemExit("Config requires bf16, but torch reports bf16 support is unavailable on the active GPU")

    _assert_writeable_dir(output_dir)
    _assert_writeable_dir(logging_dir)
    output_status = _assert_clean_or_resumable_output(output_dir, allow_existing_output=args.allow_existing_output)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "ok",
        "config_path": config_path.as_posix(),
        "python_version": platform.python_version(),
        "package_versions": package_versions,
        "platform": platform.system(),
        "nvidia_smi": _collect_nvidia_smi(),
        "cuda": {
            "device_count": gpu_count,
            "first_gpu_name": first_gpu_name,
            "first_gpu_memory_gb": first_gpu_memory_gb,
            "bf16_supported": torch.cuda.is_bf16_supported(),
            "torch_cuda_version": torch.version.cuda,
        },
        "dataset": {
            "export_id": manifest.get("export_id"),
            "manifest_path": manifest_path.as_posix(),
            "train_file": train_path.as_posix(),
            "eval_file": eval_path.as_posix(),
            "train_records": len(train_rows),
            "eval_records": len(eval_rows),
            "train_bytes": train_path.stat().st_size,
            "eval_bytes": eval_path.stat().st_size,
            "source_train_files": manifest.get("source_train_files", []),
            "source_eval_files": manifest.get("source_eval_files", []),
        },
        "outputs": {
            "output_dir": output_dir.as_posix(),
            "logging_dir": logging_dir.as_posix(),
            "allow_existing_output": bool(args.allow_existing_output),
            "output_status": output_status,
        },
    }

    if args.summary_output:
        write_json(_resolve(repo_root, args.summary_output), summary)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

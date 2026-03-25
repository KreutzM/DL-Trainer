from __future__ import annotations

from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from common import make_parser, read_json, read_jsonl


def _resolve(repo_root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return repo_root / path


def _build_ms_swift_command(config: dict) -> str:
    model = config["model"]
    dataset = config["dataset"]
    training = config["training"]
    lora = config["lora"]
    runtime = config["runtime"]
    run = config["run"]

    command = [
        "swift sft",
        f"--model {model['base_model']}",
        f"--train_dataset {dataset['train_file']}",
        f"--val_dataset {dataset['eval_file']}",
        f"--dataset_format {dataset['format']}",
        f"--max_length {model['max_length']}",
        f"--output_dir {training['output_dir']}",
        f"--logging_dir {training['logging_dir']}",
        f"--num_train_epochs {training['num_train_epochs']}",
        f"--per_device_train_batch_size {training['per_device_train_batch_size']}",
        f"--per_device_eval_batch_size {training.get('per_device_eval_batch_size', 1)}",
        f"--gradient_accumulation_steps {training['gradient_accumulation_steps']}",
        f"--learning_rate {training['learning_rate']}",
        f"--lr_scheduler_type {training.get('lr_scheduler_type', 'cosine')}",
        f"--warmup_ratio {training.get('warmup_ratio', 0.0)}",
        f"--weight_decay {training.get('weight_decay', 0.0)}",
        f"--max_grad_norm {training.get('max_grad_norm', 1.0)}",
        f"--eval_strategy {training.get('eval_strategy', 'steps')}",
        f"--eval_steps {training.get('eval_steps', 10)}",
        f"--save_strategy {training.get('save_strategy', 'steps')}",
        f"--save_steps {training.get('save_steps', 50)}",
        f"--save_total_limit {training.get('save_total_limit', 2)}",
        f"--seed {training['seed']}",
        f"--run_name {run['run_name']}",
        f"--lora_rank {lora['r']}",
        f"--lora_alpha {lora['alpha']}",
        f"--lora_dropout {lora['dropout']}",
        f"--target_modules {','.join(lora['target_modules'])}",
    ]
    if model.get("trust_remote_code", False):
        command.append("--trust_remote_code true")
    if training.get("bf16", False):
        command.append("--bf16 true")
    if runtime.get("gradient_checkpointing", False):
        command.append("--gradient_checkpointing true")
    if runtime.get("flash_attention"):
        command.append(f"--attn_impl {runtime['flash_attention']}")
    if runtime.get("report_to"):
        command.append(f"--report_to {','.join(runtime['report_to'])}")
    if runtime.get("dry_run_steps"):
        command.append(f"--max_steps {runtime['dry_run_steps']}")
    return " ".join(command)


def main() -> None:
    parser = make_parser("Validate Qwen training config and exported dataset, then print a reproducible dry-run command.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    config_path = _resolve(repo_root, args.config)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config_schema = read_json(repo_root / "schemas" / "qwen_training_config.schema.json")
    validator = Draft202012Validator(config_schema)
    errors = list(validator.iter_errors(config))
    if errors:
        raise SystemExit("\n".join(err.message for err in errors))

    dataset = config["dataset"]
    train_path = _resolve(repo_root, dataset["train_file"])
    eval_path = _resolve(repo_root, dataset["eval_file"])
    train_meta_path = _resolve(repo_root, dataset["train_metadata_file"])
    eval_meta_path = _resolve(repo_root, dataset["eval_metadata_file"])
    manifest_path = _resolve(repo_root, dataset["manifest_file"])

    for path in [train_path, eval_path, train_meta_path, eval_meta_path, manifest_path]:
        if not path.exists():
            raise SystemExit(f"Missing dataset path: {path.as_posix()}")

    train_rows = read_jsonl(train_path)
    eval_rows = read_jsonl(eval_path)
    train_meta_rows = read_jsonl(train_meta_path)
    eval_meta_rows = read_jsonl(eval_meta_path)

    if not train_rows or not eval_rows:
        raise SystemExit("Train/eval export must not be empty")
    if len(train_rows) != len(train_meta_rows):
        raise SystemExit("Train export and metadata counts differ")
    if len(eval_rows) != len(eval_meta_rows):
        raise SystemExit("Eval export and metadata counts differ")

    train_chunks = {chunk_id for row in train_meta_rows for chunk_id in row["source_chunk_ids"]}
    eval_chunks = {chunk_id for row in eval_meta_rows for chunk_id in row["source_chunk_ids"]}
    if train_chunks & eval_chunks:
        raise SystemExit(f"Train/eval chunk overlap detected: {sorted(train_chunks & eval_chunks)}")

    max_train_turns = max(len(row["messages"]) for row in train_rows)
    max_eval_turns = max(len(row["messages"]) for row in eval_rows)
    max_train_chars = max(sum(len(message["content"]) for message in row["messages"]) for row in train_rows)
    max_eval_chars = max(sum(len(message["content"]) for message in row["messages"]) for row in eval_rows)

    print(f"Config OK: {config_path.as_posix()}")
    print(f"Train rows: {len(train_rows)} | Eval rows: {len(eval_rows)}")
    print(f"Max train turns/chars: {max_train_turns}/{max_train_chars}")
    print(f"Max eval turns/chars: {max_eval_turns}/{max_eval_chars}")
    print("Dry-run command:")
    print(_build_ms_swift_command(config))


if __name__ == "__main__":
    main()

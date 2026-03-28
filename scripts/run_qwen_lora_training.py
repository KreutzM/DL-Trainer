from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import torch
import yaml
from datasets import Dataset
from jsonschema import Draft202012Validator
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)

from common import find_repo_root, make_parser, read_json, read_jsonl, write_json


def _resolve(repo_root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return repo_root / path


def _apply_chat_template(tokenizer: Any, messages: list[dict], add_generation_prompt: bool) -> str:
    kwargs = {"tokenize": False, "add_generation_prompt": add_generation_prompt}
    try:
        return tokenizer.apply_chat_template(messages, enable_thinking=False, **kwargs)
    except TypeError:
        return tokenizer.apply_chat_template(messages, **kwargs)


def _dtype(dtype_name: str) -> torch.dtype:
    mapping = {
        "bfloat16": torch.bfloat16,
        "bf16": torch.bfloat16,
        "float16": torch.float16,
        "fp16": torch.float16,
        "float32": torch.float32,
        "fp32": torch.float32,
    }
    try:
        return mapping[dtype_name.casefold()]
    except KeyError as exc:
        raise ValueError(f"Unsupported dtype {dtype_name}") from exc


def _git_value(repo_root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.strip() or None


def _token_length_percentiles(lengths: list[int]) -> dict[str, int]:
    if not lengths:
        return {}
    ordered = sorted(lengths)
    values: dict[str, int] = {}
    for percentile in [50, 75, 90, 95, 99, 100]:
        idx = min(len(ordered) - 1, round((percentile / 100) * (len(ordered) - 1)))
        values[f"p{percentile}"] = ordered[idx]
    return values


@dataclass
class PreparedSplit:
    dataset: Dataset
    stats: dict[str, Any]


class CausalLMCollator:
    def __init__(self, tokenizer: Any) -> None:
        self.tokenizer = tokenizer

    def __call__(self, features: list[dict]) -> dict[str, torch.Tensor]:
        batch = self.tokenizer.pad(
            [{"input_ids": feature["input_ids"], "attention_mask": feature["attention_mask"]} for feature in features],
            padding=True,
            return_tensors="pt",
        )
        max_len = int(batch["input_ids"].shape[1])
        labels = []
        for feature in features:
            pad_size = max_len - len(feature["labels"])
            labels.append(feature["labels"] + [-100] * pad_size)
        batch["labels"] = torch.tensor(labels, dtype=torch.long)
        return batch


def _prepare_split(
    rows: list[dict],
    tokenizer: Any,
    max_length: int,
    assistant_only_loss: bool,
    split: str,
    max_rows: int | None = None,
) -> PreparedSplit:
    processed_rows: list[dict] = []
    token_lengths: list[int] = []
    prompt_token_lengths: list[int] = []
    truncated_rows = 0

    source_rows = rows[:max_rows] if max_rows else rows
    for row in source_rows:
        messages = row["messages"]
        full_text = _apply_chat_template(tokenizer, messages, add_generation_prompt=False)
        prompt_text = _apply_chat_template(tokenizer, messages[:-1], add_generation_prompt=True)
        full_tokens = tokenizer(
            full_text,
            add_special_tokens=False,
            truncation=True,
            max_length=max_length,
        )
        prompt_tokens = tokenizer(
            prompt_text,
            add_special_tokens=False,
            truncation=True,
            max_length=max_length,
        )
        input_ids = list(full_tokens["input_ids"])
        attention_mask = list(full_tokens["attention_mask"])
        labels = list(input_ids)
        prompt_len = min(len(prompt_tokens["input_ids"]), len(input_ids))
        if len(tokenizer(full_text, add_special_tokens=False)["input_ids"]) > max_length:
            truncated_rows += 1
        if assistant_only_loss:
            labels[:prompt_len] = [-100] * prompt_len
            if all(value == -100 for value in labels):
                raise ValueError(f"{row['id']} loses all assistant tokens at max_length={max_length}")
        token_lengths.append(len(input_ids))
        prompt_token_lengths.append(prompt_len)
        processed_rows.append(
            {
                "id": row["id"],
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "labels": labels,
            }
        )

    stats = {
        "split": split,
        "rows": len(processed_rows),
        "max_length": max_length,
        "mean_tokens": round(mean(token_lengths), 2) if token_lengths else 0,
        "token_length_percentiles": _token_length_percentiles(token_lengths),
        "mean_prompt_tokens": round(mean(prompt_token_lengths), 2) if prompt_token_lengths else 0,
        "truncated_rows": truncated_rows,
    }
    return PreparedSplit(dataset=Dataset.from_list(processed_rows), stats=stats)


def _load_and_validate_config(repo_root: Path, config_path: Path) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    schema = read_json(repo_root / "schemas" / "qwen_training_config.schema.json")
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(config))
    if errors:
        raise SystemExit("\n".join(err.message for err in errors))
    return config


def _load_model_and_tokenizer(config: dict[str, Any]) -> tuple[Any, Any]:
    model_cfg = config["model"]
    runtime_cfg = config["runtime"]
    quant_cfg = config.get("quantization", {})

    tokenizer = AutoTokenizer.from_pretrained(
        model_cfg["tokenizer_name_or_path"],
        trust_remote_code=model_cfg.get("trust_remote_code", False),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    quantization_config = None
    if quant_cfg.get("load_in_4bit", False):
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type=quant_cfg.get("bnb_4bit_quant_type", "nf4"),
            bnb_4bit_use_double_quant=quant_cfg.get("bnb_4bit_use_double_quant", True),
            bnb_4bit_compute_dtype=_dtype(quant_cfg.get("bnb_4bit_compute_dtype", "bfloat16")),
        )

    model = AutoModelForCausalLM.from_pretrained(
        model_cfg["base_model"],
        trust_remote_code=model_cfg.get("trust_remote_code", False),
        dtype=torch.bfloat16 if config["training"].get("bf16", False) else torch.float16,
        quantization_config=quantization_config,
        device_map="auto",
        low_cpu_mem_usage=True,
        attn_implementation=runtime_cfg.get("attention_implementation"),
    )
    model.config.use_cache = False
    if runtime_cfg.get("gradient_checkpointing", False):
        model = prepare_model_for_kbit_training(
            model,
            use_gradient_checkpointing=True,
            gradient_checkpointing_kwargs={
                "use_reentrant": not bool(runtime_cfg.get("max_grad_ckpt_use_reentrant", False))
            },
        )

    lora_cfg = config["lora"]
    peft_config = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["alpha"],
        lora_dropout=lora_cfg["dropout"],
        bias="none",
        task_type=TaskType.CAUSAL_LM,
        target_modules=lora_cfg["target_modules"],
    )
    model = get_peft_model(model, peft_config)
    return model, tokenizer


def main() -> None:
    parser = make_parser("Run a reproducible Qwen3-8B PEFT/QLoRA training job from a validated config.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--resume-from-checkpoint", default=None)
    args = parser.parse_args()

    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    repo_root = find_repo_root(Path.cwd())
    config_path = _resolve(repo_root, args.config)
    config = _load_and_validate_config(repo_root, config_path)

    dataset_cfg = config["dataset"]
    training_cfg = config["training"]
    runtime_cfg = config["runtime"]
    model_cfg = config["model"]

    train_path = _resolve(repo_root, dataset_cfg["train_file"])
    eval_path = _resolve(repo_root, dataset_cfg["eval_file"])
    manifest_path = _resolve(repo_root, dataset_cfg["manifest_file"])
    output_dir = _resolve(repo_root, training_cfg["output_dir"])
    logging_dir = _resolve(repo_root, training_cfg["logging_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    logging_dir.mkdir(parents=True, exist_ok=True)

    train_rows = read_jsonl(train_path)
    eval_rows = read_jsonl(eval_path)
    manifest = read_json(manifest_path)

    model, tokenizer = _load_model_and_tokenizer(config)
    max_length = int(model_cfg["max_length"])
    assistant_only_loss = bool(runtime_cfg.get("assistant_only_loss", True))

    prepared_train = _prepare_split(
        train_rows,
        tokenizer,
        max_length=max_length,
        assistant_only_loss=assistant_only_loss,
        split="train",
        max_rows=training_cfg.get("max_train_samples"),
    )
    prepared_eval = _prepare_split(
        eval_rows,
        tokenizer,
        max_length=max_length,
        assistant_only_loss=assistant_only_loss,
        split="eval",
        max_rows=training_cfg.get("max_eval_samples"),
    )

    data_collator = CausalLMCollator(tokenizer)
    training_args = TrainingArguments(
        output_dir=output_dir.as_posix(),
        logging_dir=logging_dir.as_posix(),
        num_train_epochs=float(training_cfg["num_train_epochs"]),
        per_device_train_batch_size=int(training_cfg["per_device_train_batch_size"]),
        per_device_eval_batch_size=int(training_cfg.get("per_device_eval_batch_size", 1)),
        gradient_accumulation_steps=int(training_cfg["gradient_accumulation_steps"]),
        learning_rate=float(training_cfg["learning_rate"]),
        lr_scheduler_type=training_cfg.get("lr_scheduler_type", "cosine"),
        warmup_ratio=float(training_cfg.get("warmup_ratio", 0.0)),
        weight_decay=float(training_cfg.get("weight_decay", 0.0)),
        max_grad_norm=float(training_cfg.get("max_grad_norm", 1.0)),
        eval_strategy=training_cfg.get("eval_strategy", "steps"),
        eval_steps=int(training_cfg.get("eval_steps", 10)),
        save_strategy=training_cfg.get("save_strategy", "steps"),
        save_steps=int(training_cfg.get("save_steps", 50)),
        save_total_limit=int(training_cfg.get("save_total_limit", 2)),
        logging_steps=int(training_cfg.get("logging_steps", 5)),
        seed=int(training_cfg["seed"]),
        bf16=bool(training_cfg.get("bf16", False)),
        remove_unused_columns=False,
        dataloader_num_workers=int(runtime_cfg.get("dataloader_num_workers", 0)),
        report_to=list(runtime_cfg.get("report_to", [])),
        optim=training_cfg.get("optim", "paged_adamw_8bit"),
        max_steps=int(training_cfg["max_steps"]) if training_cfg.get("max_steps") is not None else -1,
        save_safetensors=True,
        label_names=["labels"],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=prepared_train.dataset,
        eval_dataset=prepared_eval.dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    resume_from_checkpoint = None
    if args.resume_from_checkpoint:
        resume_from_checkpoint = _resolve(repo_root, args.resume_from_checkpoint).as_posix()
    elif runtime_cfg.get("resume_from_checkpoint"):
        resume_from_checkpoint = _resolve(repo_root, runtime_cfg["resume_from_checkpoint"]).as_posix()

    train_result = trainer.train(resume_from_checkpoint=resume_from_checkpoint)
    eval_metrics = trainer.evaluate()
    trainer.save_state()

    final_adapter_dir = output_dir / "final_adapter"
    trainer.model.save_pretrained(final_adapter_dir)
    tokenizer.save_pretrained(final_adapter_dir)

    run_summary = {
        "run_name": config["run"]["run_name"],
        "framework": config["run"]["framework"],
        "stage": config["run"]["stage"],
        "started_from_config": config_path.as_posix(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "git": {
            "branch": _git_value(repo_root, "branch", "--show-current"),
            "head": _git_value(repo_root, "rev-parse", "HEAD"),
            "head_short": _git_value(repo_root, "rev-parse", "--short", "HEAD"),
        },
        "dataset": {
            "manifest_path": manifest_path.as_posix(),
            "export_id": manifest.get("export_id"),
            "train_file": train_path.as_posix(),
            "eval_file": eval_path.as_posix(),
            "manifest_train_records": manifest.get("train_records"),
            "manifest_eval_records": manifest.get("eval_records"),
            "prepared_train": prepared_train.stats,
            "prepared_eval": prepared_eval.stats,
        },
        "model": {
            "base_model": model_cfg["base_model"],
            "tokenizer_name_or_path": model_cfg["tokenizer_name_or_path"],
            "max_length": max_length,
            "trainable_params": int(sum(param.numel() for param in trainer.model.parameters() if param.requires_grad)),
            "total_params": int(sum(param.numel() for param in trainer.model.parameters())),
        },
        "training": {
            "output_dir": output_dir.as_posix(),
            "logging_dir": logging_dir.as_posix(),
            "resume_from_checkpoint": resume_from_checkpoint,
            "final_adapter_dir": final_adapter_dir.as_posix(),
            "global_step": int(trainer.state.global_step),
            "train_runtime_sec": float(train_result.metrics.get("train_runtime", 0.0)),
            "train_samples_per_second": float(train_result.metrics.get("train_samples_per_second", 0.0)),
            "train_loss": float(train_result.metrics.get("train_loss", 0.0)),
            "eval_loss": float(eval_metrics.get("eval_loss", 0.0)),
            "eval_runtime_sec": float(eval_metrics.get("eval_runtime", 0.0)),
            "config": config,
        },
    }
    write_json(output_dir / "run_summary.json", run_summary)
    print(json.dumps(run_summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

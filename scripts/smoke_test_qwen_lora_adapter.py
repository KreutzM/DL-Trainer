from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import yaml
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from common import find_repo_root, make_parser, read_json, read_jsonl, write_json


CASE_ORDER = [
    "faq_direct_answer",
    "troubleshooting",
    "step_by_step",
    "clarification",
    "uncertainty_escalation",
]


def _resolve(repo_root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return repo_root / path


def _dtype(dtype_name: str) -> torch.dtype:
    return {
        "bfloat16": torch.bfloat16,
        "bf16": torch.bfloat16,
        "float16": torch.float16,
        "fp16": torch.float16,
        "float32": torch.float32,
        "fp32": torch.float32,
    }[dtype_name.casefold()]


def _apply_chat_template(tokenizer: Any, messages: list[dict], add_generation_prompt: bool) -> str:
    kwargs = {"tokenize": False, "add_generation_prompt": add_generation_prompt}
    try:
        return tokenizer.apply_chat_template(messages, enable_thinking=False, **kwargs)
    except TypeError:
        return tokenizer.apply_chat_template(messages, **kwargs)


def _pick_smoke_rows(gold_eval_rows: list[dict]) -> list[dict]:
    picks: list[dict] = []
    for case_type in CASE_ORDER:
        matching = sorted(
            (row for row in gold_eval_rows if row.get("case_type") == case_type),
            key=lambda row: row["eval_id"],
        )
        if matching:
            picks.append(matching[0])
    return picks


def main() -> None:
    parser = make_parser("Load a trained Qwen LoRA adapter and run a small deterministic smoke test.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--adapter-dir", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    repo_root = find_repo_root(Path.cwd())
    config_path = _resolve(repo_root, args.config)
    adapter_dir = _resolve(repo_root, args.adapter_dir)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    manifest = read_json(_resolve(repo_root, config["dataset"]["manifest_file"]))
    gold_eval_path = _resolve(repo_root, manifest["source_eval_files"][0])
    gold_eval_rows = read_jsonl(gold_eval_path)
    smoke_rows = _pick_smoke_rows(gold_eval_rows)
    if len(smoke_rows) != len(CASE_ORDER):
        missing = [case for case in CASE_ORDER if case not in {row["case_type"] for row in smoke_rows}]
        raise SystemExit(f"Missing smoke-test case types: {missing}")

    tokenizer = AutoTokenizer.from_pretrained(
        config["model"]["tokenizer_name_or_path"],
        trust_remote_code=config["model"].get("trust_remote_code", False),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type=config["quantization"].get("bnb_4bit_quant_type", "nf4"),
        bnb_4bit_use_double_quant=config["quantization"].get("bnb_4bit_use_double_quant", True),
        bnb_4bit_compute_dtype=_dtype(config["quantization"].get("bnb_4bit_compute_dtype", "bfloat16")),
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        config["model"]["base_model"],
        trust_remote_code=config["model"].get("trust_remote_code", False),
        dtype=torch.bfloat16 if config["training"].get("bf16", False) else torch.float16,
        quantization_config=quantization_config,
        device_map="auto",
        low_cpu_mem_usage=True,
        attn_implementation=config["runtime"].get("attention_implementation"),
    )
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()

    results = []
    generation_cfg = config.get("inference", {})
    for row in smoke_rows:
        behavior_spec_path = ((row.get("provenance") or {}).get("behavior_spec_path")) or ""
        messages = []
        if behavior_spec_path:
            behavior_spec = _resolve(repo_root, behavior_spec_path).read_text(encoding="utf-8").strip()
            messages.append({"role": "system", "content": behavior_spec})
        messages.append({"role": "user", "content": row["prompt"]})
        prompt_text = _apply_chat_template(tokenizer, messages, add_generation_prompt=True)
        model_inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            generated = model.generate(
                **model_inputs,
                max_new_tokens=int(generation_cfg.get("max_new_tokens", 192)),
                do_sample=bool(generation_cfg.get("do_sample", False)),
                temperature=float(generation_cfg.get("temperature", 0.0)),
                top_p=float(generation_cfg.get("top_p", 1.0)),
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        generated_text = tokenizer.decode(
            generated[0][model_inputs["input_ids"].shape[1] :],
            skip_special_tokens=True,
        ).strip()
        results.append(
            {
                "eval_id": row["eval_id"],
                "case_type": row["case_type"],
                "prompt": row["prompt"],
                "generated_answer": generated_text,
                "reference_answer": row["reference_answer"],
                "source_chunk_ids": row.get("source_chunk_ids", []),
            }
        )

    output_path = (
        _resolve(repo_root, args.output)
        if args.output
        else adapter_dir.parent / "smoke_test_results.json"
    )
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "config_path": config_path.as_posix(),
        "adapter_dir": adapter_dir.as_posix(),
        "base_model": config["model"]["base_model"],
        "dataset_export_id": manifest.get("export_id"),
        "results": results,
    }
    write_json(output_path, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

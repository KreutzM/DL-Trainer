.PHONY: validate demo-export qwen-clean-gate

validate:
	python scripts/validate_metadata.py --input data/normalized/demo_product/de/manual_v1/index.meta.json
	python scripts/validate_jsonl.py --schema schemas/chunk.schema.json --input data/derived/chunks/demo_chunk_set.jsonl
	python scripts/check_provenance.py --input data/derived/task_cards/demo_task_cards.jsonl

demo-export:
	python scripts/export_for_training.py --input data/gold/train/sft/demo_sft_samples.jsonl --output training/exports/demo_train.jsonl

qwen-clean-gate:
	python scripts/run_qwen_clean_gate.py

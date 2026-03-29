.PHONY: validate demo-export teacher-proof-batch

validate:
	python scripts/validate_metadata.py --input data/normalized/demo_product/de/manual_v1/index.meta.json
	python scripts/validate_jsonl.py --schema schemas/chunk.schema.json --input data/derived/chunks/demo_chunk_set.jsonl
	python scripts/check_provenance.py --input data/derived/task_cards/demo_task_cards.jsonl

demo-export:
	python scripts/export_for_training.py --input data/gold/train/sft/demo_sft_samples.jsonl --output training/exports/demo_train.jsonl

teacher-proof-batch:
	python scripts/run_codex_cli_teacher_batch.py --jobs data/derived/teacher_jobs/JAWS/DE/qwen_step_focus_wave_v1_generation_jobs.jsonl --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_smoke_v1_job_ids.txt --raw-output data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_raw_responses.jsonl --teacher-output data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_teacher_outputs.jsonl --report-output data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_report.json --artifact-dir data/derived/teacher_runs/JAWS/DE/codex_cli_smoke_v1 --teacher-run-id jaws_de_codex_cli_smoke_v1 --teacher-model gpt-5.4 --reasoning-effort high --resume

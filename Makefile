.PHONY: validate repo-consistency jaws-de-current-validate jaws-de-current-export jaws-de-training-smoke jaws-de-fresh-run

CURRENT_JAWS_DE_RUN := codex_cli_support_validation_v2
CURRENT_JAWS_DE_TRAIN := data/gold/train/sft/JAWS/DE/$(CURRENT_JAWS_DE_RUN)_promoted_sft_samples.jsonl
CURRENT_JAWS_DE_EVAL := data/gold/eval/JAWS/DE/$(CURRENT_JAWS_DE_RUN)_promoted_eval_cases.jsonl
CURRENT_JAWS_DE_EXPORT_DIR := data/exports/qwen_sft/JAWS/DE/current
CURRENT_JAWS_DE_EXPORT_ID := jaws_de_validation_v2_current
CURRENT_JAWS_DE_TRAINING_CONFIG := training/transformers/jaws_de_current.yaml

validate: repo-consistency jaws-de-current-validate

repo-consistency:
	python -m pytest tests/test_repo_smoke.py tests/test_jaws_de_workflow_consistency.py

jaws-de-current-validate:
	python scripts/validate_jsonl.py --schema schemas/sft_sample.schema.json --input $(CURRENT_JAWS_DE_TRAIN)
	python scripts/check_provenance.py --input $(CURRENT_JAWS_DE_TRAIN)
	python scripts/validate_jsonl.py --schema schemas/eval_case.schema.json --input $(CURRENT_JAWS_DE_EVAL)
	python scripts/check_provenance.py --input $(CURRENT_JAWS_DE_EVAL)

jaws-de-current-export:
	python scripts/export_qwen_sft.py --train-input $(CURRENT_JAWS_DE_TRAIN) --eval-input $(CURRENT_JAWS_DE_EVAL) --output-dir $(CURRENT_JAWS_DE_EXPORT_DIR) --export-id $(CURRENT_JAWS_DE_EXPORT_ID)
	python scripts/validate_qwen_sft_export.py --input-dir $(CURRENT_JAWS_DE_EXPORT_DIR)

jaws-de-training-smoke:
	python scripts/smoke_test_qwen_sft.py --config $(CURRENT_JAWS_DE_TRAINING_CONFIG)

jaws-de-fresh-run:
	python -c "import sys; run_name = '$(RUN_NAME)'.strip(); sys.exit(0 if run_name else 'RUN_NAME is required')"
	python scripts/run_codex_cli_support_mvp_pipeline.py --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_validation_v1_job_ids.txt --run-name $(RUN_NAME) --promote

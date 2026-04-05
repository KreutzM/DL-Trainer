.PHONY: validate repo-consistency jaws-de-current-validate jaws-de-current-export jaws-de-current-training-smoke jaws-de-current-first-train jaws-de-current-second-train jaws-de-current-third-train jaws-de-current-fourth-train jaws-de-current-fifth-train jaws-de-current-sixth-train jaws-de-training-smoke jaws-de-fresh-run support-mvp-benchmark-reference support-mvp-benchmark-candidate support-mvp-benchmark-compare

CURRENT_JAWS_DE_BASELINE := docs/jaws_de_current_baseline.json
CURRENT_JAWS_DE_RUN := openrouter_gpt54_controlled_gold_v16
CURRENT_JAWS_DE_TRAIN := data/gold/train/sft/JAWS/DE/$(CURRENT_JAWS_DE_RUN)_promoted_sft_samples.jsonl
CURRENT_JAWS_DE_EVAL := data/gold/eval/JAWS/DE/$(CURRENT_JAWS_DE_RUN)_promoted_eval_cases.jsonl
CURRENT_JAWS_DE_EXPORT_DIR := data/exports/qwen_sft/JAWS/DE/current
CURRENT_JAWS_DE_EXPORT_ID := jaws_de_controlled_gold_v16_current
CURRENT_JAWS_DE_TRAINING_CONFIG := training/transformers/jaws_de_current.yaml
CURRENT_JAWS_DE_SELECTION := data/derived/teacher_jobs/JAWS/DE/current_generation_selection.json
SUPPORT_MVP_BENCHMARK_SELECTION := data/derived/teacher_jobs/JAWS/DE/current_generation_selection.json
SUPPORT_MVP_REFERENCE_PROFILE_SET := support_mvp_default
SUPPORT_MVP_CANDIDATE_PROFILE_SET := support_mvp_openrouter_candidate
SUPPORT_MVP_BENCHMARK_OUTPUT_DIR := data/derived/teacher_reviews/JAWS/DE/benchmarks

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

jaws-de-current-training-smoke:
	python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_smoke.yaml --summary-output training/transformers/outputs/jaws_de_current_smoke/preflight_summary.json
	python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_smoke.yaml
	python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_smoke.yaml --adapter-dir training/transformers/outputs/jaws_de_current_smoke/final_adapter --output training/transformers/outputs/jaws_de_current_smoke/adapter_smoke.json

jaws-de-current-first-train:
	python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_first_train.yaml --summary-output training/transformers/outputs/jaws_de_current_first_train/preflight_summary.json
	python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_first_train.yaml
	python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_first_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_first_train/final_adapter --output training/transformers/outputs/jaws_de_current_first_train/adapter_smoke.json

jaws-de-current-second-train:
	python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_second_train.yaml --summary-output training/transformers/outputs/jaws_de_current_second_train/preflight_summary.json
	python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_second_train.yaml
	python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_second_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_second_train/final_adapter --output training/transformers/outputs/jaws_de_current_second_train/adapter_smoke.json

jaws-de-current-third-train:
	python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_third_train.yaml --summary-output training/transformers/outputs/jaws_de_current_third_train/preflight_summary.json
	python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_third_train.yaml
	python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_third_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_third_train/final_adapter --output training/transformers/outputs/jaws_de_current_third_train/adapter_smoke.json

jaws-de-current-fourth-train:
	python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_fourth_train.yaml --summary-output training/transformers/outputs/jaws_de_current_fourth_train/preflight_summary.json
	python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_fourth_train.yaml
	python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_fourth_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_fourth_train/final_adapter --output training/transformers/outputs/jaws_de_current_fourth_train/adapter_smoke.json

jaws-de-current-fifth-train:
	python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_fifth_train.yaml --summary-output training/transformers/outputs/jaws_de_current_fifth_train/preflight_summary.json
	python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_fifth_train.yaml
	python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_fifth_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_fifth_train/final_adapter --output training/transformers/outputs/jaws_de_current_fifth_train/adapter_smoke.json

jaws-de-current-sixth-train:
	python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_sixth_train.yaml --summary-output training/transformers/outputs/jaws_de_current_sixth_train/preflight_summary.json
	python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_sixth_train.yaml
	python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_sixth_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_sixth_train/final_adapter --output training/transformers/outputs/jaws_de_current_sixth_train/adapter_smoke.json

jaws-de-training-smoke:
	python scripts/smoke_test_qwen_sft.py --config $(CURRENT_JAWS_DE_TRAINING_CONFIG)

jaws-de-fresh-run:
	python -c "import sys; run_name = '$(RUN_NAME)'.strip(); sys.exit(0 if run_name else 'RUN_NAME is required')"
	python scripts/run_codex_cli_support_mvp_pipeline.py --selection-manifest $(CURRENT_JAWS_DE_SELECTION) --run-name $(RUN_NAME) --promote

support-mvp-benchmark-reference:
	python -c "import sys; benchmark_name = '$(BENCHMARK_NAME)'.strip(); run_name = '$(RUN_NAME)'.strip(); sys.exit(0 if benchmark_name and run_name else 'BENCHMARK_NAME and RUN_NAME are required')"
	python scripts/run_codex_cli_support_mvp_pipeline.py --selection-manifest $(SUPPORT_MVP_BENCHMARK_SELECTION) --run-name $(RUN_NAME) --llm-profile-set $(SUPPORT_MVP_REFERENCE_PROFILE_SET) --benchmark-name $(BENCHMARK_NAME) --benchmark-role reference

support-mvp-benchmark-candidate:
	python -c "import sys; benchmark_name = '$(BENCHMARK_NAME)'.strip(); run_name = '$(RUN_NAME)'.strip(); sys.exit(0 if benchmark_name and run_name else 'BENCHMARK_NAME and RUN_NAME are required')"
	python scripts/run_codex_cli_support_mvp_pipeline.py --selection-manifest $(SUPPORT_MVP_BENCHMARK_SELECTION) --run-name $(RUN_NAME) --llm-profile-set $(SUPPORT_MVP_CANDIDATE_PROFILE_SET) --benchmark-name $(BENCHMARK_NAME) --benchmark-role candidate

support-mvp-benchmark-compare:
	python -c "import sys; benchmark_name = '$(BENCHMARK_NAME)'.strip(); reference_run = '$(REFERENCE_RUN)'.strip(); candidate_run = '$(CANDIDATE_RUN)'.strip(); sys.exit(0 if benchmark_name and reference_run and candidate_run else 'BENCHMARK_NAME, REFERENCE_RUN and CANDIDATE_RUN are required')"
	python scripts/compare_support_mvp_benchmarks.py --reference-run $(REFERENCE_RUN) --candidate-run $(CANDIDATE_RUN) --output $(SUPPORT_MVP_BENCHMARK_OUTPUT_DIR)/$(BENCHMARK_NAME)_comparison.json

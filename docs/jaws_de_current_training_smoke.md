# JAWS-DE Current Training Smoke

Zweck: kleiner, kontrollierter Export-/Trainings-Smoke auf dem aktuellen Current-Stand `openrouter_gpt54_controlled_gold_v16`.

## Verwendete Inputs

- Gold-Train: `data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl`
- Gold-Eval: `data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl`
- Current-Export: `data/exports/qwen_sft/JAWS/DE/current/`
- Smoke-Konfig: `training/transformers/jaws_de_current_smoke.yaml`

## Ausgefuehrte Schritte

1. Export neu gebaut und validiert:
   - `python scripts/export_qwen_sft.py --train-input data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl --eval-input data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl --output-dir data/exports/qwen_sft/JAWS/DE/current --export-id jaws_de_controlled_gold_v16_current`
   - `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/current`
2. Smoke-Vorpruefung gegen die lokale Windows-/CUDA-Umgebung:
   - `python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_smoke.yaml --summary-output training/transformers/outputs/jaws_de_current_smoke/preflight_summary.json`
3. Mini-Trainingslauf:
   - `python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_smoke.yaml`
4. Adapter-Smoke:
   - `python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_smoke.yaml --adapter-dir training/transformers/outputs/jaws_de_current_smoke/final_adapter --output training/transformers/outputs/jaws_de_current_smoke/adapter_smoke.json`

## Ergebnis

- Export lief sauber durch.
- Preflight war erfolgreich.
- Der Mini-Trainingslauf lief mit `max_steps=1`, `max_train_samples=4`, `max_eval_samples=2` auf dem aktuellen Current-Export.
- Der Adapter-Smoke konnte den frisch erzeugten Adapter laden und deterministische Inferenz ausfuehren.

## Einordnung

- Der neue Current-Stand ist praktisch export- und trainingsfaehig.
- Der Smoke ist bewusst klein und lokal auf Windows/CUDA kalibriert.
- Fuer einen groesseren Trainingslauf bleibt nur noch die reguläre Trainingsausfuehrung auf dem gleichen Current-Stand.

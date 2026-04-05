# JAWS-DE Current First Train

Zweck: erster echter, aber weiter kontrollierter Trainingslauf auf dem aktuellen Current-Stand `openrouter_gpt54_controlled_gold_v16`.

## Verwendete Inputs

- Gold-Train: `data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl`
- Gold-Eval: `data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl`
- Current-Export: `data/exports/qwen_sft/JAWS/DE/current/`
- Trainings-Config: `training/transformers/jaws_de_current_first_train.yaml`

## Laufparameter

- Model: `Qwen/Qwen3-8B`
- Quantisierung: 4-bit NF4
- LoRA: `r=16`, `alpha=32`
- `max_length=1024`
- `num_train_epochs=1`
- `max_steps=4`
- `per_device_train_batch_size=1`
- `gradient_accumulation_steps=1`
- `eval_steps=2`
- `save_steps=2`

## Ausgefuehrte Schritte

1. Export gegen den aktuellen Gold-Stand validiert:
   - `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/current`
2. Vorabcheck der Trainingsumgebung:
   - `python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_first_train.yaml --summary-output training/transformers/outputs/jaws_de_current_first_train/preflight_summary.json`
3. Erster echter kleiner Trainingslauf:
   - `python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_first_train.yaml`
4. Adapter-Smoke nach dem Training:
   - `python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_first_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_first_train/final_adapter --output training/transformers/outputs/jaws_de_current_first_train/adapter_smoke.json`

## Ergebnis

- Der Trainingslauf lief mit 4 echten Optimization Steps auf dem aktuellen Current-Export durch.
- Keine OOM-, Loader- oder Export-Reibung im Lauf.
- Der Adapter-Smoke konnte den erzeugten Adapter laden und fünf Standard-Fälle aus dem aktuellen Scope generieren.
- Der Lauf blieb klein, ist aber deutlich näher am echten Trainingspfad als der Smoke mit einem Schritt.

## Kurzbefund

- `faq_direct_answer` und `troubleshooting` bleiben stabil und knapp.
- `step_by_step` bleibt vorsichtig und beantwortet teils konservativ, aber der Pfad ist technisch stabil.
- `clarification` zeigt im kleinen Smoke noch keine robuste Präzision; das ist für diesen ersten Mini-Run erwartbar und kein technischer Blocker.

## Einordnung

- Der neue Current-Stand ist praktisch tragfähig für weitere echte Trainingsläufe.
- Als direkter nächster Schritt bietet sich ein etwas längerer, aber weiterhin kontrollierter Trainingslauf an, bevor man in einen größeren Hauptlauf geht.

# JAWS-DE Current Second Train

Zweck: zweiter echter, aber weiter kontrollierter Trainingslauf auf dem aktuellen Current-Stand `openrouter_gpt54_controlled_gold_v16`.

## Verwendete Inputs

- Gold-Train: `data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl`
- Gold-Eval: `data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl`
- Current-Export: `data/exports/qwen_sft/JAWS/DE/current/`
- Trainings-Config: `training/transformers/jaws_de_current_second_train.yaml`

## Laufparameter

- Model: `Qwen/Qwen3-8B`
- Quantisierung: 4-bit NF4
- LoRA: `r=16`, `alpha=32`
- `max_length=1024`
- `num_train_epochs=1`
- `max_steps=8`
- `per_device_train_batch_size=1`
- `gradient_accumulation_steps=1`
- `eval_steps=4`
- `save_steps=4`

## Ausgefuehrte Schritte

1. Export gegen den aktuellen Gold-Stand validiert:
   - `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/current`
2. Vorabcheck der Trainingsumgebung:
   - `python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_second_train.yaml --summary-output training/transformers/outputs/jaws_de_current_second_train/preflight_summary.json`
3. Zweiter kontrollierter Trainingslauf:
   - `python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_second_train.yaml`
4. Adapter-Smoke nach dem Training:
   - `python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_second_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_second_train/final_adapter --output training/transformers/outputs/jaws_de_current_second_train/adapter_smoke.json`

## Ergebnis

- Der Trainingslauf lief mit 8 echten Optimization Steps auf dem aktuellen Current-Export durch.
- Gemessene Kernwerte:
  - `train_loss = 1.8970330953598022`
  - `eval_loss = 1.7825261354446411`
  - `global_step = 8`
  - `train_rows = 27`
  - `eval_rows = 23`
- Keine OOM-, Loader- oder Export-Reibung im Lauf.
- Der Adapter-Smoke konnte den erzeugten Adapter laden und fünf Standardfaelle aus dem aktuellen Scope generieren.

## Kurzbefund

- `faq_direct_answer` bleibt brauchbar und knapp, wenn auch noch nicht besonders präzise.
- `troubleshooting` bleibt stabil, beantwortet aber teils noch generisch.
- `uncertainty_escalation` bleibt vorsichtig und verweigert keine klar belegtete Dokumentationslage unnötig.
- `step_by_step` bleibt konservativ und verweist in diesem kleinen Check weiterhin eher auf fehlende explizite Schritte als auf eine groessere Antwortspanne.
- `clarification` ist im kleinen Check weiterhin die sichtbar schwächste Klasse und wirkt eher paraphrasierend als wirklich klärend.

## Einordnung

- Der neue Current-Stand wirkt auch fuer einen etwas groesseren kontrollierten Trainingslauf tragfaehig.
- Als naechster Schritt bietet sich ein noch etwas laengerer, aber weiterhin kontrollierter Lauf an, bevor ein groesserer Trainingszyklus gestartet wird.

# JAWS-DE Current Third Train

Zweck: dritter, nochmals etwas laengerer, aber weiterhin kontrollierter Trainingslauf auf dem aktuellen Current-Stand `openrouter_gpt54_controlled_gold_v16`.

## Verwendete Inputs

- Gold-Train: `data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl`
- Gold-Eval: `data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl`
- Current-Export: `data/exports/qwen_sft/JAWS/DE/current/`
- Trainings-Config: `training/transformers/jaws_de_current_third_train.yaml`

## Laufparameter

- Model: `Qwen/Qwen3-8B`
- Quantisierung: 4-bit NF4
- LoRA: `r=16`, `alpha=32`
- `max_length=1024`
- `num_train_epochs=1`
- `max_steps=12`
- `per_device_train_batch_size=1`
- `gradient_accumulation_steps=1`
- `eval_steps=4`
- `save_steps=4`

## Ausgefuehrte Schritte

1. Export gegen den aktuellen Gold-Stand validiert:
   - `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/current`
2. Vorabcheck der Trainingsumgebung:
   - `python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_third_train.yaml --summary-output training/transformers/outputs/jaws_de_current_third_train/preflight_summary.json`
3. Dritter kontrollierter Trainingslauf:
   - `python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_third_train.yaml`
4. Adapter-Smoke nach dem Training:
   - `python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_third_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_third_train/final_adapter --output training/transformers/outputs/jaws_de_current_third_train/adapter_smoke.json`

## Ergebnis

- Der Trainingslauf lief mit 12 echten Optimization Steps auf dem aktuellen Current-Export durch.
- Gemessene Kernwerte:
  - `train_loss = 1.7134862343470256`
  - `eval_loss = 1.7696441411972046`
  - `global_step = 12`
  - `train_rows = 27`
  - `eval_rows = 23`
- Keine OOM-, Loader- oder Export-Reibung im Lauf.
- Der Adapter-Smoke konnte den erzeugten Adapter laden und fuenf Standardfaelle aus dem aktuellen Scope generieren.

## Trend

- Run 1: `train_loss = 1.7948`, `eval_loss = 1.8447`, `global_step = 4`
- Run 2: `train_loss = 1.8970`, `eval_loss = 1.7825`, `global_step = 8`
- Run 3: `train_loss = 1.7135`, `eval_loss = 1.7696`, `global_step = 12`
- Einordnung: der Eval-Score verbessert sich ueber die drei kontrollierten Laeufe schrittweise; der dritte Lauf ist damit die bisher beste praktische Stabilitaetsmarke.

## Kurzbefund

- `clarification` bleibt die schwaechste Klasse und wirkt weiterhin eher paraphrasierend als praezise klaerend.
- `faq_direct_answer` bleibt brauchbar und knapp.
- `troubleshooting` bleibt stabil und regelorientiert.
- `uncertainty_escalation` bleibt vorsichtig und dokumentationsnah.
- `step_by_step` bleibt konservativ, aber nicht instabil.

## Qualitative Probe-Bewertung

| Klasse | Was gut war | Was schwach blieb | Naeher am Gold? |
| --- | --- | --- | --- |
| `faq_direct_answer` | Antwort bleibt kurz, direkt und thematisch passend. | Noch zu allgemein, konkrete Quellelemente fehlen. | Ja, etwas naeher als die ersten Runs, aber noch nicht voll praezise. |
| `troubleshooting` | Modell benennt das relevante Konzept und bleibt im Dokumentationsrahmen. | Noch generisch; die konkrete Aenderungsaktion fehlt. | Teilweise. |
| `step_by_step` | Modell verweigert keine offensichtliche Halluzination und bleibt defensiv. | Weiter konservativ; die echte Schrittfolge wird noch nicht ausgefuehrt. | Nur leicht. |
| `clarification` | Paraphrasiert die gemeinte Bedeutung sauberer als in den Mini-Runs. | Wirkt noch nicht wie eine wirklich starke Rueckfrage, eher wie eine Antwort. | Leicht, aber weiterhin die schwaechste Klasse. |
| `uncertainty_escalation` | Markiert Unsicherheit und vermeidet Ueberbehauptung. | Antwort bleibt knapp; die dokumentierte Einordnung koennte klarer sein. | Ja, aber moderat. |

## Einordnung

- Der neue Current-Stand wirkt auch fuer einen noch etwas laenger laufenden, kontrollierten Trainingszyklus tragfaehig.
- Nach Abschluss des Laufs spricht das Trendbild dafuer, dass ein groesserer Trainingszyklus jetzt vertretbar ist.
- Gleichzeitig bleibt `clarification` die sichtbar schwaechste Klasse und sollte im naechsten Zyklus aktiv beobachtet werden.

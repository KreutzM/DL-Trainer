# JAWS-DE Current Seventh Train

Zweck: siebter, produktionsnaher aber weiterhin kontrollierter lokaler Trainingslauf auf dem aktuellen Current-Stand `openrouter_gpt54_controlled_gold_v16`.

## Verwendete Inputs

- Gold-Train: `data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl`
- Gold-Eval: `data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl`
- Current-Export: `data/exports/qwen_sft/JAWS/DE/current/`
- Trainings-Config: `training/transformers/jaws_de_current_seventh_train.yaml`

## Laufparameter

- Model: `Qwen/Qwen3-8B`
- Quantisierung: 4-bit NF4
- LoRA: `r=16`, `alpha=32`
- `max_length=1024`
- `num_train_epochs=1`
- `max_steps=48`
- `per_device_train_batch_size=1`
- `gradient_accumulation_steps=1`
- `eval_steps=12`
- `save_steps=12`

## Ausgefuehrte Schritte

1. Export gegen den aktuellen Gold-Stand validiert:
   - `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/current`
2. Vorabcheck der Trainingsumgebung:
   - `python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_seventh_train.yaml --summary-output training/transformers/outputs/jaws_de_current_seventh_train/preflight_summary.json`
3. Siebter kontrollierter Trainingslauf:
   - `python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_seventh_train.yaml`
4. Adapter-Smoke nach dem Training:
   - `python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_seventh_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_seventh_train/final_adapter --output training/transformers/outputs/jaws_de_current_seventh_train/adapter_smoke.json`

## Ergebnis

- Der Trainingslauf lief mit 48 echten Optimization Steps auf dem aktuellen Current-Export durch.
- Gemessene Kernwerte:
  - `train_loss = 1.4066754281520844`
  - `eval_loss = 1.6418606042861938`
  - `global_step = 48`
  - `train_rows = 27`
  - `eval_rows = 23`
- Keine OOM-, Loader- oder Export-Reibung im Lauf.
- Der Adapter-Smoke konnte den erzeugten Adapter laden und fuenf Standardfaelle aus dem aktuellen Scope generieren.

## Trend

- Run 1: `train_loss = 1.7948`, `eval_loss = 1.8447`, `global_step = 4`
- Run 2: `train_loss = 1.8970`, `eval_loss = 1.7825`, `global_step = 8`
- Run 3: `train_loss = 1.7135`, `eval_loss = 1.7696`, `global_step = 12`
- Run 4: `train_loss = 1.7093`, `eval_loss = 1.7600`, `global_step = 16`
- Run 5: `train_loss = 1.6673`, `eval_loss = 1.7225`, `global_step = 24`
- Run 6: `train_loss = 1.5700`, `eval_loss = 1.6845`, `global_step = 32`
- Run 7: `train_loss = 1.4067`, `eval_loss = 1.6419`, `global_step = 48`
- Einordnung: der 48-Step-Lauf prueft den Current-Stand schon nah an einem produktionsnahen lokalen Zyklus, bleibt aber weiterhin kontrolliert.

## Kurzbefund

- `clarification` bleibt die sichtbar schwaechste Klasse und wirkt weiterhin eher paraphrasierend als praezise klaerend.
- `faq_direct_answer` bleibt tragfaehig und direkt.
- `troubleshooting` bleibt tragfaehig und regelorientiert.
- `uncertainty_escalation` kann noch zu selbstsicher werden und braucht weiter Beobachtung.
- `step_by_step` bleibt konservativ statt instabil.

## Qualitative Probe-Bewertung

| Klasse | Erwartete Tendenz | Beobachtete Antwortqualitaet | Auffaellige Schwaechen |
| --- | --- | --- | --- |
| `clarification` | Echte Rueckfrage zur Praezisierung. | Bleibt klarer formuliert als fruehe Laeufe, fragt aber immer noch nicht sauber zurueck. | Weiter Antwortton statt echter Rueckfrage. |
| `faq_direct_answer` | Kurze, konkrete Dokumentationsantwort. | Greift den Kern direkt auf und bleibt lesbar. | Fuegt noch immer unbelegte Zusatzdetails hinzu. |
| `step_by_step` | Vollstaendige, operative Schrittfolge. | Bleibt konservativ und halluziniert keine Schritte. | Kippt hier sogar in eine Rueckfrage statt in eine Prozedur. |
| `troubleshooting` | Konkreter, dokumentierter Hinweis mit Handlung. | Stabil und knapp, aber leicht strukturierter als in Run 5. | Der konkrete Handlungsschritt bleibt knapp. |
| `uncertainty_escalation` | Unsicherheit markieren und korrekt begrenzen. | Formuliert zu sicher und macht eine nicht belegte Aussage ueber den aktiven Zustand. | Schwachste Probe in diesem Run; fachlich eher ein Rueckschritt. |

## Einordnung

- Der neue Current-Stand bleibt robust genug fuer einen produktionsnahen lokalen Trainingszyklus.
- Gegenueber Run 5 sind die Loss-Werte deutlich besser; gegenueber Run 6 ist der Lauf laenger und damit produktionsnaher.
- `clarification` bleibt die Klasse mit dem hoechsten Beobachtungsbedarf.
- `uncertainty_escalation` bleibt die naechste Klasse, die noch zu selbstsicher wirken kann.

## Schlussfolgerung

- Der neue Current-Stand ist fuer regulaere lokale Trainingszyklen geeignet.
- Ein weiterer kontrollierter Zwischenlauf ist dafuer nicht erforderlich.


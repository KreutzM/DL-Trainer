# JAWS-DE Current Sixth Train

Zweck: sechster, groesserer aber weiterhin kontrollierter lokaler Trainingslauf auf dem aktuellen Current-Stand `openrouter_gpt54_controlled_gold_v16`.

## Verwendete Inputs

- Gold-Train: `data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl`
- Gold-Eval: `data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl`
- Current-Export: `data/exports/qwen_sft/JAWS/DE/current/`
- Trainings-Config: `training/transformers/jaws_de_current_sixth_train.yaml`

## Laufparameter

- Model: `Qwen/Qwen3-8B`
- Quantisierung: 4-bit NF4
- LoRA: `r=16`, `alpha=32`
- `max_length=1024`
- `num_train_epochs=1`
- `max_steps=32`
- `per_device_train_batch_size=1`
- `gradient_accumulation_steps=1`
- `eval_steps=8`
- `save_steps=8`

## Ausgefuehrte Schritte

1. Export gegen den aktuellen Gold-Stand validiert:
   - `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/current`
2. Vorabcheck der Trainingsumgebung:
   - `python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_sixth_train.yaml --summary-output training/transformers/outputs/jaws_de_current_sixth_train/preflight_summary.json`
3. Sechster kontrollierter Trainingslauf:
   - `python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_sixth_train.yaml`
4. Adapter-Smoke nach dem Training:
   - `python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_sixth_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_sixth_train/final_adapter --output training/transformers/outputs/jaws_de_current_sixth_train/adapter_smoke.json`

## Ergebnis

- Der Trainingslauf lief mit 32 echten Optimization Steps auf dem aktuellen Current-Export durch.
- Gemessene Kernwerte:
  - `train_loss = 1.5700154341757298`
  - `eval_loss = 1.6845097541809082`
  - `global_step = 32`
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
- Einordnung: der 32-Step-Lauf ist der bisher ernsthafteste lokale Zwischenlauf. Der Eval-Score verbessert sich weiter und bleibt ohne technische Nebenwirkungen stabil.

## Kurzbefund

- `clarification` bleibt die sichtbar schwaechste Klasse und wirkt weiterhin eher paraphrasierend als praezise klaerend.
- `faq_direct_answer` bleibt brauchbar und direkt.
- `troubleshooting` bleibt stabil und regelorientiert.
- `uncertainty_escalation` bleibt zwar vorsichtig, ist im Probe-Run aber noch zu selbstsicher geworden.
- `step_by_step` bleibt konservativ, aber nicht instabil.

## Qualitative Probe-Bewertung

| Klasse | Erwartete Tendenz | Beobachtete Antwortqualitaet | Auffaellige Schwaechen |
| --- | --- | --- | --- |
| `clarification` | Echte Rueckfrage zur Praezisierung. | Bleibt inhaltlich brauchbar, ist aber weiter als Antwort statt als echte Rueckfrage formuliert. | Kein klarer Fortschritt gegenueber Run 5. |
| `faq_direct_answer` | Kurze, konkrete Dokumentationsantwort. | Trifft den Dokumentationskern besser und bleibt direkt. | Noch immer etwas ungenau und nicht vollstaendig. |
| `step_by_step` | Vollstaendige, operative Schrittfolge. | Bleibt defensiv und halluziniert keine Schritte. | Weiter nicht operativ genug; eher sichere Minimalantwort. |
| `troubleshooting` | Konkreter, dokumentierter Hinweis mit Handlung. | Bleibt stabil und leicht strukturierter als zuvor. | Handlungsschritt ist noch etwas knapp. |
| `uncertainty_escalation` | Unsicherheit markieren und korrekt begrenzen. | Formuliert zu sicher und nennt eine nicht belegte Handlungsanweisung. | Schwachste Probe in diesem Run; gegenueber Run 5 eher schlechter. |

## Einordnung

- `clarification`:
  - Weiterhin eher Antwort als echte Rueckfrage.
  - Gegenueber Run 5 kein klarer qualitativer Sprung.
- `faq_direct_answer`:
  - Etwas besser auf den Dokumentationskern fokussiert als Run 5.
  - Noch nicht vollstaendig praezise, aber brauchbar.
- `step_by_step`:
  - Weiter konservativ und sauber ohne Halluzinationen.
  - Praktisch stabil, aber noch nicht operativ genug.
- `troubleshooting`:
  - Gegenueber Run 5 leicht strukturierter.
  - Immer noch eher knapp als ausformuliert.
- `uncertainty_escalation`:
  - In diesem Probe-Run schwacher als Run 5, weil die Antwort zu sicher formuliert und eine nicht belegte Handlungsanweisung gegeben hat.

## Schlussfolgerung

- Der neue Current-Stand ist fuer regulaere lokale Trainingszyklen tragfaehig.
- Die Loss-Entwicklung ist stabil und verbessert sich weiter, ohne technische Nebenwirkungen.
- Qualitativ bleiben `clarification` und `uncertainty_escalation` die Klassen mit dem hoechsten Beobachtungsbedarf.
- Fuer den naechsten Schritt ist kein weiterer kontrollierter Zwischenlauf notwendig; ein ernsthafter lokaler Trainingslauf ist vertretbar.

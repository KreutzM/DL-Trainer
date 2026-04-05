# JAWS-DE Current Fifth Train

Zweck: fuenfter, groesserer aber weiterhin kontrollierter lokaler Trainingslauf auf dem aktuellen Current-Stand `openrouter_gpt54_controlled_gold_v16`.

## Verwendete Inputs

- Gold-Train: `data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl`
- Gold-Eval: `data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl`
- Current-Export: `data/exports/qwen_sft/JAWS/DE/current/`
- Trainings-Config: `training/transformers/jaws_de_current_fifth_train.yaml`

## Laufparameter

- Model: `Qwen/Qwen3-8B`
- Quantisierung: 4-bit NF4
- LoRA: `r=16`, `alpha=32`
- `max_length=1024`
- `num_train_epochs=1`
- `max_steps=24`
- `per_device_train_batch_size=1`
- `gradient_accumulation_steps=1`
- `eval_steps=6`
- `save_steps=6`

## Ausgefuehrte Schritte

1. Export gegen den aktuellen Gold-Stand validiert:
   - `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/current`
2. Vorabcheck der Trainingsumgebung:
   - `python scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current_fifth_train.yaml --summary-output training/transformers/outputs/jaws_de_current_fifth_train/preflight_summary.json`
3. Fuenfter kontrollierter Trainingslauf:
   - `python scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current_fifth_train.yaml`
4. Adapter-Smoke nach dem Training:
   - `python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/jaws_de_current_fifth_train.yaml --adapter-dir training/transformers/outputs/jaws_de_current_fifth_train/final_adapter --output training/transformers/outputs/jaws_de_current_fifth_train/adapter_smoke.json`

## Ergebnis

- Der Trainingslauf lief mit 24 echten Optimization Steps auf dem aktuellen Current-Export durch.
- Gemessene Kernwerte:
  - `train_loss = 1.6673318147659302`
  - `eval_loss = 1.7224960327148438`
  - `global_step = 24`
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
- Einordnung: der 24-Step-Lauf prueft den Current-Stand deutlich ernster; der Eval-Score verbessert sich weiter und ist jetzt klar der bisher beste Wert.

## Kurzbefund

- `clarification` bleibt die sichtbar schwächste Klasse und verfehlt noch die Form einer echten Rueckfrage.
- `faq_direct_answer` bleibt brauchbar und direkt, liefert aber noch keine vollstaendige Detailtiefe.
- `troubleshooting` bleibt stabil und handlungsorientiert, ist aber noch etwas knapp.
- `uncertainty_escalation` bleibt vorsichtig, kann aber noch zu stark in unbelegte Sicherheit kippen.
- `step_by_step` bleibt konservativ, aber nicht instabil.

## Qualitative Probe-Bewertung

| Klasse | Erwartete Tendenz | Beobachtete Antwortqualität | Auffällige Schwächen |
| --- | --- | --- | --- |
| `clarification` | Echte Rückfrage zur Präzisierung. | Antwort bleibt klarer als in den frühen Läufen, ist aber noch keine saubere Rückfrage. | Zu viel Antwortton, zu wenig echtes Nachfragen. |
| `faq_direct_answer` | Kurze, konkrete Dokumentationsantwort. | Antwort trifft die richtige Stelle und bleibt knapp. | Noch etwas zu allgemein, Details fehlen. |
| `step_by_step` | Vollständige, operative Schrittfolge. | Modell bleibt defensiv und halluziniert keine Schritte. | Noch kein wirklich operativer Ablauf; nur begrenzte Struktur. |
| `troubleshooting` | Konkreter, dokumentierter Hinweis mit Handlung. | Greift das relevante Fensterklassen-Thema jetzt spezifischer auf. | Der Umsetzungsschritt bleibt noch etwas vage. |
| `uncertainty_escalation` | Unsicherheit markieren und korrekt begrenzen. | Erkennt Unsicherheit an, bleibt aber teils zu selbstsicher. | Kann die dokumentierte Begrenzung sauberer treffen. |

## Einordnung

- Der neue Current-Stand wirkt auch fuer einen noch groesser angelegten, kontrollierten Trainingszyklus tragfaehig.
- Nach Abschluss des Laufs spricht das Trendbild klar fuer einen ersten produktionsnahen lokalen Trainingslauf, ohne weitere OpenAI-/OpenRouter-Datengenerierung.
- `clarification` und `uncertainty_escalation` bleiben die beiden Klassen, die im naechsten Lauf am ehesten weiter beobachtet werden sollten.

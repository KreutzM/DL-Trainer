# Qwen3-8B JAWS-DE LoRA Pilot

## Ziel

Dieser Pilot zieht den ersten echten lokalen Qwen3-8B-LoRA/SFT-Lauf auf dem aktuell voll validierten JAWS-DE-Clean-Stand durch.

## Datensatzentscheidung

- Verwendet wird bewusst `data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl` plus `data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl`.
- Zugehoeriger Export: `data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326/`.
- Der groessere Stand `consolidated_gold_v1_lora_pilot_clean_*` bleibt ausserhalb dieses ersten echten Laufs, weil der aktuelle Source-Faithfulness-Gate-Check dort noch Flag-Faelle meldet.

## Reproduzierbarer Ablauf

1. Gold- und Export-Validierung:
   - `python scripts/validate_jsonl.py --schema schemas/sft_sample.schema.json --input data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl`
   - `python scripts/validate_jsonl.py --schema schemas/eval_case.schema.json --input data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl`
   - `python scripts/check_provenance.py --input data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl`
   - `python scripts/check_provenance.py --input data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl`
   - `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326`
2. Technik-Check:
   - `python scripts/run_qwen_lora_pilot.py --config training/transformers/qwen3_8b_jaws_de_lora_clean_pilot_v1_dry_run.yaml`
3. Echter Pilot:
   - `python scripts/run_qwen_lora_pilot.py --config training/transformers/qwen3_8b_jaws_de_lora_clean_pilot_v1.yaml`
4. Adapter-Smoke-Test:
   - `python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/qwen3_8b_jaws_de_lora_clean_pilot_v1.yaml --adapter-dir training/transformers/outputs/qwen3_8b_jaws_de_lora_clean_pilot_v1/final_adapter`

## Hardwareprofil

- Zielmaschine fuer diesen Pilot: 1x RTX 3060 mit 12 GB VRAM
- Konsequenz: konservativer 4-Bit-QLoRA-Lauf mit `max_length: 1280`, `batch_size: 1`, `gradient_accumulation_steps: 16`, `num_train_epochs: 1`

## Tatsaechlich ausgefuehrter Pilotlauf

- Der erste laengere Lauf mit `qwen3_8b_jaws_de_lora_clean_pilot_v1.yaml` war auf dieser Windows-Maschine nicht stabil genug und endete in einem `nvlddmkm`-Treiberreset.
- Der erfolgreich durchgelaufene echte Pilot wurde deshalb mit `training/transformers/qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry.yaml` ausgefuehrt.
- Wesentliche Unterschiede des erfolgreichen Laufs:
  - `max_length: 1024`
  - keine Eval-Schleifen waehrend des Trainings
  - fruehe Checkpoints alle `10` Schritte
  - konservativere LoRA-Zielmodule `q_proj`, `k_proj`, `v_proj`, `o_proj`

## Ergebnis des erfolgreichen Laufs

- Datensatz: `689` Train / `82` Eval aus `jaws_de_consolidated_gold_v1_lora_clean_20260326`
- Laufstatus: vollstaendig durchgelaufen
- Global Steps: `50`
- Train Runtime: `1816.63` Sekunden
- Finaler Train Loss: `1.1714`
- Finaler Eval Loss: `2.0146`
- Adapter-Artefakt:
  - `training/transformers/outputs/qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry/final_adapter`
- Report-Dateien:
  - `training/transformers/outputs/qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry/run_summary.json`
  - `training/transformers/outputs/qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry/smoke_test_results.json`

## Ehrliche Ersteinschaetzung

- Technisch ist die Strecke jetzt geschlossen: Datensatz -> Training -> Adapter -> Inferenz-Smoke-Test.
- Inhaltlich ist der Pilot noch schwach.
- Im Smoke-Test zeigt der Adapter zwar ein engeres, deterministisches Supportformat, verfehlt aber mehrfach die dokumentationsgebundene Antwort:
  - FAQ: falsche Negation statt dokumentierter Kurzdefinition
  - Troubleshooting: weicht auf unpassende Textzeilen-Hilfe aus
  - Schrittfolge: liefert formale Schritte, aber falschen Bedienpfad
  - Rueckfrage: beantwortet spekulativ statt sauber einzugrenzen
  - Eskalation: antwortet zu absolut statt Unsicherheit korrekt zu markieren

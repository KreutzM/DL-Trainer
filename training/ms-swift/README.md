# ms-swift

Dieser Ordner haelt die erste reproduzierbare Startstrecke fuer den lokalen Qwen3-8B-LoRA-Lauf.

## Dateien

- `qwen3_8b_jaws_de_lora_clean.yaml` ist die Basiskonfiguration fuer den bevorzugten bereinigten JAWS-DE-SFT-Lauf.
- `qwen3_8b_jaws_de_lora_clean_dry_run.yaml` ist die kleine Smoke-Konfiguration fuer Loader-, Split- und Kommando-Pruefung des Clean-Stands.
- `qwen3_8b_jaws_de_lora.yaml` und `qwen3_8b_jaws_de_lora_dry_run.yaml` bleiben als aelterer `gold_v1`-Pfad erhalten.

## Empfohlene Reihenfolge

1. `make qwen-clean-gate` oder `python scripts/run_qwen_clean_gate.py`
2. Falls der Export separat geprueft werden soll: `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326`
3. `python scripts/smoke_test_qwen_sft.py --config training/ms-swift/qwen3_8b_jaws_de_lora_clean_dry_run.yaml`
4. Danach das ausgegebene `swift sft`-Kommando erst lokal mit installiertem MS-SWIFT ausfuehren.

## Noch manuell pruefen vor dem ersten echten Lauf

- Hugging-Face-Modellzugriff fuer `Qwen/Qwen3-8B`
- GPU-Speicher und BF16-Unterstuetzung
- ob `flash_attention_2` in der Zielumgebung verfuegbar ist
- ob die bereinigte Gold-Menge fuer den geplanten Lauf ausreicht oder vorab weitere reviewte Beispiele promotet werden sollen

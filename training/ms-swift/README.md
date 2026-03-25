# ms-swift

Dieser Ordner haelt die erste reproduzierbare Startstrecke fuer den lokalen Qwen3-8B-LoRA-Lauf.

## Dateien

- `qwen3_8b_jaws_de_lora.yaml` ist die Basiskonfiguration fuer den ersten echten JAWS-DE-SFT-Lauf.
- `qwen3_8b_jaws_de_lora_dry_run.yaml` ist die kleine Smoke-Konfiguration fuer Loader-, Split- und Kommando-Pruefung.

## Empfohlene Reihenfolge

1. Gold-Daten nach `data/exports/qwen_sft/JAWS/DE/gold_v1/` exportieren.
2. `python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/gold_v1`
3. `python scripts/smoke_test_qwen_sft.py --config training/ms-swift/qwen3_8b_jaws_de_lora_dry_run.yaml`
4. Danach das ausgegebene `swift sft`-Kommando erst lokal mit installiertem MS-SWIFT ausfuehren.

## Noch manuell pruefen vor dem ersten echten Lauf

- Hugging-Face-Modellzugriff fuer `Qwen/Qwen3-8B`
- GPU-Speicher und BF16-Unterstuetzung
- ob `flash_attention_2` in der Zielumgebung verfuegbar ist
- ob die kleine Gold-Menge fuer einen ersten Testlauf ausreicht oder vorab weitere reviewte Beispiele promotet werden sollen

# Qwen Export und erster Trainingslauf

## Ziel

Diese Stufe macht aus reviewten Gold-Daten einen direkt ladbaren Qwen-SFT-Export und legt die erste reproduzierbare Trainingskonfiguration fuer `Qwen/Qwen3-8B` an.

## Datenfluss

```text
data/gold/train/... + data/gold/eval/...
  -> scripts/export_qwen_sft.py
  -> data/exports/qwen_sft/JAWS/DE/gold_v1/
  -> scripts/validate_qwen_sft_export.py
  -> scripts/smoke_test_qwen_sft.py
  -> training/ms-swift/qwen3_8b_jaws_de_lora*.yaml
  -> erster echter LoRA-Lauf
```

## Exportstruktur

Unter `data/exports/qwen_sft/JAWS/DE/gold_v1/` liegen:

- `train.jsonl`: direkt trainierbare Chat-Beispiele im `messages`-Format
- `eval.jsonl`: eval-seitig ebenfalls als `messages`, aus Gold-Eval mit `prompt` + `reference_answer` gebaut
- `train.metadata.jsonl`: Provenance, Chunk-Referenzen und Gold-Status fuer Train
- `eval.metadata.jsonl`: Rubrik, Provenance und Gold-Referenzen fuer Eval
- `manifest.json`: Zaehler, Dateipfade und SHA256-Hashes

## Was im Export bleibt

- `messages` fuer den eigentlichen SFT-Loader
- `id` pro Beispiel
- vollstaendige Provenance und Gold-Herkunft in den Sidecar-Metadaten
- klare Trennung von `train` und `eval`

## Was bewusst nur in Metadaten bleibt

- `source_doc_ids`
- `source_chunk_ids`
- `teacher_run_id`
- `teacher_model`
- `promoted_from`
- Eval-Rubriken und `expected_behavior`

Das haelt den eigentlichen Trainings-Loader schlicht, ohne Rueckverfolgbarkeit zu verlieren.

## Export ausfuehren

```bash
python scripts/export_qwen_sft.py ^
  --train-input data/gold/train/sft/JAWS/DE/promoted_seed_sft_samples.jsonl ^
  --eval-input data/gold/eval/JAWS/DE/promoted_seed_eval_cases.jsonl ^
  --output-dir data/exports/qwen_sft/JAWS/DE/gold_v1 ^
  --export-id jaws_de_qwen_sft_gold_v1
```

## Export pruefen

```bash
python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/gold_v1
```

Der Validator prueft:

- Pflichtdateien vorhanden
- `messages`-Struktur parsebar
- keine leeren Assistant-Nachrichten
- Export-IDs und Sidecar-Metadaten konsistent
- keine Chunk-Kollisionen zwischen `train` und `eval`

## Dry-Run und echter Run

```bash
python scripts/smoke_test_qwen_sft.py --config training/ms-swift/qwen3_8b_jaws_de_lora_dry_run.yaml
python scripts/smoke_test_qwen_sft.py --config training/ms-swift/qwen3_8b_jaws_de_lora.yaml
```

Das Smoke-Test-Script:

- validiert die YAML-Konfiguration gegen `schemas/qwen_training_config.schema.json`
- prueft Train/Eval-Dateien und Sidecars
- prueft Split-Trennung auf Chunk-Ebene
- gibt das reproduzierbare `swift sft`-Kommando fuer den naechsten Schritt aus

## Vor dem ersten echten LoRA-Lauf noch manuell pruefen

- ob weitere reviewte Gold-Beispiele promotet werden sollen
- ob die Zielmaschine Zugriff auf `Qwen/Qwen3-8B` hat
- ob MS-SWIFT installiert und im Pfad verfuegbar ist
- ob die GPU-Ressourcen fuer die gewaehlte Sequenzlaenge reichen
- ob Eval-Loss auf dem kleinen Holdout als technischer Check ausreicht oder spaeter eine separate Antwortbewertung folgen soll

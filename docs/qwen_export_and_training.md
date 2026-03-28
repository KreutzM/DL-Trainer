# Qwen Export und Clean-Trainingslauf

## Ziel

Diese Stufe macht aus reviewten Gold-Daten einen direkt ladbaren Qwen-SFT-Export und legt die reproduzierbaren Trainingskonfigurationen fuer `Qwen/Qwen3-8B` an. Der bevorzugte Pfad laeuft ueber den bereinigten Clean-Stand.

## Datenfluss

```text
data/gold/train/... + data/gold/eval/...
  -> scripts/cleanup_qwen_sft_gold.py
  -> scripts/audit_qwen_source_faithfulness.py
  -> scripts/export_qwen_sft.py
  -> data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326/
  -> scripts/validate_qwen_sft_export.py
  -> scripts/smoke_test_qwen_sft.py
  -> training/ms-swift/qwen3_8b_jaws_de_lora_clean*.yaml
  -> erster echter LoRA-Lauf
```

## Exportstruktur

Unter `data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326/` liegen:

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

## Empfohlener Ablauf

### 1. Clean-Gate ausfuehren

```bash
make qwen-clean-gate
```

Ohne `make`:

```bash
python scripts/run_qwen_clean_gate.py
```

### 2. Export manuell ausfuehren

```bash
python scripts/export_qwen_sft.py ^
  --train-input data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl ^
  --eval-input data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl ^
  --output-dir data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326 ^
  --export-id jaws_de_consolidated_gold_v1_lora_clean_20260326
```

### 3. Export pruefen

```bash
python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326
```

Der Validator prueft:

- Pflichtdateien vorhanden
- `messages`-Struktur parsebar
- keine leeren Assistant-Nachrichten
- Export-IDs und Sidecar-Metadaten konsistent
- keine Chunk-Kollisionen zwischen `train` und `eval`

### 4. Dry-Run und echter Run

```bash
python scripts/smoke_test_qwen_sft.py --config training/ms-swift/qwen3_8b_jaws_de_lora_clean_dry_run.yaml
python scripts/smoke_test_qwen_sft.py --config training/ms-swift/qwen3_8b_jaws_de_lora_clean.yaml
```

Das Smoke-Test-Script:

- validiert die YAML-Konfiguration gegen `schemas/qwen_training_config.schema.json`
- prueft Train/Eval-Dateien und Sidecars
- prueft Split-Trennung auf Chunk-Ebene
- gibt das reproduzierbare `swift sft`-Kommando fuer den naechsten Schritt aus

## Gate vor dem Export

Der Clean-Gate-Lauf stellt sicher, dass:

- Stub- und Artefakt-Faelle entfernt sind
- Source-Faithfulness fuer Train und Eval auf `0` verbleibende Flags geprueft ist
- der Export und der MS-SWIFT-Dry-Run weiter konsistent sind

## Vor dem ersten echten LoRA-Lauf noch manuell pruefen

- ob weitere reviewte Gold-Beispiele promotet werden sollen
- ob die Zielmaschine Zugriff auf `Qwen/Qwen3-8B` hat
- ob MS-SWIFT installiert und im Pfad verfuegbar ist
- ob die GPU-Ressourcen fuer die gewaehlte Sequenzlaenge reichen
- ob Eval-Loss auf dem kleinen Holdout als technischer Check ausreicht oder spaeter eine separate Antwortbewertung folgen soll

## Historischer Hinweis

Der fruehere Beispielpfad `data/exports/qwen_sft/JAWS/DE/gold_v1/` bleibt aus Rueckverfolgbarkeitsgruenden im Repository, ist aber nicht mehr der empfohlene Standard fuer den JAWS-DE-LoRA-Lauf.

## Server-Ready 4090 v2

Fuer den naechsten echten Linux-Cloud-Run ist der eingefrorene Export `data/exports/qwen_sft/JAWS/DE/qwen3_8b_jaws_de_lora_4090_v3_20260328/` zusammen mit der Config `training/transformers/qwen3_8b_jaws_de_lora_4090_v3.yaml` vorgesehen. Der komplette Startpfad mit Preflight, Startskript, Resume und Post-Run-Smoke-Test ist in `docs/qwen3_8b_jaws_de_lora_4090_v3_runbook.md` beschrieben. Fuer Slurm-/Cluster-Hosts gibt es zusaetzlich `docs/qwen3_8b_jaws_de_lora_4090_v3_cluster_runbook.md`; das passende Environment-Bootstrap liefert `scripts/bootstrap_qwen_server_4090_env.sh`.

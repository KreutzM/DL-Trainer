# Qwen LoRA Dataset Cleanup

## Ziel

Diese Stufe bereitet den konsolidierten JAWS-DE-Gold-Stand fuer einen saubereren Qwen-LoRA-Lauf vor, ohne `data/raw/` oder bestehende Exportdateien manuell zu editieren.

## Grundsatz

- Source of truth bleibt unter `data/gold/`.
- Cleanup passiert auf Gold-Ebene, nicht direkt im Export.
- Bereinigte Staende werden in neue Dateien geschrieben.
- Jede entfernte Zeile muss per ID und Regel im Report nachvollziehbar bleiben.

## Werkzeuge

- `scripts/report_qwen_sft_quality.py`
  - erzeugt einen deterministischen Qualitaetsreport fuer Gold- oder Exportdateien
  - misst Dubletten, Stilsaettigung, Stub-Anteile, Marker-Artefakte und optionale Tokenlaengen
- `scripts/audit_qwen_source_faithfulness.py`
  - priorisiert Grenzfaelle fuer menschlichen Review anhand von lexical-overlap- und Novelty-Heuristiken
  - greift direkt auf `source_spans` in `data/normalized/` zu
- `scripts/cleanup_qwen_sft_gold.py`
  - erstellt einen bereinigten Gold-Ableger fuer Train und Eval
  - schreibt zusaetzlich einen Audit-Report mit entfernten IDs und Regeln

## Aktuelle Cleanup-Regeln

1. `stub_filter`
   - entfernt Zeilen, deren Teacher-Metadaten auf Stub- oder Fixture-Herkunft hindeuten

2. `artifact_filter`
   - entfernt Antworten mit offensichtlichen Template-Artefakten
   - aktuelle Marker:
     - `Verwenden Sie dazu **Hinweis:**`
     - `Verwenden Sie dazu **Tipp:**`
     - `Die Dokumentation empfiehlt fuer diesen Fall: Hinweis:`
     - `Die Dokumentation empfiehlt fuer diesen Fall: Tipp:`
     - `terminal_ellipsis`

3. `pair_dedup`
   - behaelt genau eine deterministische Gewinnerzeile pro normalisiertem Prompt-Antwort-Paar

4. `prompt_repeat_cap`
   - deckelt uebersaettigte Trainingsprompts pro Task
   - aktuell:
     - `clarification`: max. 3 Zeilen pro normalisiertem Prompt
     - `uncertainty_escalation`: max. 2 Zeilen pro normalisiertem Prompt
   - gilt nur fuer Train, damit Eval nicht unnoetig ausgeduennt wird

## Empfohlener Ablauf

### 1. Qualitaetsreport fuer den aktuellen Export

```bash
python scripts/report_qwen_sft_quality.py ^
  --train-input data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_full_20260326/train.jsonl ^
  --eval-input data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_full_20260326/eval.jsonl ^
  --train-metadata-input data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_full_20260326/train.metadata.jsonl ^
  --eval-metadata-input data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_full_20260326/eval.metadata.jsonl ^
  --tokenizer-name-or-path Qwen/Qwen3-8B ^
  --output tmp/qwen_quality/consolidated_gold_v1_full_20260326.report.json
```

### 2. Bereinigten Gold-Stand erzeugen

```bash
python scripts/cleanup_qwen_sft_gold.py ^
  --train-input data/gold/train/sft/JAWS/DE/consolidated_gold_v1_sft_samples.jsonl ^
  --eval-input data/gold/eval/JAWS/DE/consolidated_gold_v1_eval_cases.jsonl ^
  --train-output data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl ^
  --report-output tmp/qwen_quality/consolidated_gold_v1_lora_clean.cleanup.json
```

### 3. Quelltreue-Audit fuer Grenzfaelle

```bash
python scripts/audit_qwen_source_faithfulness.py ^
  --train-input data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl ^
  --eval-input data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl ^
  --output tmp/qwen_quality/consolidated_gold_v1_lora_clean.source_audit.json
```

### 4. Bereinigte Gold-Dateien validieren

```bash
python scripts/validate_jsonl.py --schema schemas/sft_sample.schema.json --input data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl
python scripts/validate_jsonl.py --schema schemas/eval_case.schema.json --input data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl
python scripts/check_provenance.py --input data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl
python scripts/check_provenance.py --input data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl
```

### 5. Clean-Export neu bauen

```bash
python scripts/export_qwen_sft.py ^
  --train-input data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl ^
  --eval-input data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl ^
  --output-dir data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326 ^
  --export-id jaws_de_consolidated_gold_v1_lora_clean_20260326
python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326
python scripts/smoke_test_qwen_sft.py --config training/ms-swift/qwen3_8b_jaws_de_lora_clean_dry_run.yaml
```

## Review-Fokus

- Werden echte Problemfaelle entfernt und nicht nur formal auffaellige?
- Ist die Dublettenlast sichtbar kleiner?
- Ist die Prompt-Saettigung bei Rueckfragen und Eskalationen reduziert?
- Bleiben Provenance und Split-Trennung intakt?
- Sind die neuen Gold-Dateien klar als bereinigter Ableger erkennbar?

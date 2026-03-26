# Support Data Pipeline Starter Repo

Dieses Repository ist ein Startgeruest fuer eine lokale Datenaufbereitungs- und Trainingspipeline fuer Produktsupport-Assistenten mit:

- **RAG-Korpus** aus Produkthandbuechern
- **Teacher-generierten SFT-/LoRA-Daten**
- **Qwen3-8B** als lokales Student-Modell
- **Codex CLI** als repo-zentrierte Orchestrierungsschicht

## Zielbild

1. Produkthandbuecher oder dokumentierte Importquellen kanonisch unter `data/raw/` ablegen.
2. In maschinenfreundliche Markdown-Normalform unter `data/normalized/` ueberfuehren.
3. Daraus zitierfaehige Chunks, Task-Cards und Synonym-Layer unter `data/derived/` bauen.
4. Mit einem starken Teacher-Modell qualitaetsgesicherte Supportdaten erzeugen.
5. SFT-/LoRA-Datensaetze unter `data/gold/train/` und Evals unter `data/gold/eval/` pflegen.
6. Gold-Daten nach `data/exports/qwen_sft/` exportieren.
7. Student-Modell trainieren und gegen definierte Evals pruefen.

## Schnellstart

### 1. Python-Umgebung anlegen

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Beispiel-Daten validieren

```bash
python scripts/validate_jsonl.py --schema schemas/chunk.schema.json --input data/derived/chunks/demo_chunk_set.jsonl
python scripts/validate_metadata.py --input data/normalized/demo_product/de/manual_v1/index.meta.json
python scripts/check_provenance.py --input data/derived/task_cards/demo_task_cards.jsonl
python scripts/validate_jsonl.py --schema schemas/sft_sample.schema.json --input data/gold/train/sft/demo_sft_samples.jsonl
python scripts/validate_jsonl.py --schema schemas/eval_case.schema.json --input data/gold/eval/demo_eval_cases.jsonl
```

### 3. JAWS-DE-Chunks aufbauen

```bash
python scripts/build_jaws_de_chunks.py
python scripts/validate_jaws_de_chunks.py
```

### 4. JAWS-DE Teacher-Jobs und Seed-Preview-Daten aufbauen

```bash
python scripts/build_jaws_support_data.py
python scripts/validate_support_datasets.py --sft data/derived/teacher_outputs/JAWS/DE/seed_sft_candidates.jsonl --eval data/derived/teacher_outputs/JAWS/DE/seed_eval_cases.jsonl
python scripts/validate_jsonl.py --schema schemas/teacher_job.schema.json --input data/derived/teacher_jobs/JAWS/DE/seed_generation_jobs.jsonl
```

### 5. Teacher-Runner und Gold-Promotion pruefen

```bash
python scripts/run_teacher_jobs.py --jobs data/derived/teacher_jobs/JAWS/DE/seed_generation_jobs.jsonl --output data/derived/teacher_outputs/JAWS/DE/seed_teacher_outputs.jsonl --mode stub --teacher-model teacher-stub-no-llm --teacher-run-id jaws_de_teacher_stub_run_v1
python scripts/validate_teacher_pipeline.py --jobs data/derived/teacher_jobs/JAWS/DE/seed_generation_jobs.jsonl --outputs data/derived/teacher_outputs/JAWS/DE/seed_teacher_outputs.jsonl
```

### 6. Erste groeßere Teacher-Welle fuer JAWS-DE erzeugen

```bash
python scripts/build_jaws_teacher_wave.py
python scripts/run_teacher_jobs.py --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl --output data/derived/teacher_outputs/JAWS/DE/wave1_teacher_outputs.jsonl --mode stub --teacher-model teacher-stub-no-llm --teacher-run-id jaws_de_teacher_wave_stub_run_v1
python scripts/select_teacher_wave_review_ids.py --input data/derived/teacher_outputs/JAWS/DE/wave1_teacher_outputs.jsonl --approve-output data/derived/teacher_outputs/JAWS/DE/wave1_approve_ids.txt --reject-output data/derived/teacher_outputs/JAWS/DE/wave1_reject_ids.txt --report-output data/derived/teacher_outputs/JAWS/DE/wave1_review_selection_report.json
python scripts/review_teacher_outputs.py --input data/derived/teacher_outputs/JAWS/DE/wave1_teacher_outputs.jsonl --output data/derived/teacher_outputs/JAWS/DE/wave1_reviewed_teacher_outputs.jsonl --reviewer codex-demo-wave1 --approve-file data/derived/teacher_outputs/JAWS/DE/wave1_approve_ids.txt --reject-file data/derived/teacher_outputs/JAWS/DE/wave1_reject_ids.txt
python scripts/promote_teacher_outputs.py --input data/derived/teacher_outputs/JAWS/DE/wave1_reviewed_teacher_outputs.jsonl --train-output data/gold/train/sft/JAWS/DE/promoted_teacher_wave_v1_sft_samples.jsonl --eval-output data/gold/eval/JAWS/DE/promoted_teacher_wave_v1_eval_cases.jsonl
```

### 7. Qwen-SFT-Export und Dry-Run vorbereiten

```bash
python scripts/export_qwen_sft.py --train-input data/gold/train/sft/JAWS/DE/promoted_seed_sft_samples.jsonl --eval-input data/gold/eval/JAWS/DE/promoted_seed_eval_cases.jsonl --output-dir data/exports/qwen_sft/JAWS/DE/gold_v1 --export-id jaws_de_qwen_sft_gold_v1
python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/gold_v1
python scripts/smoke_test_qwen_sft.py --config training/ms-swift/qwen3_8b_jaws_de_lora_dry_run.yaml
```

### 8. Clean-Qwen-Gate fuer den reviewten JAWS-DE-Stand

```bash
make qwen-clean-gate
```

Falls `make` lokal nicht verfuegbar ist:

```bash
python scripts/run_qwen_clean_gate.py
```

## Repo-Navigation

- `docs/` - Architektur, Policies, Review-Regeln, Repo-Spezifikation, Qwen-Export-Runbook
- `schemas/` - JSON-Schemas fuer Kernartefakte
- `prompts/` - Teacher- und Judge-Prompts
- `scripts/` - reproduzierbare ETL-/Validierungs-/Export-Skripte
- `.codex/` - Codex-Konfiguration und Subagents
- `.agents/skills/` - task-spezifische Skills fuer Codex
- `data/` - Datenzonen (`raw`, `normalized`, `derived`, `gold`, `exports`, `reports`)
- `training/` - Startpunkte fuer MS-SWIFT, Unsloth, Axolotl

## Arbeitsprinzipien

- **Source of truth** bleibt immer im Korpus und in reviewten Gold-Daten, nicht im Export.
- **Alle abgeleiteten Artefakte** benoetigen Provenance.
- **Nichts erfinden**: Fakten duerfen nur aus dokumentierter Quelle stammen.
- **Reviewbarkeit vor Automatisierung**: jeder Datensatz soll zurueckverfolgbar und diffbar sein.

## Naechste sinnvolle Schritte

1. Eigenes Produkthandbuch oder dokumentierte Importquelle unter `data/raw/<produkt>/...` ablegen.
2. `docs/metadata_schema.md`, `docs/chunking_policy.md` und die Support-Behavior-Spec anpassen.
3. Teacher-Prompts im Ordner `prompts/teacher/` verfeinern.
4. Teacher-Jobs aus `data/derived/teacher_jobs/` laufen lassen, Outputs in `data/derived/teacher_outputs/` reviewen und gezielt nach `data/gold/` uebernehmen.
5. Evals in `data/gold/eval/` aus echten Supportfaellen aufbauen.
6. Gold-Daten nach `data/exports/qwen_sft/` exportieren und den Dry-Run fuer Qwen3-8B pruefen.

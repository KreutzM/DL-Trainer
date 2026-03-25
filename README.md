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
6. Student-Modell trainieren und gegen definierte Evals pruefen.

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

### 6. Beispiel-Export fuer Training erzeugen

```bash
python scripts/export_for_training.py --input data/gold/train/sft/demo_sft_samples.jsonl --output training/exports/demo_train.jsonl
```

## Repo-Navigation

- `docs/` - Architektur, Policies, Review-Regeln, Repo-Spezifikation
- `schemas/` - JSON-Schemas fuer Kernartefakte
- `prompts/` - Teacher- und Judge-Prompts
- `scripts/` - reproduzierbare ETL-/Validierungs-/Export-Skripte
- `.codex/` - Codex-Konfiguration und Subagents
- `.agents/skills/` - task-spezifische Skills fuer Codex
- `data/` - Datenzonen (`raw`, `normalized`, `derived`, `gold`, `reports`)
- `training/` - Startpunkte fuer MS-SWIFT, Unsloth, Axolotl

## Arbeitsprinzipien

- **Source of truth** bleibt immer im Korpus, nicht im LoRA.
- **Alle abgeleiteten Artefakte** benoetigen Provenance.
- **Nichts erfinden**: Fakten duerfen nur aus dokumentierter Quelle stammen.
- **Reviewbarkeit vor Automatisierung**: jeder Datensatz soll zurueckverfolgbar und diffbar sein.

## Naechste sinnvolle Schritte

1. Eigenes Produkthandbuch oder dokumentierte Importquelle unter `data/raw/<produkt>/...` ablegen.
2. `docs/metadata_schema.md`, `docs/chunking_policy.md` und die Support-Behavior-Spec anpassen.
3. Teacher-Prompts im Ordner `prompts/teacher/` verfeinern.
4. Teacher-Jobs aus `data/derived/teacher_jobs/` laufen lassen, Outputs in `data/derived/teacher_outputs/` reviewen und gezielt nach `data/gold/` uebernehmen.
5. Evals in `data/gold/eval/` aus echten Supportfaellen aufbauen.

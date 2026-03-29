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
7. Student-Modelle trainieren und gegen definierte Evals pruefen.

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

### 4. JAWS-DE Teacher-Jobs aufbauen

```bash
python scripts/build_jaws_support_data.py
python scripts/build_jaws_teacher_wave.py
python scripts/validate_jsonl.py --schema schemas/teacher_job.schema.json --input data/derived/teacher_jobs/JAWS/DE/seed_generation_jobs.jsonl
python scripts/validate_jsonl.py --schema schemas/teacher_job.schema.json --input data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl
```

### 5. JAWS-DE MVP-Pfad kostenbewusst ausfuehren

Bevorzugter Produktivweg: der Orchestrator setzt stage-spezifisch billigere Defaults und nutzt Batch-Aufrufe statt Einzelfall-Calls.

```bash
python scripts/run_codex_cli_support_mvp_pipeline.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_mvp_v1_job_ids.txt ^
  --run-name codex_cli_support_mvp_v2 ^
  --promote
```

Standard-Defaults des effizienten Produktivpfads:
- User-Simulation: `gpt-5.4-mini`, `reasoning-effort=low`, `batch-size=8`
- Answering: `gpt-5.4`, `reasoning-effort=medium`, `batch-size=4`
- Judge/Gate: `gpt-5.4-mini`, `reasoning-effort=medium`, `batch-size=8`

Die drei Stage-Skripte bleiben direkt nutzbar und schreiben jetzt zusaetzlich `runtime`-Metriken in ihre Reports: Batch-Anzahl, Prompt-Volumen, Laufzeit pro Stage, Retry-Zahl und Quellenkontext-Groesse.

### 6. Optionale manuelle Promotion nach dem automatischen Gate

```bash
python scripts/promote_teacher_outputs.py ^
  --input data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v2_reviewed_teacher_outputs.jsonl ^
  --train-output data/gold/train/sft/JAWS/DE/codex_cli_support_mvp_v2_promoted_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/codex_cli_support_mvp_v2_promoted_eval_cases.jsonl ^
  --allow-codex-reviewed
```

## Repo-Navigation

- `docs/` - Architektur, Policies, Review-Regeln und produktive Runbooks
- `tools/jsonl_editor/` - statische Browser-UI fuer reviewbare JSONL-Dateien
- `schemas/` - JSON-Schemas fuer Kernartefakte
- `prompts/` - Teacher- und Judge-Prompts
- `scripts/` - reproduzierbare ETL-/Validierungs-/Export-Skripte
- `.codex/` - Codex-Konfiguration und Subagents
- `.agents/skills/` - task-spezifische Skills fuer Codex
- `data/` - Datenzonen (`raw`, `normalized`, `derived`, `gold`, `exports`, `reports`)
- `training/` - generische Trainingsstacks und Utilities

## Arbeitsprinzipien

- **Source of truth** bleibt immer im Korpus und in reviewten Gold-Daten, nicht im Export.
- **Alle abgeleiteten Artefakte** benoetigen Provenance.
- **Nichts erfinden**: Fakten duerfen nur aus dokumentierter Quelle stammen.
- **Reviewbarkeit vor Automatisierung**: jeder Datensatz soll zurueckverfolgbar und diffbar sein.
- **Clean cut fuer JAWS-DE**: belastbare produktive JAWS-DE-Daten beginnen im aktiven Stand wieder bei `teacher_jobs` plus echtem Codex-CLI-Teacher. Alte stub-/fake-/import-basierte Teacher-, Gold- und Exportdaten bleiben nur in der Git-Historie.

## Naechste sinnvolle Schritte

1. Eigenes Produkthandbuch oder dokumentierte Importquelle unter `data/raw/<produkt>/...` ablegen.
2. `docs/metadata_schema.md`, `docs/chunking_policy.md` und die Support-Behavior-Spec anpassen.
3. Teacher-Prompts im Ordner `prompts/teacher/` verfeinern.
4. Teacher-Jobs aus `data/derived/teacher_jobs/` bevorzugt ueber `scripts/run_codex_cli_support_mvp_pipeline.py` laufen lassen.
5. Bei Bedarf die einzelnen Stage-Skripte separat verwenden, aber mit den neuen stage-spezifischen Defaults und Batch-Aufrufen.
6. Nur `codex_reviewed` Outputs nach `data/gold/` uebernehmen.

## JSONL-Editor

Fuer den manuellen Review von Teacher-Outputs und Gold-Dateien gibt es einen lokalen Browser-Editor:

```bash
python scripts/editor_server.py --open-browser
```

Details stehen in `docs/jsonl_editor.md`.

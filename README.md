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

### 5. JAWS-DE MVP-Pfad mit User-Simulation, Answerer und Judge ausfuehren

```bash
python scripts/run_codex_cli_user_sim_batch.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_mvp_v1_job_ids.txt ^
  --output data/derived/user_simulations/JAWS/DE/codex_cli_support_mvp_v1_user_simulations.jsonl ^
  --report-output data/derived/user_simulations/JAWS/DE/codex_cli_support_mvp_v1_user_simulations_report.json ^
  --artifact-dir data/derived/teacher_runs/JAWS/DE/codex_cli_support_mvp_v1/user_simulations ^
  --simulator-run-id jaws_de_codex_cli_support_mvp_v1_user_sim ^
  --simulator-model gpt-5.4 ^
  --reasoning-effort high

python scripts/run_codex_cli_support_answer_batch.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_mvp_v1_job_ids.txt ^
  --user-simulations data/derived/user_simulations/JAWS/DE/codex_cli_support_mvp_v1_user_simulations.jsonl ^
  --raw-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_raw_responses.jsonl ^
  --teacher-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_teacher_outputs.jsonl ^
  --report-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_answer_report.json ^
  --artifact-dir data/derived/teacher_runs/JAWS/DE/codex_cli_support_mvp_v1/answers ^
  --teacher-run-id jaws_de_codex_cli_support_mvp_v1_answer ^
  --teacher-model gpt-5.4 ^
  --reasoning-effort high

python scripts/run_codex_cli_support_judge_batch.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_mvp_v1_job_ids.txt ^
  --user-simulations data/derived/user_simulations/JAWS/DE/codex_cli_support_mvp_v1_user_simulations.jsonl ^
  --raw-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_raw_responses.jsonl ^
  --teacher-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_teacher_outputs.jsonl ^
  --judge-output data/derived/teacher_reviews/JAWS/DE/codex_cli_support_mvp_v1_judge_results.jsonl ^
  --reviewed-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_reviewed_teacher_outputs.jsonl ^
  --report-output data/derived/teacher_reviews/JAWS/DE/codex_cli_support_mvp_v1_judge_report.json ^
  --artifact-dir data/derived/teacher_runs/JAWS/DE/codex_cli_support_mvp_v1/judge ^
  --reviewer-run-id jaws_de_codex_cli_support_mvp_v1_judge ^
  --reviewer-model gpt-5.4 ^
  --reasoning-effort high
```

### 6. Optionale Promotion nach dem automatischen Gate

```bash
python scripts/promote_teacher_outputs.py ^
  --input data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_reviewed_teacher_outputs.jsonl ^
  --train-output data/gold/train/sft/JAWS/DE/codex_cli_support_mvp_v1_promoted_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/codex_cli_support_mvp_v1_promoted_eval_cases.jsonl ^
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
4. Teacher-Jobs aus `data/derived/teacher_jobs/` zuerst durch `scripts/run_codex_cli_user_sim_batch.py` laufen lassen.
5. Danach mit `scripts/run_codex_cli_support_answer_batch.py` echte Support-Antworten erzeugen.
6. Anschliessend mit `scripts/run_codex_cli_support_judge_batch.py` automatisch gaten und nur belastbare reviewed Outputs nach `data/gold/` uebernehmen.

## JSONL-Editor

Fuer den manuellen Review von Teacher-Outputs und Gold-Dateien gibt es einen lokalen Browser-Editor:

```bash
python scripts/editor_server.py --open-browser
```

Details stehen in `docs/jsonl_editor.md`.

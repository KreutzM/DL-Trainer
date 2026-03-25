# GPT-5.4 Teacher Runner fuer Wave1

## Ziel

Diese Stufe verbindet die vorhandenen Wave1-Teacher-Jobs mit einem echten GPT-5.4-Lauf oder mit einem spaeteren Import derselben strukturierten Antworten.

Der Pfad bleibt bewusst getrennt:

- `data/derived/teacher_jobs/...`: stabile Wave1-Jobquelle
- `data/derived/teacher_outputs/...`: rohe Teacher-Responses und reviewbare Outputs
- `data/gold/train/...` und `data/gold/eval/...`: nur promotete Faelle

## Modi

`scripts/run_teacher_jobs.py` unterstuetzt jetzt vier Modi:

- `stub`: deterministische Fixture-Baseline ohne Modellzugriff
- `replay`: uebernimmt bereits fertige Kandidaten im bisherigen Teacher-Output-Format
- `import`: uebernimmt strukturierte rohe Teacher-Responses nach `schemas/teacher_response.schema.json`
- `openai`: ruft die OpenAI Chat Completions API mit JSON-Schema-Ausgabe auf

## GPT-5.4 Direct-Run

Voraussetzungen:

- `OPENAI_API_KEY` ist in der Umgebung gesetzt
- das verwendete Konto kann das Modell `gpt-5.4` aufrufen

Beispiel fuer eine kleine Wave1-Teilmenge:

```bash
python scripts/build_wave1_gpt54_subset.py
python scripts/run_teacher_jobs.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/wave1_gpt54_subset_job_ids.txt ^
  --mode openai ^
  --teacher-model gpt-5.4 ^
  --teacher-run-id jaws_de_wave1_gpt54_subset_run_v1 ^
  --raw-output data/derived/teacher_outputs/JAWS/DE/wave1_gpt54_subset_raw_responses.jsonl ^
  --output data/derived/teacher_outputs/JAWS/DE/wave1_gpt54_subset_teacher_outputs.jsonl
```

Der Lauf speichert zwei Artefaktstufen:

- rohe strukturierte Teacher-Responses mit Provider-Metadaten
- reviewbare Teacher-Outputs fuer den bestehenden Review-/Promotion-Workflow

## Replay- oder Import-Pfad

Wenn ein echter API-Lauf ausserhalb des Repos stattfindet, bleibt das Importformat stabil:

1. exportierte oder extern erzeugte Responses muessen `schemas/teacher_response.schema.json` erfuellen
2. `job_id`, `source_chunk_ids`, `task_type` und `target_split` muessen zum Wave1-Job passen
3. `scripts/run_teacher_jobs.py --mode import` ueberfuehrt die Responses in reviewbare Teacher-Outputs

Beispiel:

```bash
python scripts/validate_teacher_responses.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --input data/derived/teacher_outputs/JAWS/DE/wave1_gpt54_subset_raw_responses.jsonl

python scripts/run_teacher_jobs.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/wave1_gpt54_subset_job_ids.txt ^
  --mode import ^
  --import-input data/derived/teacher_outputs/JAWS/DE/wave1_gpt54_subset_raw_responses.jsonl ^
  --teacher-run-id jaws_de_wave1_gpt54_subset_run_v1 ^
  --output data/derived/teacher_outputs/JAWS/DE/wave1_gpt54_subset_teacher_outputs.jsonl
```

## Verbindliche Teacher-Output-Felder

Fuer rohe Teacher-Responses sind besonders wichtig:

- `job_id`
- `output_id`
- `teacher_provider`
- `teacher_model`
- `teacher_run_id`
- `teacher_prompt_version`
- `generation_mode`
- `parsed_response`
- `source_chunk_ids`
- `provenance`

Fuer reviewbare Teacher-Outputs bleibt die bestehende Schnittstelle erhalten, ergaenzt um:

- `teacher_provider`
- `raw_response_path`

## Review und Promotion

Der Review-Pfad bleibt unveraendert:

1. rohe Responses validieren
2. Teacher-Outputs reviewen
3. nur `human_reviewed` nach Gold promoten
4. Gold erst danach in den Qwen-Export ueberfuehren

Manuell pruefen vor einem groesseren GPT-5.4-Wellenlauf:

- ob Rueckfragen wirklich genau eine fokussierte Frage bleiben
- ob Schrittfolgen keine nicht belegten Zwischenschritte enthalten
- ob Eskalationsfaelle die Evidenzgrenze klar benennen
- ob Train/Eval weiter chunk-separiert bleiben
- ob auffaellige Formulierungen oder Redundanzen in Gold nicht uebernommen werden

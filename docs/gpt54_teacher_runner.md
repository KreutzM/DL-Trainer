# GPT-5.4 Teacher Runner

## Ziel

Der produktive Teacher-Pfad fuer JAWS-DE nutzt Codex CLI direkt.

Nach dem Clean-Cut bleiben im aktiven Repo nur noch:

- Teacher-Jobs als stabile Eingabe
- der echte Codex-CLI-Runner
- Review- und Promotion-Skripte

Es werden keine committed JAWS-DE-Teacher-, Gold- oder Export-Artefakte mehr als produktiver Stand mitgefuehrt. Neue Batches muessen bei Bedarf frisch erzeugt werden.

## Produktiver Ablauf

1. Teacher-Jobs bauen oder bestehende Jobs auswaehlen.
2. `scripts/run_codex_cli_teacher_batch.py` fuehrt die Jobs ueber Codex CLI aus.
3. Dabei entstehen echte Roh-Responses im Schema `schemas/teacher_response.schema.json`.
4. Optional materialisiert derselbe Lauf direkt reviewbare Teacher-Outputs.
5. `review_teacher_outputs.py` und `promote_teacher_outputs.py` laufen wie bisher weiter.
6. Neue Gold- und Export-Staende entstehen erst wieder aus diesen echten reviewed Outputs.

## Start des echten Pfads

Beispiel fuer einen kleinen Batch:

```bash
python scripts/run_codex_cli_teacher_batch.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/qwen_step_focus_wave_v1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_smoke_v1_job_ids.txt ^
  --raw-output data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_raw_responses.jsonl ^
  --teacher-output data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_teacher_outputs.jsonl ^
  --report-output data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_report.json ^
  --artifact-dir data/derived/teacher_runs/JAWS/DE/codex_cli_smoke_v1 ^
  --teacher-run-id jaws_de_codex_cli_smoke_v1 ^
  --teacher-model gpt-5.4 ^
  --reasoning-effort high
```

## Review und Promotion

Nach dem Lauf:

```bash
python scripts/review_teacher_outputs.py ^
  --input data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_teacher_outputs.jsonl ^
  --output data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_reviewed_teacher_outputs.jsonl ^
  --reviewer codex-cli-proof ^
  --approve-file data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_approved_ids.txt

python scripts/promote_teacher_outputs.py ^
  --input data/derived/teacher_outputs/JAWS/DE/codex_cli_smoke_v1_reviewed_teacher_outputs.jsonl ^
  --train-output data/gold/train/sft/JAWS/DE/codex_cli_smoke_v1_promoted_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/codex_cli_smoke_v1_promoted_eval_cases.jsonl
```

## I/O-Struktur des echten Codex-CLI-Pfads

Pro Batch:

- Jobquelle: `data/derived/teacher_jobs/...`
- Roh-Responses: `data/derived/teacher_outputs/..._raw_responses.jsonl`
- reviewbare Outputs: `data/derived/teacher_outputs/..._teacher_outputs.jsonl`
- Ausfuehrungsartefakte: `data/derived/teacher_runs/...`

Pro Job im Artefaktordner:

- `request.json`
- `prompt.txt`
- `response_schema.json`
- `last_message.json`
- `stdout.txt`
- `stderr.txt`

## Echte vs. Legacy-Pfade

Produktiv:

- `scripts/run_codex_cli_teacher_batch.py`
- Teacher-Metadaten mit `teacher_provider=codex_cli`
- `generation_mode=teacher_runner_codex_cli_v1`

Legacy oder Nebenweg:

- `run_teacher_jobs.py --mode stub`
- `run_teacher_jobs.py --mode replay`
- `run_teacher_jobs.py --mode import`
- `run_teacher_jobs.py --mode codex`

Diese Legacy-Pfade bleiben fuer Tests, Reproduktion oder Rueckspielung alter Artefakte erhalten, sind aber nicht mehr der primaere Weg fuer neue produktive Teacher-Wellen.

## Skalierung auf groessere Wellen

Der neue Pfad ist fuer groessere Wellen vorbereitet, weil er bereits hat:

- Jobselektion per `--job-id`, `--job-ids-file`, `--limit`
- Resume ueber `--resume`
- artefaktbasierte Nachvollziehbarkeit pro Job
- getrennte Roh- und Teacher-Outputs

Noch offen fuer sehr grosse Wellen:

- parallele Ausfuehrung mehrerer Codex-Jobs
- explizite Retry-Queues fuer Fehljobs
- ggf. Batch-Splitting ueber mehrere Worker-Maschinen

## Kennzeichnung echter Teacher-Runs

Ein echter Codex-CLI-Run ist an folgenden Feldern erkennbar:

- `teacher_provider: codex_cli`
- `teacher_model: gpt-5.4`
- eigener `teacher_run_id`
- `generation_mode: teacher_runner_codex_cli_v1`

## Aktiver JAWS-DE-Status

- `data/derived/teacher_outputs/JAWS/DE/` ist im aktiven Repo leer und wird erst durch neue echte Batches wieder befuellt.
- `data/gold/train/sft/JAWS/DE/` und `data/gold/eval/JAWS/DE/` sind im aktiven Repo leer.
- `data/exports/qwen_sft/JAWS/DE/` ist bewusst leer, bis neue echte Teacher-Wellen wieder einen belastbaren Gold-Stand erzeugt haben.

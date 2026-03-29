# JAWS-DE Teacher-, Review- und Gold-Pipeline

## Ziel

Diese Stufe trennt bewusst zwischen:

- `data/derived/teacher_jobs/`
- `data/derived/teacher_outputs/`
- `data/gold/train/`
- `data/gold/eval/`

Nach dem Clean-Cut gibt es fuer JAWS-DE im aktiven Repo nur noch einen belastbaren produktiven Standard:

- Jobs aus dem Repo
- echte Teacher-Generierung ueber Codex CLI
- menschlicher Review
- Promotion nach Gold

Alte stub-, fake-, replay-, import- oder anderweitig nicht belastbar echte JAWS-DE-Downstreamdaten wurden aus dem aktiven Stand entfernt.

## Statusfluss

Die Pipeline verwendet einen kleinen, festen Statussatz:

- `draft`
- `seed`
- `teacher_generated`
- `human_reviewed`
- `promoted`
- `rejected`

Praktisch fuer JAWS-DE:

1. `build_jaws_support_data.py` und `build_jaws_teacher_wave.py` erzeugen fruehe deterministische Jobstufen.
2. `scripts/run_codex_cli_teacher_batch.py` erzeugt echte Roh-Responses und optional reviewbare Teacher-Outputs.
3. `review_teacher_outputs.py` setzt ausgewaehlte Outputs auf `human_reviewed` oder `rejected`.
4. `promote_teacher_outputs.py` uebernimmt nur `human_reviewed`-Faelle nach `data/gold/` und markiert sie dort als `promoted`.

## Produktiver JAWS-DE-Pfad

- `data/derived/teacher_jobs/JAWS/DE/*.jsonl` bleibt die stabile Eingabeschicht.
- `data/derived/teacher_outputs/JAWS/DE/` enthaelt im aktiven Repo nur noch den echten `codex_cli_smoke_v1`-Nachweis.
- `data/gold/train/sft/JAWS/DE/` und `data/gold/eval/JAWS/DE/` enthalten nur noch die dazugehoerigen kleinen promoted Proof-Artefakte.
- `data/exports/qwen_sft/JAWS/DE/` ist bewusst leer, bis neue echte Teacher-Wellen wieder einen belastbaren Gold-Stand erzeugt haben.

## Runner-Modi

Produktiv:

- `scripts/run_codex_cli_teacher_batch.py`
- `teacher_provider=codex_cli`
- `generation_mode=teacher_runner_codex_cli_v1`

Legacy oder Test:

- `run_teacher_jobs.py --mode stub`
- `run_teacher_jobs.py --mode replay`
- `run_teacher_jobs.py --mode import`
- `run_teacher_jobs.py --mode codex`

Diese Modi duerfen fuer Architekturtests oder Rueckspielpfade weiter existieren, sind fuer neue produktive JAWS-DE-Wellen aber nicht der Standard.

## Harte Qualitaetsgrenzen

- Review und Promotion muessen Ellipsis-/Abschneideartefakte ablehnen.
- Review und Promotion muessen Markdown-Tabellen oder Listenmuell in der sichtbaren Antwort ablehnen.
- Hinweis-/Achtung-Labels duerfen nicht als Inhalt oder Tastenkombination in Gold durchrutschen.
- Stub-Fixtures in Jobs sind nie direkt freizugebende Zielantworten.

## Echte CLI-Beispielwelle

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

Danach folgt wie gewohnt:

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

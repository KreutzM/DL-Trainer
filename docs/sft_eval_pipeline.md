# JAWS-DE Teacher-, Review- und Gold-Pipeline

## Ziel

Diese Stufe trennt bewusst zwischen:

- `data/derived/teacher_jobs/`
- `data/derived/user_simulations/`
- `data/derived/teacher_outputs/`
- `data/derived/teacher_reviews/`
- `data/gold/train/`
- `data/gold/eval/`

Nach dem Clean-Cut gibt es fuer JAWS-DE im aktiven Repo nur noch einen belastbaren produktiven Standard:

- Jobs aus dem Repo
- echte User-Simulation ueber Codex CLI
- echte Teacher-Generierung ueber Codex CLI
- automatischer Judge ueber Codex CLI
- optionale Promotion nach Gold

Es werden keine committed JAWS-DE-Downstreamdaten mehr als produktiver Stand mitgefuehrt.

## Statusfluss

Die Pipeline verwendet einen kleinen, festen Statussatz:

- `draft`
- `seed`
- `teacher_generated`
- `codex_reviewed`
- `human_reviewed`
- `promoted`
- `rejected`

Praktisch fuer JAWS-DE:

1. `build_jaws_support_data.py` und `build_jaws_teacher_wave.py` erzeugen fruehe deterministische Jobstufen.
2. `scripts/run_codex_cli_user_sim_batch.py` erzeugt realistische User-Anfragen.
3. Bevorzugt `scripts/run_codex_cli_support_mvp_pipeline.py` starten; der Wrapper setzt die produktiven kostensparenden Stage-Defaults.
4. `scripts/run_codex_cli_support_answer_batch.py` erzeugt echte Roh-Responses und reviewbare Teacher-Outputs.
5. `scripts/run_codex_cli_support_judge_batch.py` setzt Outputs automatisiert auf `codex_reviewed` oder `rejected`.
5. `review_teacher_outputs.py` bleibt fuer spaetere manuelle Nachpruefung verfuegbar.
6. `promote_teacher_outputs.py` kann `human_reviewed` oder optional `codex_reviewed`-Faelle nach `data/gold/` uebernehmen und dort als `promoted` markieren.

## Produktiver JAWS-DE-Pfad

- `data/derived/teacher_jobs/JAWS/DE/*.jsonl` bleibt die stabile Eingabeschicht.
- `data/derived/user_simulations/JAWS/DE/` enthaelt reale, von Codex erzeugte Nutzeranfragen.
- `data/derived/teacher_outputs/JAWS/DE/` ist im aktiven Repo leer und wird erst durch neue echte Batches wieder befuellt.
- `data/derived/teacher_reviews/JAWS/DE/` enthaelt Judge-Ergebnisse und Gate-Reports.
- `data/gold/train/sft/JAWS/DE/` und `data/gold/eval/JAWS/DE/` sind im aktiven Repo leer.
- `data/exports/qwen_sft/JAWS/DE/` ist bewusst leer, bis neue echte Teacher-Wellen wieder einen belastbaren Gold-Stand erzeugt haben.

## Runner-Modi

Produktiv:

- `scripts/run_codex_cli_user_sim_batch.py`
- `scripts/run_codex_cli_support_answer_batch.py`
- `scripts/run_codex_cli_support_judge_batch.py`
- `simulator_provider=codex_cli`, `teacher_provider=codex_cli`, `reviewer_provider=codex_cli`
- `generation_mode=teacher_user_simulator_codex_cli_v1`, `teacher_answer_codex_cli_v1`, `teacher_judge_codex_cli_v1`

Legacy oder Test:

- `scripts/run_codex_cli_teacher_batch.py`
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

## Echte CLI-MVP-Welle

```bash
python scripts/run_codex_cli_support_mvp_pipeline.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_mvp_v1_job_ids.txt ^
  --run-name codex_cli_support_mvp_v2 ^
  --promote
```

Produktive Default-Profile:

- User-Simulation: `gpt-5.4-mini`, `low`, `batch-size=8`
- Answering: `gpt-5.4`, `medium`, `batch-size=4`
- Judge/Gate: `gpt-5.4-mini`, `medium`, `batch-size=8`

Die Stage-Reports enthalten jetzt einen `runtime`-Block mit Batch-, Prompt-, Laufzeit- und Retry-Metriken.

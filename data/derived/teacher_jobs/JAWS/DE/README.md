# JAWS-DE Teacher Jobs

Diese Ablage ist die stabile Eingabeschicht fuer neue JAWS-DE-Teacher-Laeufe.

Aktiv relevant:

- `wave1_generation_jobs.jsonl`
- `current_generation_job_ids.txt`
- `current_generation_selection.json`

Weitere vorhandene Jobquellen:

- `seed_generation_jobs.jsonl`
- `wave2_scaleup_generation_jobs.jsonl`
- `wave2_topoff_generation_jobs.jsonl`

Historische oder schmale Hilfslisten:

- `codex_cli_support_mvp_v1_job_ids.txt`
- `codex_cli_smoke_v1_job_ids.txt`

Regel:

- Neue produktive Wellen starten von diesen Jobquellen.
- Der empfohlene Runner ist `scripts/run_codex_cli_support_mvp_pipeline.py`.
- Fuer den Fresh-Run-Default die aktuelle Selektion ueber `current_generation_selection.json` laden.
- Aeltere Job-IDs bleiben nur als Herkunft der aktuellen Selektion erhalten, nicht als aktueller Default.
- Details und aktuelle Baseline stehen in `docs/jaws_de_workflow.md` und `docs/jaws_de_current_baseline.json`.

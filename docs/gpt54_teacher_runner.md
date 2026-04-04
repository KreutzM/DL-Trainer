# GPT-5.4 Teacher Runner

Die kanonische Beschreibung des produktiven JAWS-DE-Workflows steht in `docs/jaws_de_workflow.md`.
Die maschinenlesbare Current-Baseline dazu steht in `docs/jaws_de_current_baseline.json`.

## Zweck dieser Datei

Diese Datei beschreibt nur noch die Runner-Einordnung:

- produktiver Orchestrator: `scripts/run_codex_cli_support_mvp_pipeline.py`
- produktive Stages:
  - `scripts/run_codex_cli_user_sim_batch.py`
  - `scripts/run_codex_cli_support_answer_batch.py`
  - `scripts/run_codex_cli_support_judge_batch.py`
- Promotion: `scripts/promote_teacher_outputs.py`

## Aktueller Produktivstandard

- neuer produktiver JAWS-DE-Run immer mit neuem `run_name`
- committed Referenz-Baseline: `openrouter_gpt54_controlled_gold_v16`
- historische Prefixe: `codex_cli_support_mvp_v1`, `codex_cli_support_mvp_v2_probe`, `codex_cli_smoke_v1`

## Legacy-Einordnung

`scripts/run_codex_cli_teacher_batch.py` bleibt fuer Tests oder Reproduktion historischer Nebenpfade erhalten, ist aber nicht der empfohlene JAWS-DE-Produktivweg.

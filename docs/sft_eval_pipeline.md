# JAWS-DE SFT- und Eval-Pipeline

Die kanonische Workflow-Beschreibung steht in `docs/jaws_de_workflow.md`.
Die maschinenlesbare Current-Baseline dazu steht in `docs/jaws_de_current_baseline.json`.

## Statusfluss

1. `teacher_jobs`
2. `user_simulations`
3. `teacher_outputs`
4. `teacher_reviews`
5. `gold/train` und `gold/eval`
6. `exports/qwen_sft`
7. `training/transformers`

## Aktueller Stand

- produktive committed Baseline: `codex_cli_support_validation_v2`
- historisch, aber nicht aktuell: `codex_cli_support_mvp_v1`, `codex_cli_support_mvp_v2_probe`
- aktueller Trainings-Export: `data/exports/qwen_sft/JAWS/DE/current/`
- aktueller Trainingsfreeze: `training/transformers/jaws_de_current.yaml`

## Guardrail

Neue produktive Laeufe duplizieren keinen alten Baseline-Namen. Der Pipeline-Wrapper blockiert vorhandene Run-Namen ohne `--resume`.

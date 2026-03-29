# JAWS-DE Teacher Outputs

Diese Ablage ist nach dem Clean-Cut bewusst leer zwischen echten Teacher-Laeufen.

Hier sollen nur noch belastbare JAWS-DE-Artefakte ab dem echten Codex-CLI-Teacher-Schritt entstehen, zum Beispiel:

- `<batch>_raw_responses.jsonl`
- `<batch>_teacher_outputs.jsonl`
- `<batch>_reviewed_teacher_outputs.jsonl`
- `<batch>_report.json`
- optionale Review-Freigabelisten wie `<batch>_approved_ids.txt`

Bewusst entfernt:

- alle stub-, fake-, replay-, import- oder anderweitig nicht belastbar echten JAWS-DE-Teacher-Outputs
- auch der kleine fruehere Proof-Batch, damit der produktive JAWS-DE-Pfad im aktiven Repo wirklich bei Jobs plus echtem Runner neu beginnt

Wichtig:

- Nur `teacher_provider=codex_cli` plus `generation_mode=teacher_runner_codex_cli_v1` gilt hier als produktiver JAWS-DE-Standard.
- Reviewte Teacher-Outputs koennen wie bisher nach `data/gold/` promoted werden.
- Alte JAWS-DE-Teacher-Artefakte bleiben nur in der Git-Historie erhalten.

# JAWS-DE Teacher Outputs

Diese Ablage ist nach dem Clean-Cut bewusst leer zwischen echten Teacher-Laeufen.

Hier sollen nur noch belastbare JAWS-DE-Artefakte ab dem echten Codex-CLI-Teacher-Schritt entstehen, zum Beispiel:

- `<batch>_user_simulations.jsonl` unter `data/derived/user_simulations/JAWS/DE/`
- `<batch>_raw_responses.jsonl`
- `<batch>_teacher_outputs.jsonl`
- `<batch>_judge_results.jsonl` unter `data/derived/teacher_reviews/JAWS/DE/`
- `<batch>_reviewed_teacher_outputs.jsonl`
- `<batch>_report.json`
- optionale Review-Freigabelisten wie `<batch>_approved_ids.txt`

Bewusst entfernt:

- alle stub-, fake-, replay-, import- oder anderweitig nicht belastbar echten JAWS-DE-Teacher-Outputs
- auch der kleine fruehere Proof-Batch, damit der produktive JAWS-DE-Pfad im aktiven Repo wirklich bei Jobs plus echtem Runner neu beginnt

Wichtig:

- Der produktive MVP-Pfad fuer JAWS-DE ist dreistufig: User-Simulation -> Support-Answer -> Judge.
- Nur `simulator_provider=codex_cli`, `teacher_provider=codex_cli`, `reviewer_provider=codex_cli` gelten hier als produktiver JAWS-DE-Standard.
- Automatisch gegatete Outputs tragen `review_status=codex_reviewed` oder `rejected`.
- Reviewte Teacher-Outputs koennen wie bisher nach `data/gold/` promoted werden; fuer automatische Gates ueber `--allow-codex-reviewed`.
- Alte JAWS-DE-Teacher-Artefakte bleiben nur in der Git-Historie erhalten.

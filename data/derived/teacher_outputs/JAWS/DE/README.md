# JAWS-DE Teacher Outputs

Diese Ablage enthaelt nur noch belastbare JAWS-DE-Artefakte ab dem echten Codex-CLI-Teacher-Schritt.

Bewusst erhalten:

- `codex_cli_smoke_v1_raw_responses.jsonl`: echter kleiner Proof-Batch, direkt via Codex CLI mit `gpt-5.4` erzeugt
- `codex_cli_smoke_v1_teacher_outputs.jsonl`: daraus materialisierte reviewbare Teacher-Outputs
- `codex_cli_smoke_v1_reviewed_teacher_outputs.jsonl`: derselbe Proof-Batch nach Review
- `codex_cli_smoke_v1_report.json`: Batchbericht fuer den echten Codex-CLI-Lauf
- `codex_cli_smoke_v1_approved_ids.txt`: explizite Review-Freigaben fuer den Proof-Batch

Bewusst entfernt:

- alle stub-, fake-, replay-, import- oder anderweitig nicht belastbar echten JAWS-DE-Teacher-Outputs
- alle daraus abgeleiteten Review-Pakete, Cleanup-Hilfen und Qwen-Reparaturartefakte

Wichtig:

- Nur `teacher_provider=codex_cli` plus `generation_mode=teacher_runner_codex_cli_v1` gilt hier als produktiver JAWS-DE-Standard.
- Reviewte Teacher-Outputs koennen wie bisher nach `data/gold/` promoted werden.
- Alte JAWS-DE-Teacher-Artefakte bleiben nur in der Git-Historie erhalten.

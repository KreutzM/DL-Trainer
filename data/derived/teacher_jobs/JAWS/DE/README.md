# JAWS-DE Teacher Jobs

Diese Ablage enthaelt die stabile Eingabeschicht fuer Teacher-Laeufe.

Produktiv gedacht fuer den echten Codex-CLI-Pfad:

- `wave1_generation_jobs.jsonl`
- `qwen_focus_wave_v1_generation_jobs.jsonl`
- `qwen_step_focus_wave_v1_generation_jobs.jsonl`
- `qwen_troubleshooting_relabel_wave1_generation_jobs.jsonl`

Hilfs- und Selektionsartefakte:

- `seed_generation_jobs.jsonl`: kleine deterministische Seed-Jobs fuer Architekturtests
- `wave1_generation_report.json`: Verteilung der Wave nach Split, Falltyp und Quelldokument
- `wave1_gpt54_subset_job_ids.txt`: kleine historische Teilmenge fuer fruehe GPT-5.4-Experimente
- `wave1_codex_gpt54_real_job_ids.txt`: historische Job-Teilmenge fuer eine fruehe Codex-Welle
- `qwen_focus_wave_v1_generation_report.json`: Bericht zur fokussierten Qwen-Welle
- `qwen_focus_wave_v1_job_ids.txt`: Job-IDs fuer eine fokussierte FAQ-Welle
- `qwen_step_by_step_gap_report.json`: Audit fuer verbleibende `step_by_step`-Luecken
- `qwen_step_by_step_candidate_chunk_ids.txt`: dazugehoerige Chunk-IDs
- `qwen_step_focus_wave_v1_generation_report.json`: Bericht zur task-spezifischen Schrittwelle
- `qwen_step_focus_wave_v1_job_ids.txt`: Job-IDs fuer eine echte Schrittwelle
- `qwen_troubleshooting_relabel_wave1_generation_report.json`: Bericht zur FAQ-Reparaturwelle
- `qwen_troubleshooting_relabel_wave1_job_ids.txt`: Job-IDs fuer die Reparaturwelle
- `codex_cli_smoke_v1_job_ids.txt`: kleine echte Proof-Menge fuer den neuen Codex-CLI-Pfad

Wichtig:

- Diese Jobs sind die Source-of-truth fuer neue Teacher-Laeufe.
- Ein produktiver Teacher-Lauf soll diese Dateien direkt konsumieren.
- Die eigentliche Generierung erfolgt jetzt ueber `scripts/run_codex_cli_teacher_batch.py`.
- Stub-, Replay- oder Import-Pfade duerfen dieselben Jobs weiter fuer Tests nutzen, sind aber nicht mehr der produktive Primärweg.

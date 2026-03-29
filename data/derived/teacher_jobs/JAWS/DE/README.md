# JAWS-DE Teacher Jobs

Diese Ablage enthaelt die stabile Eingabeschicht fuer neue Teacher-Laeufe.

Aktiv behalten:

- `seed_generation_jobs.jsonl`: kleine deterministische Seed-Jobs fuer Architekturtests
- `wave1_generation_jobs.jsonl`: groessere allgemeine JAWS-DE-Welle
- `wave2_scaleup_generation_jobs.jsonl`: weitere groessere Welle aus der Chunk-Auswahl
- `wave2_topoff_generation_jobs.jsonl`: Topoff-Welle fuer Zusatzabdeckung
- `qwen_focus_wave_v1_generation_jobs.jsonl`: fokussierte FAQ-Welle
- `qwen_step_focus_wave_v1_generation_jobs.jsonl`: fokussierte Schrittwelle
- `qwen_troubleshooting_relabel_wave1_generation_jobs.jsonl`: fruehere Relabel-Reparaturwelle als Jobquelle
- `codex_cli_smoke_v1_job_ids.txt`: kleine echte Proof-Menge fuer den produktiven Codex-CLI-Pfad

Wichtig:

- Diese Jobs sind die Source-of-truth fuer neue Teacher-Laeufe.
- Ein produktiver Teacher-Lauf soll diese Dateien direkt konsumieren.
- Die eigentliche Generierung erfolgt ueber `scripts/run_codex_cli_teacher_batch.py`.
- Downstream-JAWS-DE-Daten ab `teacher_outputs/`, `data/gold/` und `data/exports/` wurden im aktiven Repo bewusst auf einen sauberen Neustartpunkt zurueckgesetzt.
- Alte Reports, Review-Pakete und Hilfslisten aus schwachen Downstream-Staenden wurden aus dem aktiven Repo entfernt.

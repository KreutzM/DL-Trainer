# JAWS-DE Teacher Jobs

Diese Ablage enthaelt Runner-Eingaben fuer den Teacher-Schritt.

- `seed_generation_jobs.jsonl`: kleine deterministische Seed-Jobs fuer Architekturtests
- `wave1_generation_jobs.jsonl`: erste groessere chunkbasierte Teacher-Welle
- `wave1_generation_report.json`: Verteilung der Wave nach Split, Falltyp und Quelldokument
- `wave1_gpt54_subset_job_ids.txt`: kleine deterministische Wave1-Teilmenge fuer echten GPT-5.4- oder Import-Lauf
- `wave1_gpt54_subset_report.json`: Bericht zur Wave1-Teilmenge nach Split, Falltyp und Quelldokument
- `wave1_codex_gpt54_real_job_ids.txt`: groessere deterministische Job-Menge fuer die reale Codex/GPT-5.4-Welle
- `wave1_codex_gpt54_real_batch_report.json`: Bericht zur groesseren realen Codex-Welle nach Split, Falltyp und Quelldokument
- `qwen_focus_wave_v1_generation_jobs.jsonl`: gezielte Qwen-Ausbauwelle fuer atomare FAQ-Faelle plus den letzten verbleibenden `step_by_step`-Kandidaten
- `qwen_focus_wave_v1_generation_report.json`: Bericht zur fokussierten Qwen-Welle inklusive Task-Shortages nach Gold- und Ausbau-Exclusions
- `qwen_focus_wave_v1_job_ids.txt`: extrahierte Job-IDs fuer einen spaeteren echten Teacher-Lauf auf der fokussierten Qwen-Welle
- `qwen_step_by_step_gap_report.json`: Audit, wie viele echte `step_by_step`-Kandidaten nach aktuellen Exclusions im bestehenden Chunk-Pool noch verbleiben
- `qwen_step_by_step_candidate_chunk_ids.txt`: die dazugehoerigen verbleibenden Chunk-IDs fuer gezielte Nacharbeit oder neue Quellwellen

Die Jobs sind bewusst getrennt von `data/derived/teacher_outputs/`, damit ein spaeterer echter Teacher-Lauf dieselben Job-Dateien konsumieren und neue Outputs zurueckschreiben kann.

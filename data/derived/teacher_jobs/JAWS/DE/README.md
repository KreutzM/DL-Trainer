# JAWS-DE Teacher Jobs

Diese Ablage enthaelt Runner-Eingaben fuer den Teacher-Schritt.

- `seed_generation_jobs.jsonl`: kleine deterministische Seed-Jobs fuer Architekturtests
- `wave1_generation_jobs.jsonl`: erste groessere chunkbasierte Teacher-Welle
- `wave1_generation_report.json`: Verteilung der Wave nach Split, Falltyp und Quelldokument
- `wave1_gpt54_subset_job_ids.txt`: kleine deterministische Wave1-Teilmenge fuer echten GPT-5.4- oder Import-Lauf
- `wave1_gpt54_subset_report.json`: Bericht zur Wave1-Teilmenge nach Split, Falltyp und Quelldokument

Die Jobs sind bewusst getrennt von `data/derived/teacher_outputs/`, damit ein spaeterer echter Teacher-Lauf dieselben Job-Dateien konsumieren und neue Outputs zurueckschreiben kann.

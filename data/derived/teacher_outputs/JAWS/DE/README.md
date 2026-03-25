# JAWS-DE Teacher Outputs

Diese Ablage enthaelt reviewbare Kandidaten nach dem Teacher-Schritt.

- `seed_sft_candidates.jsonl`: kleine Seed-Preview-Faelle direkt aus der Rezeptlogik, Status `seed`
- `seed_eval_cases.jsonl`: kleine Seed-Eval-Preview-Faelle, Status `seed`
- `seed_teacher_outputs.jsonl`: kleine Runner-Ausgabe im Teacher-Output-Format
- `reviewed_teacher_outputs.jsonl`: dieselben Seed-Outputs nach Review
- `wave1_teacher_outputs.jsonl`: erste groeßere JAWS-DE-Teacher-Welle, Status `teacher_generated`
- `wave1_reviewed_teacher_outputs.jsonl`: dieselbe Welle nach Review mit Status `human_reviewed` oder `rejected`
- `wave1_review_selection_report.json`: Verteilung der fuer Review ausgewaehlten Wave-Menge

Wichtig:

- Nur reviewte Teacher-Outputs sind fuer Promotion nach `data/gold/` gedacht.
- Gold-Artefakte verweisen ueber `promoted_from` zurueck auf genau einen Teacher-Output.
- `wave1_approve_ids.txt` und `wave1_reject_ids.txt` sind die deterministische Review-Auswahl fuer die erste groeßere Welle.

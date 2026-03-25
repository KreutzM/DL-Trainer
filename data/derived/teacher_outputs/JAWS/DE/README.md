# JAWS-DE Teacher Outputs

Diese Ablage enthält reviewbare Kandidaten nach dem Teacher-Schritt.

- `seed_sft_candidates.jsonl`: kleine Seed-Preview-Fälle direkt aus der Rezeptlogik, Status `seed`
- `seed_eval_cases.jsonl`: kleine Seed-Eval-Preview-Fälle, Status `seed`
- `seed_teacher_outputs.jsonl`: Runner-Ausgabe im Teacher-Output-Format, Status `teacher_generated`
- `reviewed_teacher_outputs.jsonl`: dieselben Outputs nach Review mit Status `human_reviewed` oder `rejected`

Wichtig:

- Nur `reviewed_teacher_outputs.jsonl` ist für Promotion nach `data/gold/` gedacht.
- Gold-Artefakte verweisen über `promoted_from` zurück auf genau einen Teacher-Output.

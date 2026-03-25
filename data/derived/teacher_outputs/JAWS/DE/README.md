# JAWS-DE Teacher Outputs

Diese Ablage enthaelt reviewbare Kandidaten nach dem Teacher-Schritt.

- `seed_sft_candidates.jsonl`: kleine Seed-Preview-Faelle direkt aus der Rezeptlogik, Status `seed`
- `seed_eval_cases.jsonl`: kleine Seed-Eval-Preview-Faelle, Status `seed`
- `seed_teacher_outputs.jsonl`: kleine Runner-Ausgabe im Teacher-Output-Format
- `reviewed_teacher_outputs.jsonl`: dieselben Seed-Outputs nach Review
- `wave1_teacher_outputs.jsonl`: erste groessere JAWS-DE-Teacher-Welle, Status `teacher_generated`
- `wave1_reviewed_teacher_outputs.jsonl`: dieselbe Welle nach Review mit Status `human_reviewed` oder `rejected`
- `wave1_review_selection_report.json`: Verteilung der fuer Review ausgewaehlten Wave-Menge
- `wave1_codex_gpt54_raw_responses.jsonl`: echte, von Codex selbst formulierte GPT-5.4-Roh-Responses fuer eine kleine Wave1-Teilmenge
- `wave1_codex_gpt54_teacher_outputs.jsonl`: daraus materialisierte reviewbare Teacher-Outputs
- `wave1_codex_gpt54_reviewed_outputs.jsonl`: dieselbe Teilmenge nach Review
- `wave1_codex_gpt54_real_raw_responses.jsonl`: groessere reale Codex/GPT-5.4-Roh-Response-Welle auf Basis der deterministischen Wave1-Reviewmenge
- `wave1_codex_gpt54_real_teacher_outputs.jsonl`: daraus materialisierte reviewbare Teacher-Outputs
- `wave1_codex_gpt54_real_reviewed_outputs.jsonl`: dieselbe groessere Codex-Welle nach Review
- `wave1_codex_gpt54_real_review_report.json`: Review-Verteilung fuer die groessere reale Codex-Welle
- `wave1_gpt54_subset_raw_responses.jsonl`: rohe strukturierte GPT-5.4-Responses fuer eine kleine Wave1-Teilmenge
- `wave1_gpt54_subset_teacher_outputs.jsonl`: daraus abgeleitete reviewbare Teacher-Outputs
- `wave1_gpt54_subset_reviewed_outputs.jsonl`: dieselbe Teilmenge nach Review

Wichtig:

- Nur reviewte Teacher-Outputs sind fuer Promotion nach `data/gold/` gedacht.
- Gold-Artefakte verweisen ueber `promoted_from` zurueck auf genau einen Teacher-Output.
- `wave1_approve_ids.txt` und `wave1_reject_ids.txt` sind die deterministische Review-Auswahl fuer die erste groessere Stub-Welle.
- `wave1_codex_gpt54_real_approve_ids.txt` ist die deterministische Review-Freigabeliste fuer die groessere reale Codex-Welle.
- `wave1_codex_gpt54_real_reject_ids.txt` haelt die bewusst ausgeschlossenen Qualitaetsfaelle derselben Welle fest.
- Rohe GPT-5.4-Responses bleiben getrennt von reviewbaren Teacher-Outputs, damit echte Codex-Runs, Stub-Laeufe und externe Fallbacks denselben Review-Pfad nutzen koennen.

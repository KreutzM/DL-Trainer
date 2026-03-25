# JAWS-DE Teacher-, Review- und Gold-Pipeline

## Ziel

Diese Stufe trennt bewusst zwischen:

- `data/derived/teacher_jobs/`
- `data/derived/teacher_outputs/`
- `data/gold/train/`
- `data/gold/eval/`

Damit bleibt nachvollziehbar, welche Datensaetze nur Seed- oder Teacher-Kandidaten sind und welche Faelle nach menschlichem Review in Gold-Artefakte uebernommen wurden.

## Statusfluss

Die Pipeline verwendet einen kleinen, festen Statussatz:

- `draft`
- `seed`
- `teacher_generated`
- `human_reviewed`
- `promoted`
- `rejected`

Praktisch fuer JAWS-DE:

1. `build_jaws_support_data.py` erzeugt die kleine Seed-Stufe fuer Architekturtests.
2. `build_jaws_teacher_wave.py` erzeugt die erste groeßere, chunkbasierte Welle mit Status `seed`.
3. `run_teacher_jobs.py` erzeugt reviewbare Teacher-Outputs mit Status `teacher_generated`.
4. `select_teacher_wave_review_ids.py` berechnet eine deterministische, kleinere Review-Menge mit guter Abdeckung ueber Falltypen und Dokumente.
5. `review_teacher_outputs.py` setzt die ausgewaehlten Outputs auf `human_reviewed` oder `rejected`.
6. `promote_teacher_outputs.py` uebernimmt nur `human_reviewed`-Faelle nach `data/gold/` und markiert sie dort als `promoted`.

## Wellen-Idee

Die groeßere Teacher-Welle baut nicht mehr auf einzelnen hartcodierten Beispielen auf, sondern auf Chunk-Eigenschaften:

- `faq_direct_answer` bevorzugt kompakte Konzept- und Referenz-Chunks
- `troubleshooting` bevorzugt Warnungen, Bedingungen und handlungsorientierte Abschnitte
- `step_by_step` bevorzugt Prozeduren und klare Schrittfolgen
- `clarification` bevorzugt breite Themen mit Listen, Optionen oder mehreren Bedienpfaden
- `uncertainty_escalation` bevorzugt Einschraenkungen, Hinweise und nicht pauschal zugesicherte Faelle

Die Auswahl bleibt deterministisch, chunk-basiert und dokumentiert. Train und Eval werden bereits auf Chunk-Ebene getrennt, damit spaetere Promotion keine Split-Kollisionen erzeugt.

## Artefakte

### Teacher-Jobs

- `data/derived/teacher_jobs/JAWS/DE/seed_generation_jobs.jsonl`
- `data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl`
- `data/derived/teacher_jobs/JAWS/DE/wave1_generation_report.json`

Die Wave-Datei ist die erste groeßere JAWS-DE-Welle. Sie enthaelt Runner-Input, Promptpfade, Chunk-Referenzen, Auswahlgruende und ein deterministisches Fixture-Payload. Diese Datei bleibt die stabile Schnittstelle fuer spaetere echte Teacher-Laeufe.

### Teacher-Outputs

- `data/derived/teacher_outputs/JAWS/DE/seed_teacher_outputs.jsonl`
- `data/derived/teacher_outputs/JAWS/DE/wave1_teacher_outputs.jsonl`
- `data/derived/teacher_outputs/JAWS/DE/wave1_reviewed_teacher_outputs.jsonl`
- `data/derived/teacher_outputs/JAWS/DE/wave1_review_selection_report.json`

Teacher-Outputs kapseln genau einen reviewbaren Kandidaten plus Run-Metadaten wie `teacher_model`, `teacher_run_id`, `job_id`, `task_type`, `quality_score` und `review_status`.

### Gold-Artefakte

- `data/gold/train/sft/JAWS/DE/promoted_seed_sft_samples.jsonl`
- `data/gold/eval/JAWS/DE/promoted_seed_eval_cases.jsonl`
- `data/gold/train/sft/JAWS/DE/promoted_teacher_wave_v1_sft_samples.jsonl`
- `data/gold/eval/JAWS/DE/promoted_teacher_wave_v1_eval_cases.jsonl`

Gold-Dateien enthalten nur promotete Faelle. Jeder Gold-Datensatz verweist ueber `promoted_from` auf genau einen Teacher-Output.

## Runner-Modi

### Stub

`run_teacher_jobs.py --mode stub` nutzt das Fixture-Payload aus dem Job und erzeugt deterministische Teacher-Outputs ohne externen Modellzugriff. Fuer die erste groeßere Welle ist das die reproduzierbare Repo-Baseline.

### Replay

`run_teacher_jobs.py --mode replay --replay-input <jsonl>` uebernimmt vorbereitete Kandidaten im Teacher-Output-Format. Damit laesst sich spaeter ein externer Teacher-Lauf in dieselbe Struktur zurueckspielen, ohne das Repo umzubauen.

## Menschlicher Review bleibt noetig fuer

- fachliche Freigabe vor Promotion nach `data/gold/`
- Grenzfaelle mit moeglicher Versionsabhaengigkeit
- Faelle, in denen eine Rueckfrage oder Eskalation sprachlich noch geschaerft werden sollte
- Entscheidung, welche Teacher-Kandidaten wirklich in den ersten LoRA-Export gehoeren

## Erste sinnvolle Zielgroesse

Die erste Wave muss noch nicht das spaetere Endvolumen erreichen. Sinnvoll ist eine kontrollierte Zwischenstufe mit:

- einigen hundert Teacher-Kandidaten
- einer deutlich kleineren, aber gemischten Gold-Train-Menge
- einer kleineren, sauberen Gold-Eval-Menge

Diese Repo-Stufe ist deshalb auf eine groessere reviewbare Welle plus eine kuratierte Gold-Teilmenge ausgelegt, nicht auf eine unkontrollierte Vollabdeckung des gesamten JAWS-Wissens.

## Rebuild der ersten Wave

```bash
python scripts/build_jaws_teacher_wave.py
python scripts/run_teacher_jobs.py --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl --output data/derived/teacher_outputs/JAWS/DE/wave1_teacher_outputs.jsonl --mode stub --teacher-model teacher-stub-no-llm --teacher-run-id jaws_de_teacher_wave_stub_run_v1
python scripts/select_teacher_wave_review_ids.py --input data/derived/teacher_outputs/JAWS/DE/wave1_teacher_outputs.jsonl --approve-output data/derived/teacher_outputs/JAWS/DE/wave1_approve_ids.txt --reject-output data/derived/teacher_outputs/JAWS/DE/wave1_reject_ids.txt --report-output data/derived/teacher_outputs/JAWS/DE/wave1_review_selection_report.json
python scripts/review_teacher_outputs.py --input data/derived/teacher_outputs/JAWS/DE/wave1_teacher_outputs.jsonl --output data/derived/teacher_outputs/JAWS/DE/wave1_reviewed_teacher_outputs.jsonl --reviewer codex-demo-wave1 --approve-file data/derived/teacher_outputs/JAWS/DE/wave1_approve_ids.txt --reject-file data/derived/teacher_outputs/JAWS/DE/wave1_reject_ids.txt
python scripts/promote_teacher_outputs.py --input data/derived/teacher_outputs/JAWS/DE/wave1_reviewed_teacher_outputs.jsonl --train-output data/gold/train/sft/JAWS/DE/promoted_teacher_wave_v1_sft_samples.jsonl --eval-output data/gold/eval/JAWS/DE/promoted_teacher_wave_v1_eval_cases.jsonl
python scripts/validate_teacher_pipeline.py --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl --outputs data/derived/teacher_outputs/JAWS/DE/wave1_reviewed_teacher_outputs.jsonl --gold-sft data/gold/train/sft/JAWS/DE/promoted_teacher_wave_v1_sft_samples.jsonl --gold-eval data/gold/eval/JAWS/DE/promoted_teacher_wave_v1_eval_cases.jsonl --require-all-task-types
```

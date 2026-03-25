# JAWS-DE Teacher-, Review- und Gold-Pipeline

## Ziel

Diese Stufe trennt bewusst zwischen:

- `data/derived/teacher_jobs/`
- `data/derived/teacher_outputs/`
- `data/gold/train/`
- `data/gold/eval/`

Damit bleibt nachvollziehbar, welche Datensätze nur Seed- oder Teacher-Kandidaten sind und welche Fälle nach menschlichem Review in Gold-Artefakte übernommen wurden.

## Statusfluss

Die Pipeline verwendet einen kleinen, festen Statussatz:

- `draft`
- `seed`
- `teacher_generated`
- `human_reviewed`
- `promoted`
- `rejected`

Praktisch für JAWS-DE:

1. `build_jaws_support_data.py` erzeugt Seed-Jobs und Seed-Preview-Fälle mit Status `seed`.
2. `run_teacher_jobs.py` erzeugt reviewbare Teacher-Outputs mit Status `teacher_generated`.
3. `review_teacher_outputs.py` setzt ausgewählte Outputs auf `human_reviewed` oder `rejected`.
4. `promote_teacher_outputs.py` übernimmt nur `human_reviewed`-Fälle nach `data/gold/` und markiert sie dort als `promoted`.

## Artefakte

### Teacher-Jobs

- `data/derived/teacher_jobs/JAWS/DE/seed_generation_jobs.jsonl`

Enthält den Runner-Input, Promptpfade, Chunk-Referenzen und ein deterministisches Fixture-Payload. Diese Datei ist die stabile Schnittstelle für spätere echte Teacher-Läufe.

### Teacher-Outputs

- `data/derived/teacher_outputs/JAWS/DE/seed_teacher_outputs.jsonl`
- `data/derived/teacher_outputs/JAWS/DE/reviewed_teacher_outputs.jsonl`

Teacher-Outputs kapseln genau einen reviewbaren Kandidaten plus Run-Metadaten wie `teacher_model`, `teacher_run_id`, `job_id` und `review_status`.

### Gold-Artefakte

- `data/gold/train/sft/JAWS/DE/promoted_seed_sft_samples.jsonl`
- `data/gold/eval/JAWS/DE/promoted_seed_eval_cases.jsonl`

Gold-Dateien enthalten nur promotete Fälle. Jeder Gold-Datensatz verweist über `promoted_from` auf den konkreten Teacher-Output.

## Runner-Modi

### Stub

`run_teacher_jobs.py --mode stub` nutzt das Fixture-Payload aus dem Job und erzeugt deterministische Teacher-Outputs ohne externen Modellzugriff.

### Replay

`run_teacher_jobs.py --mode replay --replay-input <jsonl>` übernimmt vorbereitete Kandidaten im Teacher-Output-Format. Damit lässt sich später ein externer Teacher-Lauf in dieselbe Struktur zurückspielen, ohne das Repo umzubauen.

## Menschlicher Review bleibt nötig für

- fachliche Freigabe vor Promotion nach `data/gold/`
- Grenzfälle mit möglicher Versionsabhängigkeit
- Fälle, in denen eine Rückfrage oder Eskalation möglicherweise anders formuliert werden sollte
- Entscheidung, welche Teacher-Kandidaten wirklich in einen späteren LoRA-Export gehören

## Rebuild

```bash
python scripts/build_jaws_support_data.py
python scripts/run_teacher_jobs.py --jobs data/derived/teacher_jobs/JAWS/DE/seed_generation_jobs.jsonl --output data/derived/teacher_outputs/JAWS/DE/seed_teacher_outputs.jsonl --mode stub --teacher-model teacher-stub-no-llm --teacher-run-id jaws_de_teacher_stub_run_v1
python scripts/review_teacher_outputs.py --input data/derived/teacher_outputs/JAWS/DE/seed_teacher_outputs.jsonl --output data/derived/teacher_outputs/JAWS/DE/reviewed_teacher_outputs.jsonl --reviewer codex-demo --approve-id jaws_de_teacher_stub_run_v1::sft_direct_jaws_cursor --approve-id jaws_de_teacher_stub_run_v1::sft_steps_teams_zoom --approve-id jaws_de_teacher_stub_run_v1::eval_web_pdf_auto_read --approve-id jaws_de_teacher_stub_run_v1::eval_virtual_pc_cursor_highlight --reject-id jaws_de_teacher_stub_run_v1::sft_escalate_mouse_mode
python scripts/promote_teacher_outputs.py --input data/derived/teacher_outputs/JAWS/DE/reviewed_teacher_outputs.jsonl --train-output data/gold/train/sft/JAWS/DE/promoted_seed_sft_samples.jsonl --eval-output data/gold/eval/JAWS/DE/promoted_seed_eval_cases.jsonl
python scripts/validate_teacher_pipeline.py --jobs data/derived/teacher_jobs/JAWS/DE/seed_generation_jobs.jsonl --outputs data/derived/teacher_outputs/JAWS/DE/reviewed_teacher_outputs.jsonl --gold-sft data/gold/train/sft/JAWS/DE/promoted_seed_sft_samples.jsonl --gold-eval data/gold/eval/JAWS/DE/promoted_seed_eval_cases.jsonl
```

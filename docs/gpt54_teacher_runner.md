# GPT-5.4 Teacher Runner fuer Wave1

## Ziel

Der primaere Teacher-Pfad fuer Wave1 ist Codex selbst.

Codex laeuft in dieser Umgebung auf GPT-5.4, liest bestehende Wave1-Jobs direkt aus dem Repo, formuliert dokumentationsgebundene Teacher-Antworten und schreibt daraus strukturierte Roh-Responses und reviewbare Teacher-Outputs.

Der Pfad bleibt getrennt:

- `data/derived/teacher_jobs/...`: stabile Jobquelle
- `data/derived/teacher_outputs/...`: rohe Teacher-Responses und reviewbare Outputs
- `data/gold/train/...` und `data/gold/eval/...`: nur promotete Faelle

## Primärer Codex-Workflow

1. Wave1-Jobs oder eine kleine Teilmenge auswaehlen.
2. Codex liest die Job-Datei und die zugehoerigen Quellen.
3. Codex schreibt rohe Teacher-Responses im Schema `teacher_response.schema.json`.
4. `run_teacher_jobs.py --mode codex` materialisiert daraus reviewbare Teacher-Outputs.
5. Review und Promotion laufen unveraendert weiter.

## Groessere reale Codex-Welle aus Wave1

Fuer die erste groessere reale Codex-Welle wird die bereits deterministisch freigegebene Wave1-Reviewmenge als eigener Codex-Lauf materialisiert:

1. `scripts/build_wave1_codex_real_batch.py` schreibt eine stabile Job-Liste und die dazugehoerigen neuen Approve-IDs.
2. `scripts/materialize_codex_teacher_responses.py` erzeugt strukturierte Roh-Responses fuer genau diese Job-Menge.
3. `scripts/run_teacher_jobs.py --mode codex` baut daraus reviewbare Teacher-Outputs mit `teacher_provider=codex` und `teacher_model=gpt-5.4`.
4. Review und Promotion laufen unveraendert auf den neuen Codex-Artefakten.

Dadurch bleibt die Trennung klar:

- alter Stub-/Fixture-Stand bleibt unveraendert erhalten
- neue Codex-Roh-Responses sind separat nachvollziehbar
- neue reviewed Outputs und Gold-Artefakte entstehen in eigenen Dateien

Beispiel fuer die kleine Wave1-Teilmenge:

```bash
python scripts/build_wave1_gpt54_subset.py
python scripts/run_teacher_jobs.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/wave1_gpt54_subset_job_ids.txt ^
  --mode codex ^
  --import-input data/derived/teacher_outputs/JAWS/DE/wave1_codex_gpt54_raw_responses.jsonl ^
  --output data/derived/teacher_outputs/JAWS/DE/wave1_codex_gpt54_teacher_outputs.jsonl
```

`--import-input` ist hier kein externer API-Import, sondern der Pfad zu den von Codex selbst erzeugten Roh-Responses.

## Kennzeichnung echter Codex-Teacher-Runs

Ein echter Codex/GPT-5.4-Run wird so markiert:

- `teacher_provider: codex`
- `teacher_model: gpt-5.4`
- eigener `teacher_run_id`
- `generation_mode: codex_teacher_gpt54_wave1_v1` oder spaetere Versionen

Dadurch bleiben echte Codex-Outputs klar getrennt von:

- `teacher_runner_stub_*`
- `teacher_runner_replay_*`
- `teacher_runner_import_fixture_*`

## Fallback-Pfad

Ein externer Replay-/Import-Pfad bleibt erhalten, ist aber nur Nebenweg:

- fuer spaetere Reproduktion
- fuer externe Batch-Laeufe ausserhalb dieses Repo-Runs
- fuer Rueckspielung bereits vorhandener strukturierter Teacher-Responses

## Review und Promotion

Der nachgelagerte Pfad bleibt gleich:

1. rohe Responses validieren
2. Teacher-Outputs reviewen
3. nur `human_reviewed` nach Gold promoten
4. erst dann in den Qwen-Export gehen

## Manuell pruefen vor dem ersten groesseren LoRA-Run

- Rueckfragen bleiben genau eine fokussierte Frage
- Schrittfolgen enthalten nur belegte Schritte
- Eskalationsfaelle benennen die Evidenzgrenze explizit
- Antworten bleiben knapp und dokumentationsgebunden
- Train/Eval bleiben auf Chunk-Ebene getrennt

## Scale-up ab Wave2

Fuer groessere Wellen reicht die feste Wave1-Selektion nicht mehr. Der skalierbare Pfad basiert deshalb auf drei zusaetzlichen Bausteinen:

1. `scripts/build_jaws_teacher_wave.py`
   - parametrische Train-/Eval-Ziele pro Falltyp
   - deterministische Exclusions gegen bereits promotete Chunks
   - balancierte Auswahl ueber Dokumente und Falltypen
2. `scripts/select_teacher_wave_review_ids.py`
   - skalierbare Freigabeziele pro Split und Falltyp
   - Exclusions gegen bestehenden Gold-Bestand
   - nachvollziehbare Shortage-Reports
3. `scripts/consolidate_gold_teacher_sets.py`
   - de-dupliziert den globalen Gold-Bestand
   - loest historische Split-Kollisionen deterministisch
   - schreibt einen konsolidierten Train-/Eval-Stand fuer LoRA und Eval

Typischer Ablauf fuer eine groessere Welle:

```bash
python scripts/build_jaws_teacher_wave.py ^
  --wave-id jaws_de_teacher_wave_v2_scaleup ^
  --exclude-dir data/gold/train/sft/JAWS/DE ^
  --exclude-dir data/gold/eval/JAWS/DE ^
  --train-target clarification=60 ^
  --train-target uncertainty_escalation=150 ^
  --train-target step_by_step=60 ^
  --train-target troubleshooting=220 ^
  --train-target faq_direct_answer=350

python scripts/run_teacher_jobs.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave2_scaleup_generation_jobs.jsonl ^
  --mode stub ^
  --output data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_teacher_outputs.jsonl

python scripts/select_teacher_wave_review_ids.py ^
  --input data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_teacher_outputs.jsonl ^
  --approve-output data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_approve_ids.txt ^
  --reject-output data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_reject_ids.txt ^
  --report-output data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_review_selection_report.json

python scripts/materialize_codex_teacher_responses.py ^
  --input data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_reviewed_teacher_outputs.jsonl ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave2_scaleup_generation_jobs.jsonl ^
  --output data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_codex_gpt54_raw_responses.jsonl ^
  --teacher-run-id jaws_de_wave2_codex_gpt54_run_v1 ^
  --generation-mode codex_teacher_gpt54_scaleup_v1

python scripts/run_teacher_jobs.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave2_scaleup_generation_jobs.jsonl ^
  --mode codex ^
  --import-input data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_codex_gpt54_raw_responses.jsonl ^
  --output data/derived/teacher_outputs/JAWS/DE/wave2_scaleup_codex_gpt54_teacher_outputs.jsonl

python scripts/consolidate_gold_teacher_sets.py ^
  --train-dir data/gold/train/sft/JAWS/DE ^
  --eval-dir data/gold/eval/JAWS/DE ^
  --train-output data/gold/train/sft/JAWS/DE/consolidated_gold_v1_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/consolidated_gold_v1_eval_cases.jsonl ^
  --report-output data/derived/teacher_outputs/JAWS/DE/consolidated_gold_v1_report.json
```

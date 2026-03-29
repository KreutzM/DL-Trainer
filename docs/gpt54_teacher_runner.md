# GPT-5.4 Teacher Runner

## Ziel

Der produktive Teacher-Pfad fuer JAWS-DE nutzt Codex CLI direkt und laeuft im MVP dreistufig:

1. User-Simulation
2. Support-Answering
3. Judge/Qualitaetsgate

Nach dem Clean-Cut bleiben im aktiven Repo nur noch:

- Teacher-Jobs als stabile Eingabe
- echte Codex-CLI-Runner fuer Simulation, Answering und Review
- Review- und Promotion-Skripte

Es werden keine committed JAWS-DE-Teacher-, Gold- oder Export-Artefakte mehr als produktiver Stand mitgefuehrt. Neue Batches muessen bei Bedarf frisch erzeugt werden.

## Produktiver Ablauf

1. Teacher-Jobs bauen oder bestehende Jobs auswaehlen.
2. Bevorzugt `scripts/run_codex_cli_support_mvp_pipeline.py` starten; der Wrapper setzt die produktiven Stage-Defaults und schreibt einen konsolidierten Laufreport.
3. `scripts/run_codex_cli_user_sim_batch.py` erzeugt realistische User-Anfragen.
4. `scripts/run_codex_cli_support_answer_batch.py` beantwortet genau diese Anfragen dokumentationsgebunden.
5. `scripts/run_codex_cli_support_judge_batch.py` bewertet Anfrage plus Antwort streng und schreibt nur belastbare Outputs als `codex_reviewed` weiter.
5. `promote_teacher_outputs.py --allow-codex-reviewed` kann diese Outputs bei Bedarf nach Gold uebernehmen.
6. Neue Gold- und Export-Staende entstehen erst wieder aus diesen echten reviewed Outputs.

## Start des effizienten MVP-Pfads

Empfohlener Einstieg:

```bash
python scripts/run_codex_cli_support_mvp_pipeline.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_mvp_v1_job_ids.txt ^
  --run-name codex_cli_support_mvp_v2 ^
  --promote
```

Kostenbewusste Defaults:

- User-Simulation: `gpt-5.4-mini`, `reasoning-effort=low`, `batch-size=8`
- Answering: `gpt-5.4`, `reasoning-effort=medium`, `batch-size=4`
- Judge/Gate: `gpt-5.4-mini`, `reasoning-effort=medium`, `batch-size=8`

## Direkte Stage-Starts

Beispiel fuer einen kleinen Batch ueber alle fuenf Task-Typen:

```bash
python scripts/run_codex_cli_user_sim_batch.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_mvp_v1_job_ids.txt ^
  --output data/derived/user_simulations/JAWS/DE/codex_cli_support_mvp_v1_user_simulations.jsonl ^
  --report-output data/derived/user_simulations/JAWS/DE/codex_cli_support_mvp_v1_user_simulations_report.json ^
  --artifact-dir data/derived/teacher_runs/JAWS/DE/codex_cli_support_mvp_v1/user_simulations ^
  --simulator-run-id jaws_de_codex_cli_support_mvp_v1_user_sim ^
  --simulator-model gpt-5.4-mini ^
  --reasoning-effort low ^
  --batch-size 8
```

Weitere Stufen:

```bash
python scripts/run_codex_cli_support_answer_batch.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_mvp_v1_job_ids.txt ^
  --user-simulations data/derived/user_simulations/JAWS/DE/codex_cli_support_mvp_v1_user_simulations.jsonl ^
  --raw-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_raw_responses.jsonl ^
  --teacher-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_teacher_outputs.jsonl ^
  --report-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_answer_report.json ^
  --artifact-dir data/derived/teacher_runs/JAWS/DE/codex_cli_support_mvp_v1/answers ^
  --teacher-run-id jaws_de_codex_cli_support_mvp_v1_answer ^
  --teacher-model gpt-5.4 ^
  --reasoning-effort medium ^
  --batch-size 4

python scripts/run_codex_cli_support_judge_batch.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_mvp_v1_job_ids.txt ^
  --user-simulations data/derived/user_simulations/JAWS/DE/codex_cli_support_mvp_v1_user_simulations.jsonl ^
  --raw-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_raw_responses.jsonl ^
  --teacher-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_teacher_outputs.jsonl ^
  --judge-output data/derived/teacher_reviews/JAWS/DE/codex_cli_support_mvp_v1_judge_results.jsonl ^
  --reviewed-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_reviewed_teacher_outputs.jsonl ^
  --report-output data/derived/teacher_reviews/JAWS/DE/codex_cli_support_mvp_v1_judge_report.json ^
  --artifact-dir data/derived/teacher_runs/JAWS/DE/codex_cli_support_mvp_v1/judge ^
  --reviewer-run-id jaws_de_codex_cli_support_mvp_v1_judge ^
  --reviewer-model gpt-5.4-mini ^
  --reasoning-effort medium ^
  --batch-size 8
```

```bash
python scripts/promote_teacher_outputs.py ^
  --input data/derived/teacher_outputs/JAWS/DE/codex_cli_support_mvp_v1_reviewed_teacher_outputs.jsonl ^
  --train-output data/gold/train/sft/JAWS/DE/codex_cli_support_mvp_v1_promoted_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/codex_cli_support_mvp_v1_promoted_eval_cases.jsonl ^
  --allow-codex-reviewed
```

## Kleine Qualitaetsvalidierungswelle

Vor einer groesseren echten Produktionswelle soll fuer JAWS-DE zunaechst eine kleine, aber belastbare Validierungswelle laufen.

Empfohlener Ablauf:

```bash
python scripts/build_jaws_de_validation_wave.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-output data/derived/teacher_jobs/JAWS/DE/codex_cli_support_validation_v1_job_ids.txt ^
  --report-output data/derived/teacher_jobs/JAWS/DE/codex_cli_support_validation_v1_selection_report.json

python scripts/run_codex_cli_support_mvp_pipeline.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --job-ids-file data/derived/teacher_jobs/JAWS/DE/codex_cli_support_validation_v1_job_ids.txt ^
  --run-name codex_cli_support_validation_v2 ^
  --user-sim-batch-size 4 ^
  --judge-batch-size 4 ^
  --timeout-sec 900 ^
  --promote

python scripts/report_jaws_de_validation_wave.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl ^
  --user-simulations data/derived/user_simulations/JAWS/DE/codex_cli_support_validation_v2_user_simulations.jsonl ^
  --raw-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_validation_v2_raw_responses.jsonl ^
  --judge-output data/derived/teacher_reviews/JAWS/DE/codex_cli_support_validation_v2_judge_results.jsonl ^
  --reviewed-output data/derived/teacher_outputs/JAWS/DE/codex_cli_support_validation_v2_reviewed_teacher_outputs.jsonl ^
  --train-output data/gold/train/sft/JAWS/DE/codex_cli_support_validation_v2_promoted_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/codex_cli_support_validation_v2_promoted_eval_cases.jsonl ^
  --report-output data/derived/teacher_reviews/JAWS/DE/codex_cli_support_validation_v2_validation_report.json
```

Bewusst so gesetzt:

- `20` Jobs statt Minimalprobe
- alle `5` Task-Typen
- `10` Train / `10` Eval
- mehrere Dokumentbereiche
- kleinere User-Sim- und Judge-Batches (`4`) fuer robustere mittlere Wellen

Wichtige Interpretationsregel:

- Nicht nur auf Approval-Quote schauen.
- Besonders auf Fail-Muster bei `step_by_step` und auf task-konforme `clarification` achten.
- Eine Welle ist erst dann ein gutes Freigabesignal, wenn sowohl Gold-Train als auch Gold-Eval entstehen und die Rejects plausibel sind.

## I/O-Struktur des echten Codex-CLI-MVP-Pfads

Pro Batch:

- Jobquelle: `data/derived/teacher_jobs/...`
- User-Simulationen: `data/derived/user_simulations/...`
- Roh-Responses: `data/derived/teacher_outputs/..._raw_responses.jsonl`
- Judge-Entscheidungen: `data/derived/teacher_reviews/..._judge_results.jsonl`
- reviewbare Outputs: `data/derived/teacher_outputs/..._teacher_outputs.jsonl`
- automatisch gegatete reviewed Outputs: `data/derived/teacher_outputs/..._reviewed_teacher_outputs.jsonl`
- Ausfuehrungsartefakte: `data/derived/teacher_runs/...`

Pro Job im Artefaktordner:

- `request.json`
- `prompt.txt`
- `response_schema.json`
- `last_message.json`
- `stdout.txt`
- `stderr.txt`

Neu in den Stage-Reports:

- `runtime.configured_batch_size`
- `runtime.executed_batches`
- `runtime.completed_batches`
- `runtime.total_elapsed_ms`
- `runtime.avg_elapsed_ms_per_processed_job`
- `runtime.total_prompt_chars`
- `runtime.total_retry_attempts`

## Echte vs. Legacy-Pfade

Produktiv:

- `scripts/run_codex_cli_user_sim_batch.py`
- `scripts/run_codex_cli_support_answer_batch.py`
- `scripts/run_codex_cli_support_judge_batch.py`
- Metadaten mit `simulator_provider=codex_cli`, `teacher_provider=codex_cli`, `reviewer_provider=codex_cli`
- `generation_mode=teacher_user_simulator_codex_cli_v1`, `teacher_answer_codex_cli_v1`, `teacher_judge_codex_cli_v1`

Legacy oder Nebenweg:

- `scripts/run_codex_cli_teacher_batch.py`
- `run_teacher_jobs.py --mode stub`
- `run_teacher_jobs.py --mode replay`
- `run_teacher_jobs.py --mode import`
- `run_teacher_jobs.py --mode codex`

Diese Legacy-Pfade bleiben fuer Tests, Reproduktion oder Rueckspielung alter Artefakte erhalten, sind aber nicht mehr der primaere Weg fuer neue produktive JAWS-DE-Wellen.

## Skalierung auf groessere Wellen

Der neue Pfad ist fuer groessere Wellen vorbereitet, weil er bereits hat:

- Jobselektion per `--job-id`, `--job-ids-file`, `--limit`
- Resume ueber `--resume`
- artefaktbasierte Nachvollziehbarkeit pro Batch und Job
- getrennte Roh- und Teacher-Outputs
- stage-spezifische Batch-Defaults statt pauschaler Einzelaufrufe
- stage-spezifische Modell-/Reasoning-Defaults

Noch offen fuer sehr grosse Wellen:

- parallele Ausfuehrung mehrerer Codex-Jobs
- explizite Retry-Queues fuer Fehljobs
- ggf. Batch-Splitting ueber mehrere Worker-Maschinen

## Kennzeichnung echter MVP-Runs

Ein echter Codex-CLI-MVP-Run ist an folgenden Feldern erkennbar:

- `simulator_provider: codex_cli`
- `teacher_provider: codex_cli`
- `reviewer_provider: codex_cli`
- `simulator_model`, `teacher_model`, `reviewer_model`: produktiv stage-spezifisch, standardmaessig `gpt-5.4-mini` / `gpt-5.4` / `gpt-5.4-mini`
- eigener `simulator_run_id`, `teacher_run_id`, `reviewer_run_id`
- `generation_mode`: `teacher_user_simulator_codex_cli_v1`, `teacher_answer_codex_cli_v1`, `teacher_judge_codex_cli_v1`

## Aktiver JAWS-DE-Status

- `data/derived/teacher_outputs/JAWS/DE/` ist im aktiven Repo leer und wird erst durch neue echte Batches wieder befuellt.
- `data/gold/train/sft/JAWS/DE/` und `data/gold/eval/JAWS/DE/` sind im aktiven Repo leer.
- `data/exports/qwen_sft/JAWS/DE/` ist bewusst leer, bis neue echte Teacher-Wellen wieder einen belastbaren Gold-Stand erzeugt haben.

# JAWS-DE Workflow

Diese Datei ist die Single Source of Truth fuer den aktuell empfohlenen produktiven JAWS-DE-Pfad.

Die maschinenlesbare Current-Baseline fuer denselben Stand steht in `docs/jaws_de_current_baseline.json`.

## Produktiver Hauptpfad

1. Rohquelle: `data/raw/JAWS/DE/Converted-Help-Files/`
2. Normalisierung: `data/normalized/JAWS/DE/`
3. Chunking: `data/derived/chunks/JAWS/DE/`
4. Jobaufbau: `data/derived/teacher_jobs/JAWS/DE/`
5. Teacher-Lauf: `scripts/run_codex_cli_support_mvp_pipeline.py`
6. Promotion: `scripts/promote_teacher_outputs.py`
7. Export: `scripts/export_qwen_sft.py`
8. Training: `training/transformers/` plus `scripts/run_qwen_lora_training.py`

## Aktuell massgeblicher committed Baseline-Stand

Der aktuell empfohlene committed Downstream-Stand fuer JAWS-DE ist der kontrollierte Gold-Stand `openrouter_gpt54_controlled_gold_v16`.

Massgebliche Dateien:

- `data/derived/user_simulations/JAWS/DE/jaws_de_shadow_2026_04_04_user_answer_v16_openrouter_gpt54_curated_pre_gold_wave_user_simulations.jsonl`
- `data/derived/teacher_outputs/JAWS/DE/jaws_de_shadow_2026_04_04_user_answer_v16_openrouter_gpt54_curated_pre_gold_wave_teacher_outputs.jsonl`
- `data/derived/teacher_outputs/JAWS/DE/jaws_de_shadow_2026_04_04_user_answer_v16_openrouter_gpt54_curated_pre_gold_wave_reviewed_teacher_outputs.jsonl`
- `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_user_answer_v16_openrouter_gpt54_curated_pre_gold_wave_judge_results.jsonl`
- `data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl`
- `data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl`
- `data/exports/qwen_sft/JAWS/DE/current/`
- `training/transformers/jaws_de_current.yaml`
- `data/derived/teacher_jobs/JAWS/DE/current_generation_selection.json`

Verwendung:

- Diese Baseline ist der sichere Ausgangspunkt fuer Validierung, Export und das naechste Training.
- Neue produktive Wellen sollen nicht auf alten Prefixen aufsetzen.
- Neue Laeufe muessen einen neuen `run_name` verwenden.
- Fresh Runs sollen die aktuelle Job-Selektion ueber `current_generation_selection.json` und nicht ueber historisch klingende Dateinamen adressieren.

## Historische Prefixe

Diese Prefixe bleiben bewusst im Repo, sind aber nicht der aktuelle produktive Standard:

- `codex_cli_support_mvp_v1`
- `codex_cli_support_mvp_v2_probe`
- `codex_cli_smoke_v1`

Einordnung:

- `mvp_v1` und `mvp_v2_probe` bleiben als historische Zwischenstaende und Vergleichsartefakte erhalten.
- Leere oder unvollstaendige historische Eval-Dateien sind kein gueltiger aktueller Export- oder Trainingsfreeze.
- `run_codex_cli_teacher_batch.py` bleibt als Legacy-/Testpfad erhalten, ist aber nicht der JAWS-DE-Produktivpfad.

## Aktueller Generierungsstandard

Der produktive JAWS-DE-Lauf ist dreistufig:

1. User-Simulation
2. Support-Answer
3. Judge/Gate

Produktive Runner:

- `scripts/run_codex_cli_user_sim_batch.py`
- `scripts/run_codex_cli_support_answer_batch.py`
- `scripts/run_codex_cli_support_judge_batch.py`
- bevorzugt orchestration ueber `scripts/run_codex_cli_support_mvp_pipeline.py`

Produktive Metadaten:

- `simulator_provider=codex_cli`
- `teacher_provider=codex_cli`
- `reviewer_provider=codex_cli`
- `generation_mode=teacher_user_simulator_codex_cli_v1`
- `generation_mode=teacher_answer_codex_cli_v1`
- `generation_mode=teacher_judge_codex_cli_v1`

Stage-Defaults:

- User-Simulation: `gpt-5.4-mini`, `reasoning-effort=low`, `batch-size=8`
- Answering: `gpt-5.4`, `reasoning-effort=medium`, `batch-size=4`
- Judge: `gpt-5.4-mini`, `reasoning-effort=medium`, `batch-size=8`

## Aktuell unterstuetzter Trainingspfad

Fuer JAWS-DE ist derzeit nur `training/transformers/` als unterstuetzter Trainingspfad dokumentiert.

Vorgehen:

1. Aktuelle Gold-Baseline validieren.
2. Export nach `data/exports/qwen_sft/JAWS/DE/current/` bauen.
3. `training/transformers/jaws_de_current.yaml` als Trainingsfreeze verwenden.
4. Vor Server-Run `scripts/preflight_qwen_lora_server.py --config training/transformers/jaws_de_current.yaml` ausfuehren.
5. Training ueber `scripts/run_qwen_lora_training.py --config training/transformers/jaws_de_current.yaml` starten.

`training/axolotl/`, `training/ms-swift/` und `training/unsloth/` bleiben generische oder historische Nebenpfade und sind fuer JAWS-DE aktuell nicht der empfohlene Standard.

## Standardbefehle

Aktuelle Baseline validieren:

```bash
python scripts/validate_jsonl.py --schema schemas/sft_sample.schema.json --input data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl
python scripts/check_provenance.py --input data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl
python scripts/validate_jsonl.py --schema schemas/eval_case.schema.json --input data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl
python scripts/check_provenance.py --input data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl
```

Aktuellen Export bauen:

```bash
python scripts/export_qwen_sft.py \
  --train-input data/gold/train/sft/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_sft_samples.jsonl \
  --eval-input data/gold/eval/JAWS/DE/openrouter_gpt54_controlled_gold_v16_promoted_eval_cases.jsonl \
  --output-dir data/exports/qwen_sft/JAWS/DE/current \
  --export-id jaws_de_controlled_gold_v16_current

python scripts/validate_qwen_sft_export.py --input-dir data/exports/qwen_sft/JAWS/DE/current
```

Lokaler Smoke auf dem aktuellen Current-Stand:

```bash
make jaws-de-current-training-smoke
```

Frischen produktiven Lauf starten:

```bash
python scripts/run_codex_cli_support_mvp_pipeline.py \
  --selection-manifest data/derived/teacher_jobs/JAWS/DE/current_generation_selection.json \
  --run-name codex_cli_support_2026_04_03 \
  --promote
```

Wichtig:

- `--run-name` muss fuer neue Wellen neu sein.
- Bereits vorhandene Run-Namen werden ohne `--resume` vom Wrapper blockiert.
- Historische Prefixe nicht fuer neue produktive Laeufe recyceln.
- Die aktuelle Fresh-Run-Selektion wird maschinenlesbar in `data/derived/teacher_jobs/JAWS/DE/current_generation_selection.json` festgehalten.

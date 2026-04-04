# DL-Trainer

Dieses Repository baut versionierte Datenartefakte aus Produkthandbuechern fuer:

- RAG-Korpora
- Teacher-generierte SFT-/LoRA-Daten
- Eval-Datensaetze
- daraus abgeleitete Trainings-Exporte

## Aktueller JAWS-DE-Standard

Die zentrale Single Source of Truth fuer den produktiven JAWS-DE-Pfad ist [`docs/jaws_de_workflow.md`](docs/jaws_de_workflow.md). Die maschinenlesbare Current-Baseline dazu steht in [`docs/jaws_de_current_baseline.json`](docs/jaws_de_current_baseline.json).

Kurzfassung:

1. `data/raw/JAWS/DE/Converted-Help-Files/` ist die kanonische Rohquelle.
2. `data/normalized/JAWS/DE/` und `data/derived/chunks/JAWS/DE/` sind die kanonischen Dokument- und Retrieval-Stufen.
3. `data/derived/teacher_jobs/JAWS/DE/` ist die stabile Eingabeschicht fuer neue Teacher-Laeufe.
4. Der produktive Generierungspfad laeuft ueber `scripts/run_codex_cli_support_mvp_pipeline.py`.
5. Der aktuell massgebliche committed Downstream-Baseline-Stand ist `codex_cli_support_validation_v2`.
6. Der aktuell unterstuetzte Trainingspfad fuer JAWS-DE laeuft ueber `training/transformers/`.
7. Der Fresh-Run-Default fuer neue produktive Wellen laeuft ueber `data/derived/teacher_jobs/JAWS/DE/current_generation_selection.json`.

Historische Prefixe wie `codex_cli_support_mvp_v1` und `codex_cli_support_mvp_v2_probe` bleiben nur als Vergleichs- oder Review-Historie im Repo und sind nicht der empfohlene Ausgangspunkt fuer neue Exporte oder Training-Runs.

## Schnellstart

### 1. Python-Umgebung

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Repo-Konsistenz und aktuelle JAWS-DE-Baseline pruefen

```bash
make validate
```

### 3. Aktuellen Trainings-Export aus der produktiven Gold-Baseline bauen

```bash
make jaws-de-current-export
```

Das erzeugt den aktuellen Qwen-SFT-Export unter `data/exports/qwen_sft/JAWS/DE/current/`.

### 4. Frischen produktiven JAWS-DE-Lauf starten

Immer mit neuem `RUN_NAME`, damit vorhandene Baselines nicht ueberschrieben werden:

```bash
make jaws-de-fresh-run RUN_NAME=codex_cli_support_2026_04_03
```

### 5. Aktuelle Trainingskonfiguration pruefen

```bash
make jaws-de-training-smoke
```

### 6. OpenRouter benchmarken, ohne den Default umzuschalten

```bash
make support-mvp-benchmark-reference BENCHMARK_NAME=jaws_de_shadow_apr2026 RUN_NAME=jaws_de_shadow_apr2026_codex
make support-mvp-benchmark-candidate BENCHMARK_NAME=jaws_de_shadow_apr2026 RUN_NAME=jaws_de_shadow_apr2026_openrouter
make support-mvp-benchmark-compare BENCHMARK_NAME=jaws_de_shadow_apr2026 REFERENCE_RUN=jaws_de_shadow_apr2026_codex CANDIDATE_RUN=jaws_de_shadow_apr2026_openrouter
```

Die Details dazu stehen in `docs/openrouter_benchmark_rollout.md`. Codex CLI bleibt bis auf Weiteres der produktive Default.

## Wichtige Pfade

- `docs/jaws_de_workflow.md` - kanonisches JAWS-DE-Runbook
- `docs/openrouter_benchmark_rollout.md` - Benchmark- und Rollout-Vorbereitung fuer OpenRouter
- `docs/jaws_de_current_baseline.json` - maschinenlesbarer Current-Baseline-Pointer
- `data/raw/JAWS/DE/` - Rohquellen
- `data/normalized/JAWS/DE/` - Normalform
- `data/derived/chunks/JAWS/DE/` - Retrieval-Chunks
- `data/derived/teacher_jobs/JAWS/DE/` - produktive Jobquellen
- `data/derived/user_simulations/JAWS/DE/` - simulierte Nutzeranfragen
- `data/derived/teacher_outputs/JAWS/DE/` - Antwort- und reviewed Teacher-Outputs
- `data/derived/teacher_reviews/JAWS/DE/` - Judge- und Pipeline-Reports
- `data/gold/train/sft/JAWS/DE/` - freigegebene Trainingsdaten
- `data/gold/eval/JAWS/DE/` - freigegebene Eval-Daten
- `data/exports/qwen_sft/JAWS/DE/current/` - aktueller Trainings-Export
- `training/transformers/` - unterstuetzter JAWS-DE-Trainingsstack

## Arbeitsprinzipien

- Rohquellen und normalisierte Dokumente bleiben Source of truth.
- Jede abgeleitete Aussage braucht Provenance.
- `data/gold/` ist reviewte Freigabezone, nicht `data/exports/`.
- Neue produktive JAWS-DE-Wellen starten von `teacher_jobs`, nicht von alten Exports.
- Legacy-, Probe- und Vergleichslaeufe duerfen existieren, muessen aber klar als historisch gelesen werden.

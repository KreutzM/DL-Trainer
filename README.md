# Support Data Pipeline Starter Repo

Dieses Repository ist ein Startgerüst für eine lokale Datenaufbereitungs- und Trainingspipeline für
Produkt-Support-Assistenten mit:

- **RAG-Korpus** aus Produkthandbüchern
- **Teacher-generierten SFT-/LoRA-Daten**
- **Qwen3-8B** als lokales Student-Modell
- **Codex CLI** als repo-zentrierte Orchestrierungsschicht

## Zielbild

1. Produkthandbücher oder dokumentierte Importquellen kanonisch unter `data/raw/` ablegen.
2. In maschinenfreundliche Markdown-Normalform unter `data/normalized/` überführen.
3. Daraus zitierfähige Chunks, Task-Cards und Synonym-Layer unter `data/derived/` bauen.
4. Mit einem starken Teacher-Modell qualitätsgesicherte Supportdaten erzeugen.
5. SFT-/LoRA-Datensätze unter `data/gold/train/` und Evals unter `data/gold/eval/` pflegen.
6. Student-Modell trainieren und gegen definierte Evals prüfen.

## Schnellstart

### 1. Python-Umgebung anlegen

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Beispiel-Daten validieren

```bash
python scripts/validate_jsonl.py --schema schemas/chunk.schema.json --input data/derived/chunks/demo_chunk_set.jsonl
python scripts/validate_metadata.py --input data/normalized/demo_product/de/manual_v1/index.meta.json
python scripts/check_provenance.py --input data/derived/task_cards/demo_task_cards.jsonl
```

### 3. JAWS-DE-Chunks aufbauen

```bash
python scripts/build_jaws_de_chunks.py
python scripts/validate_jaws_de_chunks.py
python scripts/validate_jsonl.py --schema schemas/chunk.schema.json --input data/derived/chunks/JAWS/DE/braille/chunks.jsonl
python scripts/check_provenance.py --input data/derived/chunks/JAWS/DE/braille/chunks.jsonl
```

### 4. Beispiel-Export für Training erzeugen

```bash
python scripts/export_for_training.py --input data/gold/train/sft/demo_sft_samples.jsonl --output training/exports/demo_train.jsonl
```

## Repo-Navigation

- `docs/` - Architektur, Policies, Review-Regeln, Repo-Spezifikation
- `schemas/` - JSON-Schemas für Kernartefakte
- `prompts/` - Teacher- und Judge-Prompts
- `scripts/` - reproduzierbare ETL-/Validierungs-/Export-Skripte
- `.codex/` - Codex-Konfiguration und Subagents
- `.agents/skills/` - task-spezifische Skills für Codex
- `data/` - Datenzonen (`raw`, `normalized`, `derived`, `gold`, `reports`)
- `training/` - Startpunkte für MS-SWIFT, Unsloth, Axolotl

## Arbeitsprinzipien

- **Source of truth** bleibt immer im Korpus, nicht im LoRA.
- **Alle abgeleiteten Artefakte** benötigen Provenance.
- **Nichts erfinden**: Fakten dürfen nur aus dokumentierter Quelle stammen.
- **Reviewbarkeit vor Automatisierung**: jeder Datensatz soll zurückverfolgbar und diffbar sein.

## Nächste sinnvolle Schritte

1. Eigenes Produkthandbuch oder dokumentierte Importquelle unter `data/raw/<produkt>/...` ablegen
2. `docs/metadata_schema.md` und `docs/chunking_policy.md` anpassen
3. Teacher-Prompts im Ordner `prompts/teacher/` verfeinern
4. Skripte in `scripts/` auf das reale Datenformat erweitern
5. Evals in `data/gold/eval/` aus echten Supportfällen aufbauen

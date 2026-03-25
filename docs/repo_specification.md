# Repo-Spezifikation

## Zweck

Dieses Repository dient als reproduzierbare Arbeitsumgebung für:
- Aufbereitung von Produkthandbüchern
- Aufbau lokaler RAG-Korpora
- Erzeugung von Teacher-basierten SFT-/LoRA-Datensätzen
- Evaluierung und spätere menschliche Nacharbeit

## Datenzonen

### `data/raw/`
Unveränderte Originalquellen. Nur read-only.

### `data/normalized/`
Bereinigte Normalform in Markdown plus `.meta.json`.

### `data/derived/`
Automatisch erzeugte Wissensartefakte:
- Chunks
- Task-Cards
- Synonyme
- Teacher-Outputs
- Reports

### `data/gold/`
Manuell geprüfte oder freigegebene Datensätze.
Diese Zone gilt als qualitativ höherwertig und darf nicht blind überschrieben werden.

## Artefaktklassen

1. **Document artifacts**
   - Originaldateien
   - bereinigte Markdown-Normalform
   - Dokument-Metadaten

2. **Retrieval artifacts**
   - Chunks
   - Chunk-Titel
   - Kurzbeschreibungen
   - Synonym-Layer
   - optionale Query-Expansion-Einträge

3. **Training artifacts**
   - Supportdialoge im `messages`-Format
   - Preference-Paare
   - Teacher-Outputs
   - Review-Flags

4. **Evaluation artifacts**
   - Gold-Fälle
   - Rubrics
   - Modellantworten
   - Bewertungsresultate

## ID-Strategie

Empfohlene stabile IDs:
- `doc_id`: `<product>_<lang>_<manual>_<version>`
- `section_id`: `<doc_id>::sec_<slug>`
- `chunk_id`: `<section_id>::chunk_<nnn>`
- `task_card_id`: `<doc_id>::task_<slug>`
- `sample_id`: `<product>_<lang>_<running_number>`

## Reviewstatus

Empfohlene Werte:
- `draft`
- `auto_generated`
- `human_checked`
- `approved`
- `rejected`

## Commit-Konvention

Jede Änderung an Datenartefakten soll idealerweise mit einem der folgenden Präfixe beginnen:
- `raw:`
- `normalize:`
- `chunk:`
- `taskcard:`
- `teacher:`
- `train:`
- `eval:`
- `docs:`
- `schema:`

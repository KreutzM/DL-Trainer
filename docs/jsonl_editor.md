# JSONL Editor

Der lokale JSONL-Editor ist ein Browser-Werkzeug fuer reviewbare Teacher-Outputs und Gold-Dateien.

## Start

```bash
python scripts/editor_server.py --open-browser
```

Oder ueber die Wrapper im UI-Ordner:

```bash
tools/jsonl_editor/start.sh
```

```bat
tools\jsonl_editor\start.bat
```

Standardmaessig lauscht der Server auf `http://127.0.0.1:8765/`.

## Scope

- editierbar:
  - `data/derived/teacher_outputs/**/*teacher_outputs.jsonl`
  - `data/derived/teacher_outputs/**/*reviewed*.jsonl`
  - `data/gold/train/**/*.jsonl`
  - `data/gold/eval/**/*.jsonl`
- read-only:
  - `data/exports/**/*.jsonl`
  - `data/derived/chunks/**/*.jsonl`
  - `data/derived/task_cards/**/*.jsonl`
  - `*_raw_responses.jsonl`

## MVP-Funktionen

- Dateiauswahl fuer relevante JSONL-Dateien
- Filter nach Status und Freitextsuche
- Review-Modus fuer `teacher_outputs` mit:
  - vorgeschlagenem `reviewed`-Zielpfad
  - Laden eines vorhandenen `reviewed`-Stands als Overlay
  - Merge-Bericht fuer fehlende, zusaetzliche oder konfliktbehaftete IDs
  - Pending-/Decided-Zaehlern
  - `Approve + Next` / `Reject + Next`
  - Export nach `*_reviewed_*.jsonl`
- Diff-Ansicht zwischen Roh-Teacher-Output und aktuellem Bearbeitungsstand
- Promotion von `reviewed_teacher_outputs` nach:
  - `data/gold/train/**/*.jsonl`
  - `data/gold/eval/**/*.jsonl`
  - mit vorgeschlagenen Zielpfaden und Count-Vorschau
  - mit automatischen Schema- und Provenance-Checks nach dem Schreiben
- strukturierte Bearbeitung fuer:
  - SFT-Samples
  - Eval-Cases
  - Teacher-Outputs ueber ihren `candidate`
- Roh-JSON-Editor pro Row
- Source-Preview auf Basis von `source_spans`
- Schema- und Provenance-Validierung vor dem Speichern
- Save-Guard fuer `data/gold/`

## Hinweise

- Bei Gold-Aenderungen anschliessend die ueblichen Validierungsskripte laufen lassen.
- Exportdateien unter `data/exports/` bleiben read-only; Aenderungen erfolgen ueber Re-Export.
- Fuer rohe `teacher_outputs` ist der bevorzugte Pfad nicht `Speichern`, sondern `Review-Datei schreiben`.
- Fuer die Promotion nach Gold sollte bevorzugt ein `reviewed_teacher_outputs`-Stand verwendet werden, nicht der rohe Teacher-Output.
- Fuer groessere Batches gibt es zusaetzlich den Filter `nur geaenderte`.

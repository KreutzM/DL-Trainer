# Repo-Spezifikation

## Zweck

Dieses Repository ist die reproduzierbare Arbeitsumgebung fuer:

- Aufbereitung von Produkthandbuechern
- Aufbau lokaler RAG-Korpora
- Erzeugung von Teacher-basierten SFT-/LoRA-Datensaetzen
- Promotion nach Gold
- Export und Training aus freigegebenen Daten

## Datenzonen

### `data/raw/`

Kanonische Rohquellen. Nach Ablage read-only behandeln.

### `data/normalized/`

Bereinigte Markdown-Normalform mit `.meta.json`.

### `data/derived/`

Automatisch erzeugte Zwischenartefakte:

- Chunks
- Teacher-Jobs
- User-Simulationen
- Teacher-Outputs
- Teacher-Reviews

### `data/gold/`

Reviewte und freigegebene Datensaetze. Diese Zone ist fuer Downstream massgeblich.

### `data/exports/`

Abgeleitete Trainings-Exporte. Nie Source of truth.

## JAWS-DE-Festlegung

Die aktuelle JAWS-DE-Single-Source-of-Truth ist `docs/jaws_de_workflow.md`.
Die maschinenlesbare Baseline-Referenz dazu ist `docs/jaws_de_current_baseline.json`.

Dort festgelegt:

- produktiver Hauptpfad
- aktiver committed Baseline-Stand
- historische Prefixe
- unterstuetzter Trainingsstack

## Artefaktstatus

Fuer produktive Downstream-Nutzung sind nur Artefakte massgeblich, die klar als aktuelle Baseline oder frischer neuer Run eingeordnet sind.

Historische oder unvollstaendige Prefixe muessen explizit als legacy, probe oder smoke verstanden werden und duerfen nicht still als Default weiterverwendet werden.

# Training Policy

## Grundsatz

Das Student-Modell soll primaer Verhalten lernen:

- Ton
- Struktur
- Diagnosemuster
- Rueckfrageverhalten
- Eskalationslogik

Produktwissen bleibt an Korpus, Chunks und Provenance gebunden.

## JAWS-DE-Standard

Der kanonische JAWS-DE-Pfad steht in `docs/jaws_de_workflow.md`.
Die maschinenlesbare Current-Baseline dazu steht in `docs/jaws_de_current_baseline.json`.

Aktuell gilt:

- committed Produktiv-Baseline: `openrouter_gpt54_controlled_gold_v16`
- Export-Ziel: `data/exports/qwen_sft/JAWS/DE/current/`
- unterstuetzter Trainingsstack: `training/transformers/`
- Trainingsfreeze: `training/transformers/jaws_de_current.yaml`

## Nicht trainieren

- ungesicherte Produktfakten
- versionsgemischte Beispiele
- historische Probe- oder Legacy-Files
- Datensaetze ohne `review_status=promoted`

## Historische Pfade

`codex_cli_support_mvp_v1` und `codex_cli_support_mvp_v2_probe` bleiben als Vergleichsstand erhalten, sind aber kein aktueller Trainingsausgangspunkt.

# JAWS-DE Qwen-SFT Exporte

Dieser Ordner enthaelt nur abgeleitete Trainings-Exporte fuer Qwen-kompatible SFT-Loader.

## Regeln

- Gold-Daten unter `data/gold/` bleiben Source of truth.
- `train.jsonl` und `eval.jsonl` sind fuer Loader gedacht.
- `*.metadata.jsonl` und `manifest.json` halten Provenance und Rueckverfolgbarkeit.
- Bei Aenderungen immer den Export neu erzeugen statt Dateien manuell zu editieren.
- Bereinigte Pilot-Staende werden in einem eigenen Exportordner abgelegt und nicht still ueber `gold_v1/` geschrieben.
- Vollstaendige Re-Exporte des konsolidierten Gold-Stands bekommen einen eigenen klar benannten Ordner, damit sie nicht mit `gold_v1/` oder Pilot-Cleanup-Exports verwechselt werden.

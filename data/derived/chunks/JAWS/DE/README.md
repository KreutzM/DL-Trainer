# JAWS DE Chunk-Artefakte

Dieses Verzeichnis enthält die erste echte Chunking-Stufe auf Basis der freigegebenen Markdown-Normalisierung unter `data/normalized/JAWS/DE/`.

## Zielstruktur

- Pro normalisiertem Dokument ein Zielordner unter `data/derived/chunks/JAWS/DE/<doc-slug>/`
- Darin genau eine `chunks.jsonl` mit section-aware Retrieval-Chunks

## Chunking-Baseline

- primär an Markdown-Headings ausgerichtet
- kleine Einleitungsblöcke bleiben mit direkt folgenden Listen zusammen
- große Abschnitte werden entlang von Blockgrenzen kontrolliert unterteilt
- keine inhaltliche Umsortierung und keine künstliche Umschreibung
- Provenance verweist auf Rohdatei, Normalisierungsdatei und Zeilenbereich im Markdown

## Rebuild

```bash
python scripts/build_jaws_de_chunks.py
python scripts/validate_jaws_de_chunks.py
```

## Erwartete Nutzung

- Retrieval- und Embedding-Basis
- Input für spätere Task-Card-Generierung
- nachvollziehbarer Zwischenschritt für Trainingsdaten-Ableitungen

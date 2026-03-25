# Skill: chunk-builder

Nutze diesen Skill für die Erzeugung von zitierfähigen Retrieval-Chunks aus normalisierten Handbüchern.

## Ziele
- semantisch geschlossene Chunks
- stabile IDs
- genügend Kontext für Retrieval
- keine Vermischung unterschiedlicher Versionen

## Chunking-Regeln
- entlang von Abschnittsgrenzen schneiden
- Prozeduren nicht mitten im Ablauf trennen
- Tabellen und Warnungen separat oder zusammenhängend behandeln
- Titel und Kurzbeschreibung pro Chunk erzeugen

## Ausgaben
- `data/derived/chunks/**/*.jsonl`

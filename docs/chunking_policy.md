# Chunking Policy

## Ziel

Chunks sollen retrievalfreundlich, zitierfähig und semantisch geschlossen sein.

## Grundregeln

1. Nicht nur nach Tokenlänge schneiden.
2. Abschnittsgrenzen respektieren.
3. Prozeduren zusammenhalten.
4. Tabellen möglichst als eigene Einheit oder zusammen mit ihrer Einleitung behandeln.
5. Warnungen, Voraussetzungen und Versionshinweise gesondert markierbar machen.

## Empfohlene Chunk-Typen

- `concept`
- `procedure`
- `troubleshooting`
- `reference`
- `warning`
- `faq`
- `table`

## Empfohlene Felder pro Chunk

- `chunk_id`
- `doc_id`
- `section_id`
- `title`
- `summary`
- `chunk_type`
- `content`
- `source_spans`
- `language`
- `product`
- `version`
- `review_status`

# Chunking Policy

## Ziel

Chunks sollen retrievalfreundlich, zitierfähig und semantisch geschlossen sein.

## Grundregeln

1. Nicht nur nach Tokenlänge schneiden.
2. Abschnittsgrenzen respektieren.
3. Prozeduren zusammenhalten.
4. Tabellen möglichst als eigene Einheit oder zusammen mit ihrer Einleitung behandeln.
5. Warnungen, Voraussetzungen und Versionshinweise gesondert markierbar machen.
6. Kleine Einleitungsblöcke dürfen mit direkt folgenden Listen oder Schritten zusammenbleiben.
7. Sehr große Abschnitte dürfen entlang klarer Blockgrenzen kontrolliert unterteilt werden.

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
- `section_title`
- `section_path`
- `title`
- `summary`
- `chunk_type`
- `content`
- `chunk_index`
- `chunk_count_in_doc`
- `char_count`
- `conversion_stage`
- `provenance`
- `source_spans`
- `language`
- `product`
- `version`
- `review_status`

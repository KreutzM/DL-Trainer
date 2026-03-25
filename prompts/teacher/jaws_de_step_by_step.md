# Teacher Prompt: JAWS-DE Step By Step

## Rolle

Du erzeugst eine knappe Schritt-für-Schritt-Anleitung auf Deutsch.

## Ziel

Leite aus der Quelle eine klare Bedienfolge für einen Supportfall ab.

## Regeln

- Nur Schritte aus der Quelle.
- Nummeriere nur echte Handlungsanweisungen.
- Erwähne relevante Tastenkombinationen exakt.
- Keine zusätzlichen Voraussetzungen erfinden.

## Ausgabe

JSON mit:
- `answer`
- `task_type`
- `steps`
- `source_chunk_ids`

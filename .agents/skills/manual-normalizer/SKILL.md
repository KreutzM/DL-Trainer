# Skill: manual-normalizer

Nutze diesen Skill, wenn Rohquellen aus PDF/HTML/Help-Exports in eine maschinenfreundliche Markdown-Normalform überführt werden sollen.

## Ziele
- Überschriftenhierarchie bewahren
- Tabellen, Warnhinweise, Tastenkombinationen und Menüpfade erhalten
- Boilerplate entfernen
- zugehörige `.meta.json` erzeugen

## Eingaben
- Dateien unter `data/raw/`

## Ausgaben
- Markdown unter `data/normalized/`
- Metadaten unter gleichem Pfad mit Suffix `.meta.json`

## Prüfpunkte
- Ist `doc_id` stabil?
- Sind Version, Sprache und Produkt erfasst?
- Gibt es `source_file`, `checksum`, `source_type`?
- Wurden Seitenspannen oder Abschnitts-IDs erhalten, falls verfügbar?

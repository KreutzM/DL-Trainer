# AGENTS.md

## Ziel

Dieses Repository erzeugt aus Produkthandbüchern versionierte Datenartefakte für:

1. RAG-Korpora
2. SFT-/LoRA-Trainingsdaten
3. Evaluationsdatensätze

## Source of truth

- Inhalte dürfen nur aus Dateien unter `data/raw/` und `data/normalized/` abgeleitet werden.
- Keine Fakten erfinden.
- Jede abgeleitete Aussage braucht Provenance:
  - `doc_id`
  - `section_id`
  - `source_spans`
  - `transform_pipeline_version`

## Arbeitsregeln

- Bearbeite nur Dateien im vorgesehenen Zielordner.
- Überschreibe niemals manuell geprüfte Dateien unter `data/gold/`.
- Erzeuge deterministische Outputs, wenn möglich.
- Bewahre Tabellen, Warnhinweise, Tastenkombinationen und Versionshinweise.
- Wenn Unsicherheit über Quelltreue besteht, markiere den Fall statt zu raten.
- Beende jeden inhaltlichen Arbeitslauf in reviewbarem Git-Status: sinnvolle Commits, klare Zusammenfassung, kein unfertiger Rest ohne Hinweis.

## Git-Workflow

- Bündele logisch zusammengehörige Änderungen in einem Commit; trenne unabhängige Themen.
- Vermeide Sammelcommits für einen ganzen Lauf und vermeide unnötige Mini-Commits ohne Review-Wert.
- Committe nur, wenn der Stand konsistent ist: betroffene Dateien passen zusammen, relevante Checks sind gelaufen oder offene Risiken sind klar benannt.
- Lass halb fertige Massenänderungen uncommittet, statt sie in einen "WIP"-ähnlichen Commit zu drücken.
- Behandle manuell geprüfte Daten unter `data/gold/` besonders vorsichtig; ändere sie nur gezielt und nachvollziehbar.

## Push und Abschluss

- Wenn ein sinnvoller, reviewbarer Stand erreicht ist und ein Remote sauber konfiguriert ist, pushe die neuen Commits.
- Wenn Push technisch nicht möglich ist, melde das explizit mit kurzem Fehlerhinweis statt still zu scheitern.
- Gib nach jedem Arbeitslauf eine kompakte Review-Zusammenfassung aus mit:
  - Branchname
  - relevante Commit-SHA(s) oder Commit-Range
  - kurze Liste der inhaltlichen Änderungen
  - betroffene Dateien oder Verzeichnisse
  - ausgeführte Checks oder Tests mit Ergebnis
  - Hinweis, ob gepusht wurde
  - knappe Review-Empfehlung mit sinnvollem Scope

## Ausgabeformate

- `data/normalized/**/*.md` + zugehörige `.meta.json`
- `data/derived/chunks/**/*.jsonl`
- `data/derived/task_cards/**/*.jsonl`
- `data/derived/synonyms/**/*.jsonl`
- `data/derived/teacher_outputs/**/*.jsonl`
- `data/gold/train/**/*.jsonl`
- `data/gold/eval/**/*.jsonl`

## Validierung

Führe nach Änderungen mindestens aus:

```bash
python scripts/validate_metadata.py --input <datei>
python scripts/validate_jsonl.py --schema <schema> --input <jsonl>
python scripts/check_provenance.py --input <jsonl>
```

## Do not

- Keine Änderungen in `data/raw/`
- Keine Löschung von Review-Markierungen
- Keine stillen Schemaänderungen ohne Anpassung in `schemas/` und `docs/`
- Keine neuen Abhängigkeiten ohne Begründung in `docs/architecture.md`
- Keine Commits mit kaputten Schemas, offensichtlich fehlerhaften Artefakten oder halb fertigen Massenänderungen
- Keine unnötigen Binär-, Build- oder Cache-Dateien committen

## Hinweise zu Spezialisierungen

Nutze bei Bedarf die Skills in `.agents/skills/` statt diese Datei aufzublähen.
Pfadspezifische Zusatzinstruktionen dürfen in Unterordnern mit weiteren `AGENTS.md` ergänzt werden.

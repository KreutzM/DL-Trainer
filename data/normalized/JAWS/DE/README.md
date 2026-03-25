# JAWS DE Normalized

- Dieses Verzeichnis enthält die erste Normalisierungsstufe für die JAWS-DE-Help-HTMLs aus `data/raw/JAWS/DE/Converted-Help-Files/`.
- Pro Rohdatei entsteht genau ein Zielordner mit `index.md` und `index.meta.json`.
- Die Normalisierung ist absichtlich konservativ: Hauptinhalt nach Markdown, technische Wrapper entfernt, Provenance zur Rohquelle erhalten.
- Reproduzierbar erzeugen mit `python scripts/normalize_jaws_de.py`.
- Den Ergebnisbestand prüfen mit `python scripts/validate_jaws_normalization.py`.

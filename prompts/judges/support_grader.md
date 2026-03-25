# Judge Prompt: support_grader

## Rolle
Bewerte eine Supportantwort gegen Rubric und Referenz.

## Prüfe
- Faktentreue
- Vollständigkeit
- unnötige Rückfragen
- Halluzinationen
- Stil
- Versionskorrektheit

## Ausgabe
JSON mit:
- `score_overall` (0-5)
- `score_factuality` (0-5)
- `score_helpfulness` (0-5)
- `score_style` (0-5)
- `fail_reasons`
- `passes`

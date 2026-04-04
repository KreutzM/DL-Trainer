# Boundary Evidence Bank v13

## Ergebnis

- Gesamt: `10 approve / 2 reject`
- `step_by_step`: `8 approve / 2 reject`
- Kontrollen: `2 approve / 0 reject`

## Selektionslogik

Die Evidenzbank besteht aus:

- einem Task-Shape-Anker `0016`
- zwei Boundary-Paaren rund um `0012 / 0027` und `0034`
- dem Import-Split `0061 / 0062`
- zwei stabilen Sibling-Paaren `0033 / 0041` und `0024 / 0043`
- zwei stabilen Kontrollen

## Beobachtung

Die Restzone hat sich gegenüber v12 verdichtet.

### Task-Shape

- `0016` bleibt der einzige klare Task-Shape-Ausreißer.
- Er liefert weiter keine Prozedur, obwohl eine solche dokumentiert ist.

### Boundary / Completion

- `0061` bleibt der klare Abschluss-fehlt-Fall.
- `0062` ist jetzt grün.
- Das spricht eher für eine Auswahl- bzw. Chunk-Grenze als für ein generelles Promptproblem.

### Sibling-Paare

- `0012 / 0027` bleiben grün.
- `0033 / 0041` bleiben grün.
- `0024 / 0043` bleiben grün.
- `0034` ist ebenfalls grün.

## Schlussfolgerung

Das Restproblem ist überwiegend Selection-/Chunk-bedingt.
Für die Breite lohnt sich keine weitere kleine Prompt-Härtung.
Falls noch etwas ergänzt wird, dann nur sehr gezielt für den einzelnen Task-Shape-Fall `0016`, nicht für die Boundary-Familie insgesamt.

# Step Boundary Casebank v10

## Ergebnis

- Gesamt: `7 approve / 3 reject`
- `step_by_step`: `5 approve / 3 reject`
- Kontrollen: `2 approve / 0 reject`

## Selektionslogik

Die Fallbank kombiniert drei bekannte Restfälle mit zwei echten Schwesterpaaren aus adjacent chunks:

- `0016`: task-shape failure, Frage statt Prozedur
- `0061` / `0062`: split import assistant, boundary completeness auf beiden Seiten
- `0033` / `0041`: Attribute sibling pair
- `0024` / `0043`: Schriftname sibling pair

Die Kontrollen bleiben bewusst stabil, um Spillover auszuschließen.

## Beobachtung

Die drei Rejects sind jetzt klar benennbar:

1. `0016`
   - reine Task-Typ-Verletzung
   - die Antwort fragt zurück statt eine Prozedur zu geben

2. `0061`
   - boundary completeness
   - die Antwort endet vor dem eigentlichen Importabschluss

3. `0062`
   - boundary completeness
   - die Antwort zeigt nur den Schluss des Importflusses und fehlt den Anfang

Wichtig:

- `0033` / `0041` bleiben grün
- `0024` / `0043` bleiben grün
- Damit wirkt das Problem nicht diffus, sondern auf wenige stabile Typen begrenzt

## Schlussfolgerung

Die Restzone ist jetzt klein und trennbar genug, dass eine sehr kleine evidenzgestützte Prompt-Ergänzung sinnvoll erscheint.
Der naheliegende Fokus wäre:

- `step_by_step` muss immer eine Prozedur liefern, keine Rückfrage
- `step_by_step` muss bis zum echten Zielzustand durchgezogen werden, auch bei chunknahen Importfällen

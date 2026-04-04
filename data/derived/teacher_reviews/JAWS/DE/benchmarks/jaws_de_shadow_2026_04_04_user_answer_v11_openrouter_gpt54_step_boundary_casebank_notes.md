# Step Boundary Mini Prompt Pass v11

## Vergleich zu v10

- v10: `7 approve / 3 reject`
- v11: `6 approve / 4 reject`
- `step_by_step` v10: `5 approve / 3 reject`
- `step_by_step` v11: `4 approve / 4 reject`

## Beobachtung

Die kleine Prompt-Ergänzung hat die Boundary-Fallbank nicht verbessert.

Die drei bekannten Resttypen bleiben bestehen:

1. `0016`
   - Task-shape failure
   - keine Prozedur, sondern Deflektion / Rückfrage-artige Antwort

2. `0061`
   - boundary completeness
   - der entscheidende letzte Importschritt fehlt weiter

3. `0062`
   - boundary completeness
   - nur das Schlussfragment des Imports wird geliefert

Die Kontrollen bleiben stabil grün:

- `0007`
- `0010`

## Schlussfolgerung

Die Mini-Ergänzung hilft auf dieser Fallbank nicht. Sie reduziert weder den Task-Shape-Fall noch die beiden Boundary-Completeness-Fälle und zeigt keinen Spillover-Vorteil.
Für den nächsten Schritt wäre eher eine andere, noch gezieltere Prompt-Idee oder weiterhin Datensammlung sinnvoll.

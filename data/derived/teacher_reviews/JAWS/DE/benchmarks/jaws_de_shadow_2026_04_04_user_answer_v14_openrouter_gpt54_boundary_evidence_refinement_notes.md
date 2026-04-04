# Boundary Evidence Refinement v14

## Ergebnis

- Gesamt: `7 approve / 2 reject`
- `step_by_step`: `5 approve / 2 reject`
- Kontrollen: `2 approve / 0 reject`

## Selektion

Die Evidenzbank hält die beiden Restfälle eng in der Mitte:

- `0016` als Task-Shape-Anker
- `0034` als direkter Nachbar im selben Abschnitt
- `0061 / 0062` als Import-Split-Paar
- `0048` als kompletter Import-Anker
- `0012 / 0027` als grünes Kontrollpaar
- zwei weitere Controls außerhalb von `step_by_step`

## Beobachtung

Die Grenze zwischen Setup und Abschluss ist jetzt klarer als vorher:

- `0061` bleibt der einzige echte Completion-Miss.
- `0062` ist grün.
- `0048` ist grün.
- `0034` ist grün.
- `0012 / 0027` sind grün.

Damit wirkt der Rest nicht mehr wie ein Prompt-breit gelagertes Problem, sondern wie eine Kombination aus:

1. einem isolierten Task-Shape-Ausreißer (`0016`)
2. einem einzelnen boundary-nahen Import-Fragment (`0061`)

## Schlussfolgerung

Die Evidenz ist jetzt stark genug, um weitere breite Prompt-Arbeit zu verwerfen.
Der verbleibende Rest ist überwiegend Selection-/Chunk-bedingt; falls noch etwas getan wird, dann eher noch präziseres Sammeln oder eine eng begrenzte Sonderbehandlung für `0016`, nicht ein allgemeiner `step_by_step`-Promptpass.

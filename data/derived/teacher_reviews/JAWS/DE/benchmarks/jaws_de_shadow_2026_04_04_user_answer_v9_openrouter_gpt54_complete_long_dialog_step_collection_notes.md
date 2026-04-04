# Long-Dialog Step Collection v9

## Ergebnis

- Gesamt: `10 approve / 3 reject`
- `step_by_step`: `7 approve / 3 reject`
- Kontrollen: `3 approve / 0 reject`

## Selektion

Die Selektion mischt:

- bekannte vollständige lange `step_by_step`-Fälle
- neue lange, möglichst vollständige Flows mit sichtbarem Endzustand
- drei gezielte Chunk-/Scope-Grenzfälle
- drei stabile Kontrollfälle

Ziel war, vollständige Long-Dialog-Prozeduren von echten Chunk-/Scope-Problemen zu trennen.

## Beobachtung

Die drei Rejects splitten sich wieder auf zwei unterschiedliche Muster:

1. `jaws_de_teacher_wave_v1::train::step_by_step::0016`
   - Antwort liefert eine Rückfrage statt einer Prozedur.
   - Das ist ein echter Task-Type-Fehler, aber kein reines Long-Dialog-Completeness-Problem.

2. `jaws_de_teacher_wave_v1::train::step_by_step::0034`
   - Antwort startet mitten in der Prozedur und lässt die früheren Schritte aus.
   - Das ist ein Completeness-Problem mit klarer Scope-/Coverage-Komponente.

3. `jaws_de_teacher_wave_v1::train::step_by_step::0062`
   - Antwort deckt nur den Abschluss des Imports ab.
   - Auch hier fehlt der frühere Ablauf, also ein Chunk-/Scope-Grenzfall.

Die vollständigen Langläufer bleiben grün, besonders:

- `0012`
- `0024`
- `0030`
- `0041`
- `0052`

## Schlussfolgerung

Das Restmuster ist noch nicht homogen genug für eine kleine evidenzgestützte Prompt-Ergänzung.
Die nächste sinnvolle Bewegung ist weiteres Sammeln oder Isolieren von vollständigen Long-Dialog- und Chunk-Grenzfällen.

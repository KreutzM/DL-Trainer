# Large Strong Shadow Wave v15

## Ergebnis

- Gesamt: `43 approve / 1 reject`
- `step_by_step`: `11 approve / 1 reject`
- Kontrollen und die übrigen Klassen bleiben vollständig grün.

## Auswahl

Die Welle ist absichtlich breit und balanciert:

- 44 Jobs insgesamt
- 22 Train / 22 Eval
- 8 `clarification`
- 8 `faq_direct_answer`
- 12 `step_by_step`
- 8 `troubleshooting`
- 8 `uncertainty_escalation`

Das macht die Welle geeignet, um die allgemeine Stabilität des aktuellen OpenRouter-Pfads zu prüfen, ohne `step_by_step` künstlich zu dominieren.

## Beobachtung

Die breite Welle ist stabil:

- `clarification` bleibt komplett grün
- `faq_direct_answer` bleibt komplett grün
- `troubleshooting` bleibt komplett grün
- `uncertainty_escalation` bleibt komplett grün

Der einzige Reject ist:

- `jaws_de_teacher_wave_v1::train::step_by_step::0002`

Das ist ein isolierter `step_by_step`-Mischfall mit fehlendem Abschluss der ersten Prozedur. Es gibt keinen Hinweis auf ein breites Modell- oder Judge-Problem.

## Schlussfolgerung

Der aktuelle starke OpenRouter-Pfad ist breit genug stabil, um als Basis für eine größere kuratierte Shadow-/Pre-Gold-Welle zu dienen.
Die nächste Stufe sollte nicht mehr breit am Prompt schrauben, sondern den kuratierten Datensatzaufbau vorbereiten, mit `step_by_step` weiter beobachtet, aber nicht als Blocker für die Gesamtlinie behandelt.

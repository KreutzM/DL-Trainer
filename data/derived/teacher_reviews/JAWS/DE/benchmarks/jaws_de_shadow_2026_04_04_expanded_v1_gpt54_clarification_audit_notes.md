# Clarification Judge Audit

## Scope

- Fokus nur auf bestehenden `clarification`-Faellen aus den bisherigen kleinen und erweiterten Shadow-Runs.
- Wiederverwendete Judge-Staende:
  - Codex-Baseline aus `jaws_de_shadow_2026_04_04_expanded_v1_codex_reference_pipeline_report.json`
  - OpenRouter GPT-5.4 Judge v1 aus `jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1_pipeline_report.json`
  - OpenRouter GPT-5.4 Judge v2 aus `jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_judge_rubric_v2_pipeline_report.json`
  - OpenRouter GPT-5.4 Judge v3 aus `jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_judge_rubric_v3_pipeline_report.json`
- Kleiner Shadow-Run `jaws_de_shadow_2026_04_04_small_v1_openrouter_gpt54_v1_pipeline_report.json` nur als Zusatz-Check fuer das Duplikat `eval::clarification::0001`.

## Eingeschlossene Faelle

- `jaws_de_teacher_wave_v1::eval::clarification::0001`
- `jaws_de_teacher_wave_v1::eval::clarification::0002`
- `jaws_de_teacher_wave_v1::train::clarification::0003`
- `jaws_de_teacher_wave_v1::train::clarification::0008`

Das sind vier eindeutige `clarification`-Faelle. Der kleine Shadow-Run liefert keinen zusaetzlichen neuen Fall, sondern nur ein Duplikat fuer `eval::clarification::0001`.

## Ergebnis

- Drei von vier Faellen sind ueber Codex, OpenRouter v1, v2 und v3 entscheidungsstabil.
- Genau ein Fall weicht ab: `eval::clarification::0002`.
- Mismatches gegen die Codex-Baseline:
  - v1: `0/4`
  - v2: `0/4`
  - v3: `1/4`

## Wichtigster Differenzfall

`eval::clarification::0002` ist der einzige neue Nebeneffekt.

- Codex-Judge: `approve (93)`
- OpenRouter v1: `approve (88)`
- OpenRouter v2: `approve (92)`
- OpenRouter v3: `reject (41)`

Der zugrunde liegende Kandidat fragt:

> Meinen Sie die Auswahl eines Eintrags in der Anwendungsliste oder nur das Bewegen des Fokus zur Anwendungsliste?

Die v3-Begruendung ist nicht beliebig: Der Nutzer fragte explizit nach Pfeiltasten versus Anfangsbuchstaben, und die Rueckfrage weicht auf Fokusbewegung versus Auswahl aus. Gleichzeitig approven Codex, v1 und v2 denselben Fall und behandeln ihn als noch ausreichend fokussierte Klaerung. Daraus folgt: Das ist eher ein einzelner Grenzfall mit plausibler, aber schmaler v3-Ueberstrenge als ein belastbarer Hinweis auf systematische `clarification`-Instabilitaet.

## Schlussfolgerung

- `clarification` wirkt aktuell nicht systematisch instabil.
- Der neue Nebeneffekt betrifft bisher genau einen von vier Faellen.
- Eine sofortige weitere Prompt-Korrektur ist auf dieser Evidenzbasis noch nicht gut begruendet.
- Der Judge bleibt trotzdem `shadow_only`, weil der einzelne Ausreisser zeigt, dass v3 ausserhalb von `step_by_step` noch nicht voll stabil kalibriert ist.

## Empfehlung

- Prompt vorerst **nicht** erneut anfassen.
- Stattdessen den Judge unveraendert `shadow_only` lassen und zuerst einen breiteren `clarification`-/Grenzfall-Audit fahren.
- Falls sich derselbe Drift-Typ dort wiederholt, ist erst dann eine kleine `clarification`-Nachkorrektur sinnvoll.

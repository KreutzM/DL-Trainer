# JAWS-DE GPT-5.4 Judge Step Scope Re-Audit

## Was wurde korrigiert

- Judge-Prompt von `jaws_de_support_judge_v2` auf `jaws_de_support_judge_v3` angehoben
- die verschaerften Regeln fuer:
  - fehlenden letzten entscheidenden Schritt
  - vermischte Prozeduren
  - doppelte Schrittfolgen
  - Reihenfolgeprobleme
  werden jetzt ausdruecklich nur fuer `task_type=step_by_step` beschrieben
- fuer `faq_direct_answer` wird explizit festgehalten, dass vor allem inhaltliche Korrektheit, Dokumentationsbindung, Relevanz und angemessene Kuerze zaehlen und nicht versehentlich `step_by_step`-Massstaebe

## Was gleich blieb

- kein neuer Codex-Lauf
- keine neuen Kandidatenantworten
- dieselbe Codex-Baseline wie zuvor
- dieselben bestehenden OpenRouter-GPT-5.4-Kandidatenantworten

Es wurde erneut nur der Judge auf denselben 20 Kandidatenantworten ausgefuehrt.

## Re-Audit-Artefakte

- v2 -> v3 Delta: `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_rubric_v3_vs_v2_delta.json`
- v1 -> v3 Delta: `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_rubric_v3_vs_v1_delta.json`
- neuer Audit-Subset: `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_rubric_v3_audit_subset.json`
- Findings: `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_rubric_v3_findings.json`

## Kernmetriken

- OpenRouter-GPT-5.4 mit v2:
  - `17/20` approve
  - `3/20` reject
  - Durchschnittsscore `87.20`
  - `faq_direct_answer`-Durchschnitt `87.50`
  - `step_by_step`-Durchschnitt `65.00`
- OpenRouter-GPT-5.4 mit v3:
  - `17/20` approve
  - `3/20` reject
  - Durchschnittsscore `85.50`
  - `faq_direct_answer`-Durchschnitt `95.00`
  - `step_by_step`-Durchschnitt `63.75`

## Wichtigste Effekte

### Positiv: `faq_direct_answer`-Spillover ist weg

`eval::faq_direct_answer::0004` kippt von:

- v2: `reject / 62`
- v3: `approve / 91`

Damit ist genau der zuvor unerwuenschte Spillover auf `faq_direct_answer` beseitigt. Der Judge bewertet den Fall wieder als inhaltlich korrekte, dokumentationsgebundene FAQ-Antwort.

### Positiv: `step_by_step`-Haerte haelt

`eval::step_by_step::0001` bleibt klar rejected und wird sogar noch etwas haerter bewertet. Der fehlende letzte entscheidende Schritt bleibt also weiter sauber als Hauptproblem priorisiert.

`train::step_by_step::0002` bleibt ebenfalls rejected. Die Prozedurvermischung wird weiterhin als schwerwiegender `step_by_step`-Fehler erkannt.

### Negativ: neuer Nebeneffekt bei `clarification`

`eval::clarification::0002` kippt von:

- v2: `approve / 92`
- v3: `reject / 41`

Das ist kein `step_by_step`-Problem mehr, aber ein neuer Nicht-`step_by_step`-Nebeneffekt. Die Begruendung ist nicht offensichtlich unsinnig, aber der Fall zeigt, dass die Gesamtstabilitaet des Judges ausserhalb der Zielklasse weiterhin nicht voll ruhig ist.

## Klare Schlussfolgerung

- Ist die `step_by_step`-Haerte jetzt besser scoped? **Ja.**
- Ist der Spillover auf `faq_direct_answer` reduziert? **Ja, der zentrale Spillover-Fall ist beseitigt.**
- Bleibt der Judge `shadow_only`? **Ja.**

Der Fix erreicht sein unmittelbares Ziel: `step_by_step` bleibt streng, ohne den bekannten `faq_direct_answer`-Fall weiter falsch hart zu behandeln. Fuer einen Rollout reicht es trotzdem noch nicht, weil nun ein neuer `clarification`-Nebeneffekt sichtbar ist. Der naechste sinnvolle Schritt ist deshalb entweder:

1. noch ein sehr kleiner Prompt-Scope-Fix fuer `clarification`, oder
2. den Judge bewusst auf `shadow_only` belassen und erst mit breiterem Audit-Sample pruefen, ob dieser Nebeneffekt stabil reproduzierbar ist.

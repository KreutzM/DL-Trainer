# JAWS-DE GPT-5.4 Judge Audit

## Was wurde auditiert

- Referenzbasis ohne neuen Codex-Lauf:
  - `data/derived/teacher_outputs/JAWS/DE/codex_cli_support_validation_v2_reviewed_teacher_outputs.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/codex_cli_support_validation_v2_judge_results.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_codex_reference_pipeline_report.json`
- OpenRouter-GPT-5.4-Kandidat:
  - `data/derived/teacher_outputs/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1_reviewed_teacher_outputs.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1_judge_results.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1_pipeline_report.json`
- Mechanischer Audit-Subset:
  - `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_audit_subset.json`
- Manuelle Audit-Klassifikation:
  - `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_audit_findings.json`

## Wie der Audit-Subset gebildet wurde

- Fokus-Tasktypen: alle `step_by_step`- und `faq_direct_answer`-Fälle aus dem erweiterten 20er-Shadow-Benchmark
- Zusatzregeln: alle Entscheidungsdifferenzen und alle Fälle mit `abs(score_delta) >= 20`
- Ergebnis: 8 Audit-Fälle
  - 4 `step_by_step`
  - 4 `faq_direct_answer`
  - 2 echte Entscheidungsdifferenzen
  - 3 hohe Score-Deltas

Die Auswahl trennt damit bewusst zwei Dinge:

1. sensible Klassen mit bekanntem Rollout-Risiko
2. Fälle, in denen Judge-Kalibrierung und Antwortqualität am ehesten auseinanderlaufen können

## Wichtigste Differenzfälle

### `eval::faq_direct_answer::0004`

- Codex-Judge: `reject` bei `52`
- OpenRouter-Judge: `approve` bei `90`
- Plausiblere Entscheidung: **OpenRouter**
- Einordnung: **Antwortqualitätsgewinn, kein klarer Judge-Fehler**

Der Codex-Kandidat bleibt zu abstrakt und verweist nur auf die Existenz relevanter Befehle. Die OpenRouter-Antwort nennt die dokumentierten Dialogbefehle konkret. Die abweichende Freigabe wirkt deshalb fachlich richtig.

### `eval::step_by_step::0002`

- Codex-Judge: `reject` bei `64`
- OpenRouter-Judge: `approve` bei `94`
- Plausiblere Entscheidung: **OpenRouter**
- Einordnung: **Antwortqualitätsgewinn, kein klarer Judge-Fehler**

Der Codex-Kandidat enthält denselben Ablauf doppelt. Die OpenRouter-Antwort reduziert ihn auf einen sauberen einmaligen Drei-Schritt-Block. Der Konflikt kommt hier primär aus besserer Antwortqualität, nicht aus zu weicher Judge-Kalibrierung.

## Wichtigste `step_by_step`-Grenzfälle

### `eval::step_by_step::0001`

- Codex-Judge: `reject` bei `61`
- OpenRouter-Judge: `reject` bei `61`
- Einordnung: **korrekter gemeinsamer Reject**

Der Ablauf endet weiter vor dem eigentlichen Aktivieren der Braille-Kurzschrift. Genau das bleibt der wichtigste Hinweis, dass `step_by_step` weiterhin die riskanteste Klasse ist. Positiv ist nur: der frühere problematische OpenRouter-Durchwinker ist mit GPT-5.4 hier nicht mehr sichtbar.

### `train::step_by_step::0002`

- Codex-Judge: `reject` bei `82`
- OpenRouter-Judge: `reject` bei `56`
- Einordnung: **korrekter gemeinsamer Reject, OpenRouter strenger**

Beide Antworten vermischen zwei Prozeduren. Der OpenRouter-Judge priorisiert diesen Fehler härter und nachvollziehbarer. Das sieht eher nach sinnvoller Strenge als nach Fehlkalibrierung aus.

### `train::step_by_step::0001`

- Beide Judges: `approve`
- Einordnung: **stabile Positiventscheidung**

Hier zeigt sich kein Kalibrierungsproblem. Wenn die Prozedur klar, geschlossen und dokumentationsnah ist, entscheidet der OpenRouter-Judge konsistent positiv.

## Kurzfazit zur Judge-Kalibrierung

- Kein Fall `Codex approve / OpenRouter reject`
- Die zwei sichtbaren `Codex reject / OpenRouter approve`-Fälle wirken nach Sichtung beider Antworten wie **echte Qualitätsverbesserungen** des Kandidatenpfads
- Der frühere No-Go-Fall `eval::step_by_step::0001` bleibt korrekt rejected
- `step_by_step` bleibt trotzdem der Hauptblocker, weil genau dort die sensible Grenzfalllogik sitzt:
  - fehlende letzte Schritte
  - doppelte Schrittfolgen
  - Vermischung mehrerer Prozeduren
  - unklare Abschlusszustände

## Klare Schlussfolgerung

- Ist der GPT-5.4-OpenRouter-Judge aktuell brauchbar? **Ja, aber nur für Shadow/Audit.**
- Für welche Klassen wirkt er plausibel?
  - `faq_direct_answer`: **weitgehend plausibel**
  - klare `step_by_step`-Positiv- und Negativfälle: **deutlich besser als frühere OpenRouter-Läufe**
- Bleibt `step_by_step` der Hauptblocker? **Ja.**
- Was ist der nächste sinnvollste Schritt? **Eher Judge-Prompt-/Rubrik-Nachschärfung als ein weiterer Modellvergleich.**

Der Modellwechsel auf GPT-5.4 hat den Judge sichtbar verbessert. Der verbleibende Engpass ist jetzt weniger die Modelllinie als die Kalibrierung auf harte `step_by_step`-Grenzfälle. Deshalb sollte vor einem weiteren Judge-Modellvergleich zuerst die Rubrik bzw. der Judge-Prompt für diese Fehlerklassen geschärft und dann erneut auf derselben Baseline auditiert werden.

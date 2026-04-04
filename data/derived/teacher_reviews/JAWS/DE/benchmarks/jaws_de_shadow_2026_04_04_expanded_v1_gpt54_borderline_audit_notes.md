# JAWS-DE GPT-5.4 Borderline Audit

## Was auditiert wurde

- keine neuen Codex-CLI-Runs
- kein neuer Codex-Referenzlauf
- keine neuen Kandidatenantworten
- keine neue Modellfamilie
- dieselbe Codex-Baseline:
  - `data/derived/teacher_outputs/JAWS/DE/codex_cli_support_validation_v2_reviewed_teacher_outputs.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/codex_cli_support_validation_v2_judge_results.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_codex_reference_pipeline_report.json`
- dieselben bestehenden OpenRouter-GPT-5.4-Antworten:
  - `data/derived/teacher_outputs/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1_reviewed_teacher_outputs.jsonl`
- verglichene Judge-Staende:
  - `openrouter_v1`
  - `openrouter_v2`
  - `openrouter_v3`

## Wie der Borderline-Subset gebildet wurde

Der mechanische Subset liegt in:

- `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_borderline_audit_subset.json`

Regeln:

1. Fokus auf die fuenf Klassen:
   - `step_by_step`
   - `faq_direct_answer`
   - `clarification`
   - `troubleshooting`
   - `uncertainty_escalation`
2. Primaere Auswahl, wenn mindestens eines gilt:
   - Entscheidungsdifferenz zwischen Codex und einer OpenRouter-Version
   - Entscheidungsdifferenz innerhalb von OpenRouter v1/v2/v3
   - `score_spread >= 20` ueber Codex/v1/v2/v3
   - knapper Approve mit `quality_score <= 92`
   - knapper Reject mit `quality_score >= 60`
3. Coverage-Backfill:
   - falls eine Fokusklasse unter 2 Faellen bleibt, wird der informativste Restfall dieser Klasse ergaenzt

Ergebnis:

- `12` einbezogene Faelle aus `20`
- pro Task-Typ:
  - `step_by_step`: `3`
  - `faq_direct_answer`: `2`
  - `clarification`: `2`
  - `troubleshooting`: `3`
  - `uncertainty_escalation`: `2`

## Mismatch-Muster pro Judge-Version

### OpenRouter v1 vs Codex

- `2`x `Codex reject -> OpenRouter approve`
  - `eval::step_by_step::0002`
  - `eval::faq_direct_answer::0004`
- `0`x `Codex approve -> OpenRouter reject`
- `1` stabiler Reject mit hohem Score-Abstand
  - `train::step_by_step::0002`

### OpenRouter v2 vs Codex

- `1`x `Codex reject -> OpenRouter approve`
  - `eval::step_by_step::0002`
- `0`x `Codex approve -> OpenRouter reject`
- `2` stabile Rejects mit hohem Score-Abstand
  - `eval::step_by_step::0001`
  - `train::step_by_step::0002`

### OpenRouter v3 vs Codex

- `2`x `Codex reject -> OpenRouter approve`
  - `eval::step_by_step::0002`
  - `eval::faq_direct_answer::0004`
- `1`x `Codex approve -> OpenRouter reject`
  - `eval::clarification::0002`
- `2` stabile Rejects mit hohem Score-Abstand
  - `eval::step_by_step::0001`
  - `train::step_by_step::0002`

### OpenRouter-intern

- `10/12` Faelle sind ueber v1/v2/v3 entscheidungsstabil
- `2/12` Faelle haben interne OpenRouter-Disagreements
  - `eval::faq_direct_answer::0004`
  - `eval::clarification::0002`
- beide Disagreements sind `2 approve / 1 reject`
- in beiden Faellen ist die zugrunde liegende OpenRouter-Antwort ueber v1/v2/v3 identisch

Das ist wichtig: diese beiden Faelle sind echte Judge-Kalibrierungsfaelle, keine Antwortunterschiede.

## Wichtigste Borderline-Faelle

### `jaws_de_teacher_wave_v1::eval::step_by_step::0002`

- Codex: `reject / 64`
- v1: `approve / 94`
- v2: `approve / 95`
- v3: `approve / 91`
- Einordnung: **Antwortqualitaetsgewinn statt Judge-Problem**

Die Codex-Antwort dupliziert dieselbe Prozedur. Die OpenRouter-Antwort bereinigt das auf einen sauberen Drei-Schritt-Block. Alle drei OpenRouter-Judge-Versionen bleiben auf derselben Linie. Das spricht klarer fuer bessere Antwortqualitaet als fuer Judge-Milde.

### `jaws_de_teacher_wave_v1::eval::faq_direct_answer::0004`

- Codex: `reject / 52`
- v1: `approve / 90`
- v2: `reject / 62`
- v3: `approve / 91`
- Einordnung: **gemischter Fall**

Gegenueber Codex ist die OpenRouter-Antwort fachlich klar staerker, weil sie die relevanten Dialogbefehle konkret nennt. Gleichzeitig rejectet v2 dieselbe Antwort, waehrend v1 und v3 approven. Das ist kein genereller FAQ-Drift, sondern ein echter Borderline-Fall mit v2-Ueberstrenge.

### `jaws_de_teacher_wave_v1::eval::clarification::0002`

- Codex: `approve / 93`
- v1: `approve / 88`
- v2: `approve / 92`
- v3: `reject / 41`
- Einordnung: **einmaliger Clarification-Ausreisser**

Die v3-Begruendung ist fachlich noch nachvollziehbar, weil sie die engere Unterscheidung aus dem Quelltext strenger fordert. Im Gesamtbild ist es aber ein Einzelfall: Codex, v1 und v2 approven dieselbe Rueckfrage. Das sieht nach Outlier aus, nicht nach systematischem Clarification-Drift.

### `jaws_de_teacher_wave_v1::eval::step_by_step::0001`

- Codex: `reject / 61`
- v1: `reject / 61`
- v2: `reject / 38`
- v3: `reject / 24`
- Einordnung: **echte stabile Strenge**

Hier bleibt der Judge ueber alle Versionen hinweg korrekt streng. Der fehlende letzte entscheidende Schritt wird in v2/v3 sogar klarer priorisiert. Das ist kein Fehlverhalten, sondern genau die Art von Hartefall, fuer die `step_by_step` sensibel bleiben soll.

### `jaws_de_teacher_wave_v1::train::step_by_step::0002`

- Codex: `reject / 82`
- v1: `reject / 56`
- v2: `reject / 28`
- v3: `reject / 42`
- Einordnung: **gleiche Grundentscheidung, aber starke Haerte-Spreizung**

Alle vier Judge-Sichten rejecten die vermischte Prozedur. Die Score-Differenzen sind trotzdem gross. Das zeigt weniger globale Instabilitaet als vielmehr, dass `step_by_step` weiterhin die Klasse mit der staerksten Kalibrierungsempfindlichkeit bleibt.

## Kurze qualitative Einordnung

- `step_by_step` bleibt der Hauptblocker.
  - Positiv: harte Fehlfaelle werden jetzt stabil erkannt.
  - Negativ: genau dort bleiben die groessten Score-Spreads und damit die meiste Kalibrierungsunsicherheit.
- `faq_direct_answer` wirkt nach der Scope-Korrektur wieder plausibel.
  - Der zentrale Problemfall ist nicht mehr breit systematisch, sondern ein einzelner v2-Borderline-Reject.
- `clarification` zeigt weiter keinen breiten Drift.
  - Der neue v3-Nebeneffekt bleibt sichtbar, wirkt im breiteren Sample aber eher wie ein Ausreisser.
- `troubleshooting` und `uncertainty_escalation` wirken im Subset am stabilsten.
  - Dort sieht man nur knappe Approvals, aber keine Entscheidungsumschlaege.

## Klare Schlussfolgerung

- Bleibt der Judge `shadow_only`? **Ja.**
- Ist er stabil genug fuer groessere Shadow-Wellen als Audit-/Sekundaerjudge? **Ja, vorsichtig ja.**
- Relativ brauchbare Klassen:
  - `troubleshooting`
  - `uncertainty_escalation`
  - `faq_direct_answer` mit dem bekannten einen Borderline-Fall
  - `clarification` ausserhalb des einzelnen v3-Ausreissers
- Problematische Klasse:
  - `step_by_step`

## Naechster sinnvoller Schritt

Eher **weiteres Auditieren** als sofort neues Prompt-Tuning.

Begruendung:

- Der breitere Borderline-Subset zeigt jetzt eher wenige isolierte Problemfaelle als breiten nicht-`step_by_step`-Drift.
- Ein weiterer schneller Prompt-Eingriff wuerde vor allem auf einen einzelnen `clarification`-Ausreisser reagieren.
- Fuer die Rollout-Entscheidung ist jetzt wertvoller, ob sich diese Muster in groesseren Shadow-Wellen wiederholen.

Pragmatische Reihenfolge:

1. Judge weiter `shadow_only` lassen.
2. Groessere Shadow-Wellen mit demselben Judge als Audit-/Sekundaerjudge zulassen.
3. `step_by_step` und `clarification::0002`-aehnliche Faelle in diesen Wellen gezielt beobachten.
4. Nur wenn sich der Clarification-Ausreisser oder neue Nicht-`step_by_step`-Spillover wiederholen, gezielt Prompt-Tuning nachschieben.

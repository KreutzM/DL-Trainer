# JAWS-DE GPT-5.4 Judge Rubric Hardening Re-Audit

## Was wurde geaendert

- Judge-Prompt von `jaws_de_support_judge_v1` auf `jaws_de_support_judge_v2` angehoben
- gezielte Nachschaerfung fuer `step_by_step`:
  - fehlender letzter entscheidender Schritt ist schwerwiegend
  - Vermischung verschiedener Prozeduren ist schwerwiegend
  - Duplikation ist relevant, aber nachrangig gegenueber inhaltlicher Unvollstaendigkeit
  - Struktur-/Formatmangel sind nachrangig gegenueber fachlicher Vollstaendigkeit und korrekter Reihenfolge

## Was bewusst gleich blieb

- kein neuer Codex-Lauf
- keine neuen Kandidatenantworten
- dieselbe Codex-Baseline wie im vorigen Audit:
  - `data/derived/teacher_outputs/JAWS/DE/codex_cli_support_validation_v2_reviewed_teacher_outputs.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/codex_cli_support_validation_v2_judge_results.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_codex_reference_pipeline_report.json`
- dieselben OpenRouter-GPT-5.4-Kandidatenantworten wie zuvor:
  - `data/derived/teacher_outputs/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1_teacher_outputs.jsonl`

Es wurde nur der Judge auf denselben 20 Kandidatenantworten neu ausgefuehrt.

## Re-Audit-Artefakte

- Vorher/Nachher-Diff: `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_rubric_v2_delta.json`
- Neuer Audit-Subset: `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_rubric_v2_audit_subset.json`
- Manuelle Findings: `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_rubric_v2_findings.json`

## Kernmetriken

- OpenRouter-GPT-5.4 vorher:
  - `18/20` approve
  - `2/20` reject
  - Durchschnittsscore `90.80`
  - `step_by_step`-Durchschnitt `77.25`
- OpenRouter-GPT-5.4 nach Rubrik-Haertung:
  - `17/20` approve
  - `3/20` reject
  - Durchschnittsscore `87.20`
  - `step_by_step`-Durchschnitt `65.00`
- Codex-Referenz:
  - `16/20` approve
  - `4/20` reject
  - Durchschnittsscore `88.70`
  - `step_by_step`-Durchschnitt `75.75`

Wichtig: Die Re-Audit-Ausfuehrung hatte zunaechst vier OpenRouter-Timeouts. Diese wurden auf exakt denselben Antworten in kleineren Batches nachgezogen und danach in einen vollstaendigen 20er-Report zusammengefuehrt. Es wurde nichts an Antworten oder Baselines ausgetauscht.

## Wichtigste Veraenderungen

### `eval::step_by_step::0001`

- vorher: `reject / 61`
- nachher: `reject / 38`

Das ist die gewuenschte Richtung. Der neue Judge fokussiert jetzt klar auf den fehlenden letzten entscheidenden Schritt zur Aktivierung von Braille-Kurzschrift. Die Begruendung ist fachlich sauberer als zuvor.

### `train::step_by_step::0002`

- vorher: `reject / 56`
- nachher: `reject / 28`

Auch das ist die gewuenschte Richtung. Die Vermischung zweier Prozeduren wird jetzt explizit als Hauptfehler behandelt, statt nur als allgemeine Unschaerfe.

### `eval::faq_direct_answer::0004`

- vorher: `approve / 90`
- nachher: `reject / 62`

Das ist der wichtigste Nebenbefund. Die Antwort ist weiterhin lang und nicht ideal kuratiert, beantwortet die Frage aber inhaltlich korrekt und deutlich konkreter als die Codex-Referenz. Der neue Reject wirkt deshalb eher wie moegliche Ueberhaertung ausserhalb des eigentlich adressierten `step_by_step`-Problems.

## Wirkung auf die Judge-Kalibrierung

- Positiv:
  - `step_by_step` ist sichtbar besser kalibriert
  - fehlende letzte Schritte und Prozedurvermischung werden klarer und haerter gewichtet
  - die Abweichungen zur Codex-Baseline sinken von `2` auf `1`
- Weiter offen:
  - die neue Haertung spillt mindestens in einen `faq_direct_answer`-Fall hinein
  - `step_by_step` bleibt trotz besserer Kalibrierung die empfindlichste Klasse

## Klare Schlussfolgerung

- Ist der Judge besser kalibriert? **Ja, fuer `step_by_step` klar sichtbar.**
- Bleibt `step_by_step` Hauptblocker? **Ja.**
- Bleibt der Judge `shadow_only`? **Ja.**

Der Judge ist nach dieser Nachschaerfung sicherer fuer harte `step_by_step`-Grenzfaelle, aber noch nicht release-reif. Die naechste sinnvolle Arbeit ist nicht sofort ein weiterer Modellvergleich, sondern eine kleinere Prompt-Nachkorrektur: die `step_by_step`-Haertung sollte noch expliziter task-gebunden formuliert werden, damit sie nicht auf `faq_direct_answer` uebergreift. Danach sollte derselbe Baseline-Audit erneut gefahren werden.

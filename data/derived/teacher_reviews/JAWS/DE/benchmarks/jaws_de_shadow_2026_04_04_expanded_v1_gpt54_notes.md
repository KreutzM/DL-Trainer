# JAWS-DE GPT-5.4 Expanded Shadow Benchmark

## Was wurde verglichen

- Referenzbasis ohne neuen Codex-Lauf: `codex_cli_support_validation_v2`
- Wiederverwendete Codex-Artefakte:
  - `data/derived/teacher_outputs/JAWS/DE/codex_cli_support_validation_v2_reviewed_teacher_outputs.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/codex_cli_support_validation_v2_judge_results.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_codex_reference_pipeline_report.json`
- Neuer OpenRouter-Kandidatenlauf: `jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1`
- Vergleichsartefakt: `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_comparison.json`
- Judge-Cross-Check: `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_expanded_v1_gpt54_judge_crosscheck.json`

## Subset-Bildung

- Selection manifest: `data/derived/teacher_jobs/JAWS/DE/shadow_benchmark_2026_04_04_expanded_v1_selection.json`
- Groesse: 20 Jobs
- Verteilung: 10 Train / 10 Eval
- Task-Verteilung: je 4 `clarification`, `faq_direct_answer`, `step_by_step`, `troubleshooting`, `uncertainty_escalation`
- Warum dieses Subset: Es ist exakt die bestehende Codex-Validierungsbasis `codex_cli_support_validation_v2` und damit job-identisch vergleichbar, waehrend es alle vier vorhandenen `step_by_step`-Faelle enthaelt.

## Verwendetes OpenRouter-Profil

- Profile set: `support_mvp_openrouter_gpt54_candidate`
- `user_simulation`: `openai/gpt-5.4-mini`
- `answer`: `openai/gpt-5.4`
- `judge`: `openai/gpt-5.4`
- Keine Profilanpassung gegenueber dem vorigen GPT-5.4-Shadow-Run.

## Kernmetriken

- Referenz `codex_cli_support_validation_v2`: 20/20 verarbeitet, 16 Approvals, 4 Rejects, durchschnittlicher Judge-Score `88.70`
- Kandidat `jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1`: 20/20 verarbeitet, 18 Approvals, 2 Rejects, durchschnittlicher Judge-Score `90.80`
- Entscheidungs-Matrix Codex-Judge -> OpenRouter-Judge:
  - `approve -> approve`: 16
  - `approve -> reject`: 0
  - `reject -> approve`: 2
  - `reject -> reject`: 2
- Stage-Laufzeiten:
  - User-Sim: Codex `57.7s`, OpenRouter `21.1s`
  - Answer: Codex `229.8s`, OpenRouter `79.5s`
  - Judge: Codex `64.0s`, OpenRouter `60.5s`
- Retries: auf beiden Seiten `0`

## Token- und Kosten-Sichtbarkeit

- OpenRouter-Usage aus 12 Batch-Responses:
  - Prompt-Tokens: `38378`
  - Completion-Tokens: `14008`
  - Reasoning-Tokens: `0`
- Verlaessliche Kostenpraezision ist fuer diesen Lauf nicht verfuegbar: Die gespeicherten Responses enthalten keine belastbare `total_cost`-Angabe.

## Wichtigste qualitative Befunde

### User-Sim

Die User-Simulation bleibt auf diesem groesseren Subset stabil. Es gab keine offensichtlichen Struktur- oder Schemaprobleme, keine Retries und keine Ausfaelle. Fuer weitere Shadow-Runs ist die Stage belastbar genug.

### Answer

OpenRouter-GPT-5.4 wirkt auf dem erweiterten Subset weiterhin als serioeser Kandidat.

- `eval::faq_direct_answer::0004`: Codex blieb zu allgemein und wurde dafuer abgelehnt. OpenRouter listet die dokumentierten Dialog-Befehle konkret auf und wirkt dadurch klar hilfreicher und dokumentationsnaeher.
- `eval::step_by_step::0002`: Codex erzeugte denselben Ablauf zweimal und fiel daran. OpenRouter liefert eine saubere, einmalige Drei-Schritt-Fassung; hier sieht die Freigabe wie ein echter Antwortqualitaetsgewinn aus und nicht wie Judge-Drift.
- `eval::step_by_step::0001`: Der bekannte risikoreiche Braille-Kurzschrift-Fall bleibt auch unter GPT-5.4 unvollstaendig und wird weiterhin abgelehnt. Der Risikobereich verschwindet also nicht.

### Judge

Der Judge ist besser kalibriert als in den frueheren OpenRouter-Laeufen, aber noch nicht komplett freigegeben.

- Positiv: Kein Fall `Codex approve / OpenRouter reject`. Der OpenRouter-Judge hat also auf diesem Subset keine neuen Ueberhaerten eingefuehrt.
- Positiv: `eval::step_by_step::0001` bleibt rejected. Der frueher beobachtete problematische Durchwinkler fuer einen offensichtlichen `step_by_step`-Grenzfall ist damit weiterhin nicht zurueckgekehrt.
- Positiv: `train::step_by_step::0002` bleibt ebenfalls rejected; OpenRouter begruendet den Fall sogar strenger und plausibler als die Codex-Basis, weil zwei Prozeduren vermischt werden.
- Restunsicherheit: Zwei ehemals von Codex abgelehnte Faelle werden jetzt freigegeben:
  - `eval::faq_direct_answer::0004`
  - `eval::step_by_step::0002`

Nach Sichtung der Antworten wirken beide Freigaben eher wie echte Answer-Verbesserungen als wie klare Judge-Fehlkalibrierung. Trotzdem bleibt der Judge die sensibelste Stage, weil die Zahl der `step_by_step`-Grenzfaelle trotz Erweiterung immer noch klein ist.

## Gesamteinschaetzung pro Stage

- `user_simulation`: belastbar fuer groessere Shadow-Runs
- `answer`: belastbar fuer groessere Shadow-Runs; derzeit der staerkste OpenRouter-Kandidat
- `judge`: verbessert und nicht mehr klarer No-Go, aber weiter nur `shadow_only` bzw. Audit-Modus

## Handlungsempfehlung

1. `user_simulation` und `answer` mit demselben GPT-5.4-Profil in einem noch groesseren Shadow-Run weiter testen.
2. `judge` vorerst nicht selektiv freigeben; stattdessen weitere `step_by_step`-reiche Audits und manuelle Sichtung von Entscheidungsdifferenzen fahren.
3. Als naechsten Schritt einen weiteren GPT-5.4-Shadow-Run mit zusaetzlichen `step_by_step`- und `faq_direct_answer`-Grenzfaellen aufsetzen und die neuen OpenRouter-Antworten erneut gegen die bestehende Codex-Judge-Basis spiegeln.

## Klare Schlussfolgerung

- Ist GPT-5.4 ueber OpenRouter fuer User-Sim belastbar? **Ja, fuer weitere Shadow-Runs.**
- Ist GPT-5.4 ueber OpenRouter fuer Answer belastbar? **Ja, ebenfalls fuer weitere Shadow-Runs und aktuell der staerkste Rollout-Kandidat.**
- Ist der Judge inzwischen brauchbar? **Verbessert, aber weiter der Hauptblocker fuer jede echte Freigabe.**
- Naechster sinnvollster Schritt: **groesserer GPT-5.4-Shadow mit noch mehr `step_by_step`-Grenzfaellen und weiterem Judge-Audit, ohne Default-Wechsel.**

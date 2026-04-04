# OpenRouter Benchmark Und Rollout

Der produktive Default im JAWS-DE-Support-MVP bleibt vorerst Codex CLI. OpenRouter wird in Schritt 3 nur als kontrollierter Benchmark-Kandidat vorbereitet.

## Profilsets

Die Benchmark-Laeufe bauen auf den bestehenden Profilsets in `config/llm_stage_profiles.json` auf:

- `support_mvp_default`: Codex-Referenzprofil fuer reproduzierbare Baseline-Laeufe
- `support_mvp_openrouter_candidate`: OpenRouter-Kandidatenprofil fuer Shadow- und Vergleichslaeufe

Vor Benchmark-Laeufen kann der Kandidat separat geprueft werden:

```bash
python scripts/preflight_llm_profiles.py --profile-set support_mvp_openrouter_candidate
```

## Benchmark-Einstiege

Ein Benchmark besteht aus zwei getrennten Pipeline-Laeufen mit identischem Selection-Manifest, aber unterschiedlichen Profilsets.

Codex-Referenzlauf:

```bash
make support-mvp-benchmark-reference BENCHMARK_NAME=jaws_de_shadow_apr2026 RUN_NAME=jaws_de_shadow_apr2026_codex
```

OpenRouter-Kandidatenlauf:

```bash
make support-mvp-benchmark-candidate BENCHMARK_NAME=jaws_de_shadow_apr2026 RUN_NAME=jaws_de_shadow_apr2026_openrouter
```

Beide Targets verwenden:

- dasselbe Selection-Manifest `data/derived/teacher_jobs/JAWS/DE/current_generation_selection.json`
- explizite Profilsets statt impliziter Legacy-Overrides
- Benchmark-Metadaten im Pipeline-Report (`benchmark.name`, `benchmark.role`, `llm_profile_set`)

Benchmark-Laeufe blockieren bewusst `--promote`, damit Shadow- und Kandidatenlaeufe nicht versehentlich Gold-Artefakte veraendern.

## Vergleich

Nach beiden Laeufen kann ein Vergleich erzeugt werden:

```bash
make support-mvp-benchmark-compare BENCHMARK_NAME=jaws_de_shadow_apr2026 REFERENCE_RUN=jaws_de_shadow_apr2026_codex CANDIDATE_RUN=jaws_de_shadow_apr2026_openrouter
```

Das schreibt eine strukturierte Zusammenfassung nach:

- `data/derived/teacher_reviews/JAWS/DE/benchmarks/<BENCHMARK_NAME>_comparison.json`

Die Vergleichshilfe liest die vorhandenen Pipeline-Reports und Artefakte und fasst insbesondere zusammen:

- verwendetes Profilset, Backend und Modell je Stage
- Anzahl Teacher-Outputs, reviewed Outputs und Judge-Results
- `review_status`-Verteilung der reviewed Outputs
- Approve-/Reject-Verteilung und durchschnittlichen `quality_score` der Judge-Results
- einfache Schema- und `source_records`-Checks fuer die Vergleichsartefakte
- Laufdeltas fuer Jobs, Elapsed Time und Retries pro Stage

## Rollout-Rahmen

Der vorbereitete Rollout-Pfad bleibt bewusst konservativ:

1. Zuerst Shadow-/Kandidatenlauf mit `support_mvp_openrouter_candidate`, kein Default-Wechsel.
2. Danach Vergleich gegen die Codex-Referenz inklusive Report-Review.
3. Erst bei stabilen Ergebnissen einzelne Stage-Profile gezielt anpassen.
4. Eine produktive Default-Umstellung bleibt ein eigener, spaeterer Schritt mit separater Review.

## Bewusst noch offen

Schritt 3 fuehrt noch nicht ein:

- automatische Multi-Run-Benchmark-Orchestrierung
- produktive Modell- oder Routing-Festlegung fuer OpenRouter
- automatische Promotion oder Gold-Freigabe aus Benchmark-Laeufen
- einen Default-Wechsel von Codex CLI auf OpenRouter

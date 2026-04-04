# LLM-Profile

Die Stage-Profile fuer den Support-MVP liegen in `config/llm_stage_profiles.json`.

Aktuell sind zwei Profilsets hinterlegt:

- `support_mvp_default`: spiegelt den bestehenden Codex-CLI-Defaultpfad.
- `support_mvp_openrouter_candidate`: nicht-default OpenRouter-Kandidat fuer kontrollierte Vergleichslaufe.
- `support_mvp_openrouter_gpt54_candidate`: separater OpenRouter-Kandidat auf der GPT-5.4-Linie fuer spaetere Shadow-Benchmarks gegen denselben Codex-Referenzstand.

## Struktur

Ein Profilset enthaelt Stage-Eintraege fuer:

- `user_simulation`
- `answer`
- `judge`

Jeder Stage-Eintrag trennt allgemeine von backend-spezifischen Feldern:

- allgemein: `backend`, `model`, `batch_size`, `max_attempts`, `timeout_sec`, optional `temperature`, `max_output_tokens`
- `codex_cli`: `reasoning_effort`, `sandbox`, `extra_config`
- `openrouter`: `api_base`, `api_key_env`, `extra_headers`, `provider_options`

## Laden und Preflight

Der bestehende MVP-Pfad kann optional mit `--llm-profile-set <name>` auf ein Profilset umgeschaltet werden. Ohne diesen Parameter bleibt der bisherige Codex-Default aktiv.

Vor dem Lauf wird das Profilset validiert:

- unbekannte oder fehlende Stages
- unbekannte Backends
- fehlende Pflichtfelder
- unzulaessige Backend-Kombinationen
- reservierte Request-Keys in `provider_options`
- fehlende API-Key-Umgebungsvariable bei OpenRouter-Profilen

Fuer einen separaten Check gibt es:

```bash
python scripts/preflight_llm_profiles.py --profile-set support_mvp_default
```

Fuer Benchmark- und Rollout-Vorbereitung im Support-MVP siehe zusaetzlich `docs/openrouter_benchmark_rollout.md`.

## Bewusst noch offen

Schritt 2 fuehrt noch keinen produktiven Default-Wechsel auf OpenRouter durch. Ebenso bleiben groessere Rollout-Themen fuer spaeter offen:

- Benchmark-Orchestrierung ueber mehrere Profilsets
- breitere Provider-Unterstuetzung jenseits von Codex CLI und OpenRouter im Support-MVP
- produktive Modell- und Routing-Entscheidung

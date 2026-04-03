# Architektur

## Zielbild

```text
raw manuals
  -> normalization
  -> retrieval chunks
  -> teacher jobs
  -> user simulation
  -> support answers
  -> judge gate
  -> gold promotion
  -> qwen export
  -> student training
  -> eval loop
```

## Leitideen

- RAG fuer Wissen, Training fuer Verhalten
- versionierte Artefakte pro Stufe
- Provenance fuer jede abgeleitete Aussage
- reviewbare Gold-Zone vor Export und Training
- sichere Defaults statt impliziter Altpfade

## JAWS-DE-Entscheidung

Der kanonische produktive JAWS-DE-Ablauf steht in `docs/jaws_de_workflow.md`.
Die maschinenlesbare Baseline-Definition dazu steht in `docs/jaws_de_current_baseline.json`.

Wesentliche Festlegung:

- `data/derived/teacher_jobs/JAWS/DE/` ist die stabile Eingabeschicht.
- `codex_cli_support_validation_v2` ist der aktuell massgebliche committed Downstream-Baseline-Stand.
- `data/exports/qwen_sft/JAWS/DE/current/` ist der aktuelle abgeleitete Trainings-Export.
- `training/transformers/` ist der aktuell unterstuetzte JAWS-DE-Trainingspfad.

## Architekturgrenzen

- `data/raw/` und `data/normalized/` bleiben Source of truth.
- `data/gold/` ist die reviewte Freigabezone.
- `data/exports/` und Training-Outputs sind abgeleitete Verbrauchsartefakte.
- Legacy-, Probe- und Smoke-Pfade duerfen bestehen bleiben, aber nicht wie produktive Defaults wirken.

## LLM-Konfiguration

- Stage-Profile fuer den Support-MVP liegen in `config/llm_stage_profiles.json`.
- Der bestehende Default bleibt Codex CLI; Profilsets schalten nur bei expliziter Auswahl um.
- Der Preflight fuer Profilsets validiert Backend-, Stage- und OpenRouter-Optionen vor dem Lauf.

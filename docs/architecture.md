# Architektur

## Zielarchitektur

```text
raw manuals
  -> normalization
  -> structure extraction
  -> retrieval chunking
  -> task-card generation
  -> teacher data generation
  -> gold review
  -> SFT/LoRA export
  -> student training
  -> eval loop
```

## Leitideen

- **RAG fuer Wissen**, **LoRA fuer Verhalten**
- **Versionierung fuer alle Artefakte**
- **Provenance fuer jede Aussage**
- **Human review als eigener Schritt**
- **Skripte statt manueller Klickstrecken**

## Rollen

- **Teacher**: starkes Modell fuer Transformation, Datengenerierung, optionale Bewertung
- **Student**: kleines lokales Modell, z. B. Qwen3-8B
- **Reviewer**: Mensch oder Grader-Layer
- **Codex CLI**: repo-zentrierte Automations- und Orchestrierungsschicht
- **Training export**: abgeleitete Qwen-SFT-Artefakte unter `data/exports/qwen_sft/`, nie Source of truth

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

- **RAG für Wissen**, **LoRA für Verhalten**
- **Versionierung für alle Artefakte**
- **Provenance für jede Aussage**
- **Human review als eigener Schritt**
- **Skripte statt manueller Klickstrecken**

## Rollen

- **Teacher**: starkes Modell für Transformation, Datengenerierung, optionale Bewertung
- **Student**: kleines lokales Modell, z. B. Qwen3-8B
- **Reviewer**: Mensch oder Grader-Layer
- **Codex CLI**: repo-zentrierte Automations- und Orchestrierungsschicht

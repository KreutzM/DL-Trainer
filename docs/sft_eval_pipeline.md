# JAWS-DE SFT-/Eval-Pipeline

## Zweck

Diese Stufe verbindet den section-aware Chunk-Korpus mit einer ersten reviewbaren Supportdaten-Pipeline für LoRA-Vorläuferdaten.

## Artefakte

- `data/derived/teacher_outputs/JAWS/DE/seed_generation_jobs.jsonl`
  deterministische Teacher-Jobs mit Promptpfad, Behavior-Spec und Chunk-Provenance
- `data/derived/teacher_outputs/JAWS/DE/seed_sft_candidates.jsonl`
  kleines Seed-Set für SFT im Draft-Status
- `data/derived/teacher_outputs/JAWS/DE/seed_eval_cases.jsonl`
  kleines Holdout-/Eval-Set mit disjunkten Chunk-Referenzen

## Pipeline-Idee

1. Chunks liefern belegbare Abschnittseinheiten.
2. Rezeptlogik wählt wenige, klar reviewbare Chunk-Kandidaten für unterschiedliche Falltypen.
3. Promptvorlagen definieren gewünschtes Supportverhalten für Teacher oder Dry-Run.
4. Im Seed-Modus erzeugt das Skript eine kleine templated Baseline ohne externen Teacher.
5. Später kann dieselbe Job-Struktur mit echtem Teacher-Lauf ersetzt oder erweitert werden.

## Review-Fokus

- Ist das Verhalten sauber dokumentationsgebunden?
- Sind Rückfrage- und Eskalationsfälle wirklich als solche nötig?
- Sind Holdout-Chunk-IDs von den Seed-SFT-Fällen getrennt?
- Sind die Fälle eher verhaltensorientiert als wissenskomprimierend?

## Rebuild

```bash
python scripts/build_jaws_support_data.py
python scripts/validate_support_datasets.py --sft data/derived/teacher_outputs/JAWS/DE/seed_sft_candidates.jsonl --eval data/derived/teacher_outputs/JAWS/DE/seed_eval_cases.jsonl
```

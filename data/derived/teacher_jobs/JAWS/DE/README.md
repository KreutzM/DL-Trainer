# JAWS-DE Teacher Jobs

Diese Ablage enthält Runner-Eingaben für den Teacher-Schritt.

- `seed_generation_jobs.jsonl`: deterministische JAWS-DE-Seed-Jobs mit Chunk-Provenance, Runner-Input und Fixture-Payload

Die Jobs sind bewusst getrennt von `data/derived/teacher_outputs/`, damit ein späterer echter Teacher-Lauf dieselben Job-Dateien konsumieren und neue Outputs zurückschreiben kann.

# Training Policy

## Grundsatz

Das Student-Modell soll primär **Verhalten** lernen:
- Ton
- Struktur
- Diagnosemuster
- Rückfrageverhalten
- Eskalationslogik

Produktwissen bleibt in erster Linie im RAG-Korpus.

## Trainingsstufen

1. SFT auf hochwertigen Supportbeispielen
2. optional Preference-/Ranking-Tuning
3. Eval gegen Goldfälle
4. Fehleranalyse und Datenpflege

## Nicht trainieren

- versteckte Denkschritte als Pflichtformat
- ungesicherte Produktfakten
- veraltete oder versionsgemischte Beispiele

## JAWS-DE Baseline

- Seed-SFT und Seed-Evals entstehen zuerst unter `data/derived/teacher_outputs/JAWS/DE/`
- Freigabe in `data/gold/train/` und `data/gold/eval/` bleibt ein eigener Review-Schritt
- LoRA soll Supportverhalten lernen; Faktenbindung bleibt an Chunk- und RAG-Provenance geknüpft

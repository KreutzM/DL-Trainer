# Training Policy

## Grundsatz

Das Student-Modell soll primaer **Verhalten** lernen:

- Ton
- Struktur
- Diagnosemuster
- Rueckfrageverhalten
- Eskalationslogik

Produktwissen bleibt in erster Linie im RAG-Korpus.

## Trainingsstufen

1. SFT auf hochwertigen Supportbeispielen
2. optional Preference-/Ranking-Tuning
3. Eval gegen Gold-Faelle
4. Fehleranalyse und Datenpflege

## Nicht trainieren

- versteckte Denkschritte als Pflichtformat
- ungesicherte Produktfakten
- veraltete oder versionsgemischte Beispiele

## JAWS-DE Baseline

- Seed-Jobs entstehen zuerst unter `data/derived/teacher_jobs/JAWS/DE/`
- Seed-Preview-Faelle und Teacher-Outputs leben unter `data/derived/teacher_outputs/JAWS/DE/`
- Freigabe in `data/gold/train/` und `data/gold/eval/` bleibt ein eigener Review- und Promotion-Schritt
- LoRA soll Supportverhalten lernen; Faktenbindung bleibt an Chunk- und RAG-Provenance geknuepft

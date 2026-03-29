# JAWS-DE Codex CLI Teacher Runs

Diese Ablage enthaelt pro echtem Codex-CLI-Teacher-Batch die Laufartefakte.

Typische Struktur pro Batch:

- `<batch>/request.json`: serialisierter Job-Kontext
- `<batch>/prompt.txt`: Prompt, der an `codex exec` ging
- `<batch>/response_schema.json`: JSON-Schema fuer die sichtbare Endantwort
- `<batch>/last_message.json`: letzte sichtbare JSON-Antwort von Codex
- `<batch>/stdout.txt`
- `<batch>/stderr.txt`

Diese Dateien sind keine Gold-Daten. Sie dienen der Nachvollziehbarkeit eines echten Teacher-Laufs.

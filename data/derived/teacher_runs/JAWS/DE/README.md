# JAWS-DE Codex CLI Teacher Runs

Diese Ablage ist nach dem Clean-Cut bewusst leer zwischen echten Codex-CLI-MVP-Batches.

Typische Struktur pro Batch:

- `user_simulations/<job>/...`
- `answers/<job>/...`
- `judge/<job>/...`

Pro Job-Unterordner:

- `request.json`: serialisierter Job- oder Review-Kontext
- `prompt.txt`: Prompt, der an `codex exec` ging
- `response_schema.json`: JSON-Schema fuer die sichtbare Endantwort
- `last_message.json`: letzte sichtbare JSON-Antwort von Codex
- `stdout.txt`
- `stderr.txt`

Diese Dateien sind keine Gold-Daten. Sie dienen nur der Nachvollziehbarkeit echter Teacher-Laeufe.

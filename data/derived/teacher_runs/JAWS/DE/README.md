# JAWS-DE Codex CLI Teacher Runs

Diese Ablage enthaelt nur noch Laufartefakte echter Codex-CLI-Teacher-Batches.

Aktiv erhalten:

- `codex_cli_smoke_v1/`: kleiner belastbarer Proof-Lauf fuer den neuen produktiven JAWS-DE-Teacher-Pfad

Typische Struktur pro Batch:

- `<batch>/request.json`: serialisierter Job-Kontext
- `<batch>/prompt.txt`: Prompt, der an `codex exec` ging
- `<batch>/response_schema.json`: JSON-Schema fuer die sichtbare Endantwort
- `<batch>/last_message.json`: letzte sichtbare JSON-Antwort von Codex
- `<batch>/stdout.txt`
- `<batch>/stderr.txt`

Diese Dateien sind keine Gold-Daten. Sie dienen der Nachvollziehbarkeit echter Teacher-Laeufe.

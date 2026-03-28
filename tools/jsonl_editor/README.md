# JSONL Editor UI

Dieser Ordner enthaelt die statische Browser-Oberflaeche fuer den lokalen JSONL-Editor.

## Start

Der Editor wird ueber den Python-Server aus dem Repo gestartet:

```bash
python scripts/editor_server.py --open-browser
```

Alternativ direkt aus diesem Ordner:

```bash
./start.sh
```

```bat
start.bat
```

Standard-URL:

```text
http://127.0.0.1:8765/
```

## Dateien in diesem Ordner

- `index.html` - Layout der Oberflaeche
- `app.js` - UI-Logik, Filter, Formulare und Save-Aktionen
- `styles.css` - Styling fuer die Editor-Oberflaeche

## Ziel

Die UI ist fuer diese JSONL-Artefakte gedacht:

- reviewbare Teacher-Outputs unter `data/derived/teacher_outputs/`
- Gold-Train-Dateien unter `data/gold/train/`
- Gold-Eval-Dateien unter `data/gold/eval/`

Nicht als Editierziel gedacht sind Exporte, Raw-Responses und rein automatisch erzeugte Ableitungen.

## Review-Workflow

Fuer `teacher_outputs` zeigt die UI einen eigenen Review-Modus:

- vorgeschlagener Zielpfad fuer eine `reviewed`-Datei
- Laden eines vorhandenen `reviewed`-Stands zur Fortsetzung
- Merge-Bericht fuer Konflikte sowie fehlende oder zusaetzliche IDs
- Pending-/Decided-Uebersicht
- `Approve + Next` und `Reject + Next`
- Export nach `*_reviewed_*.jsonl`
- Diff-Ansicht zwischen Roh-Output und aktuellem Review-Stand

Damit bleibt der Roh-Teacher-Output unveraendert, waehrend der reviewte Stand separat geschrieben wird.

## Gold-Promotion

Fuer `reviewed_teacher_outputs` zeigt die UI zusaetzlich einen Promotion-Bereich:

- vorgeschlagene Gold-Zielpfade fuer Train und Eval
- Count-Vorschau fuer `human_reviewed`-Faelle
- Schreiben der Gold-Dateien direkt nach `data/gold/train/` und `data/gold/eval/`
- automatische Schema- und Provenance-Checks nach dem Schreiben

Die Promotion folgt denselben Regeln wie `scripts/promote_teacher_outputs.py`.

## Hinweise

- Die UI selbst schreibt keine Dateien direkt auf Platte; das uebernimmt `scripts/editor_server.py`.
- Fuer Gold-Dateien gibt es einen expliziten Save-Guard.
- Validierung laeuft serverseitig ueber die vorhandenen Schemas und minimale Provenance-Pruefungen.
- Beide Startskripte reichen zusaetzliche Argumente an `scripts/editor_server.py` weiter, z. B. `--port 9000`.

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

## Hinweise

- Die UI selbst schreibt keine Dateien direkt auf Platte; das uebernimmt `scripts/editor_server.py`.
- Fuer Gold-Dateien gibt es einen expliziten Save-Guard.
- Validierung laeuft serverseitig ueber die vorhandenen Schemas und minimale Provenance-Pruefungen.
- Beide Startskripte reichen zusaetzliche Argumente an `scripts/editor_server.py` weiter, z. B. `--port 9000`.

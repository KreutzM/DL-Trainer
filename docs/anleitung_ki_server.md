# Anleitung KI-Server

## Ziel der Anleitung
Diese Anleitung beschreibt, wie du deinen Account auf dem KI-Server sinnvoll und sauber nutzt, insbesondere für Slurm, Container, SSH/VPN und TextGenerationWebUI.

---

# Plan: Was du wissen musst

## 1. Zugang und Grundprinzip verstehen
- Wie du dich per VPN und SSH verbindest
- Warum SSH-Key-Login nötig ist
- Was der Login-Node ist und was Compute-Nodes sind
- Warum du GPU-Jobs nie direkt auf dem Login-Node startest

## 2. Slurm als Arbeitsweise verstehen
- Unterschied zwischen `srun`, `sbatch`, `squeue`, `scancel`
- Wie du interaktive Jobs startest
- Wie du Joblaufzeit, GPU-Zahl, RAM und CPU festlegst
- Wie du prüfst, wie lange dein Job noch läuft

## 3. Container-Setup des Clusters verstehen
- Der Cluster nutzt Slurm + Pyxis + Enroot
- Der Container liefert die Laufzeitumgebung
- Dein Homeverzeichnis enthält Code, Modelle, Daten und venvs
- Warum Installationen im Container ohne venv oft nicht dauerhaft sind

## 4. Dateisystem und Modelle verstehen
- Modelle werden nicht von Slurm zwischen Nodes kopiert
- Große Modelle müssen in einem gemeinsamen Speicherbereich liegen
- Für dich ist ein zentraler Modellordner sinnvoll, z. B. `~/models`
- TGWUI kann Modelle je nach Setup auch unter `user_data/models` speichern

## 5. TextGenerationWebUI sauber betreiben
- Interaktiven Slurm-Job starten
- NGC-Container nutzen
- Python-Umgebung im Home persistent halten
- WebUI nur lokal auf dem Compute-Node starten
- Per SSH-Tunnel im Browser öffnen
- Ein zentrales Modellverzeichnis verwenden

## 6. Mehrere GPUs und große GGUF-Modelle verstehen
- Mehrere GPUs nur nutzen, wenn das Modell davon profitiert
- Bei GGUF mit `llama.cpp` geschieht Multi-GPU über Tensor-Split
- Große 70B-Modelle brauchen oft 2 GPUs und viel RAM
- Q5 kann deutlich langsamer sein als Q4

## 7. Monitoring und Fehlersuche können
- `nvidia-smi`, `nvidia-smi dmon`, `top`, `squeue`, `scontrol`
- Woran du erkennst, ob CPU, GPU oder Kontextgröße limitiert
- Wie du Joblaufzeit und Restzeit prüfst

## 8. Gute Cluster-Praxis
- Jobs sauber beenden
- Ressourcen nicht unnötig blockieren
- Meist nur 1 GPU verwenden, außer es gibt einen guten Grund
- Modelle und Umgebungen ordentlich strukturieren

---

# Vollständige Anleitung

## 1. Zugang zum Cluster

### 1.1 VPN
Um den KI-Server von außerhalb zu erreichen, musst du dich in der Regel per Hochschul-VPN verbinden.

Wichtig:
- Der Cisco Secure Client kann je nach Hochschulkonfiguration den gesamten Internetverkehr durch das VPN leiten.
- Im Client kannst du die Option aktivieren:
  - **„Lokalen (LAN)-Zugriff bei Verwendung von VPN zulassen (falls konfiguriert)”**
- Ob Split-Tunneling wirklich funktioniert, hängt von der Serverkonfiguration der Hochschule ab.

### 1.2 SSH-Login
Der Server verwendet SSH-Key-Login.

Login-Beispiel:

```bash
ssh hg11312@cvl-slurm-login.mni.thm.de
```

Wenn du beim ersten Mal gefragt wirst, ob du dem Host-Key vertraust, ist das normal.

Wenn stattdessen `Permission denied (publickey)` erscheint, dann stimmt entweder
- der Username nicht,
- der SSH-Key wird nicht angeboten,
- oder dein Public Key ist auf dem Cluster noch nicht hinterlegt.

### 1.3 Login-Node vs. Compute-Node
Nach dem Login landest du auf dem Login-Node, z. B. `cvl-slurm-login`.

Dort darfst du typischerweise:
- Dateien verwalten
- Git-Repositories klonen
- Jobs einreichen
- Logs lesen

Dort solltest du typischerweise **nicht**:
- GPU-Programme starten
- Trainings oder Inferenz direkt laufen lassen

Die eigentliche Rechenarbeit findet auf Compute-Nodes statt, z. B. `iti-dl-1.mni.thm.de`.

---

## 2. Grundprinzip: Arbeiten mit Slurm

Auf diesem Cluster gilt:

> Du startest rechenintensive Arbeit nicht direkt, sondern immer über Slurm.

### 2.1 Wichtige Befehle
- `srun` – interaktive Jobs starten
- `sbatch` – Batch-Jobs mit Skript starten
- `squeue` – laufende und wartende Jobs anzeigen
- `scancel` – Jobs abbrechen
- `scontrol` – Details zu Jobs anzeigen
- `sinfo` – Clusterstatus
- `sacct` – Informationen zu beendeten Jobs

### 2.2 Interaktiver GPU-Job
Beispiel für einen interaktiven Job mit 1 GPU:

```bash
srun \
  --gpus=1 \
  --cpus-per-task=8 \
  --mem=24G \
  --time=02:00:00 \
  --job-name=hg-textgen \
  --container-image='nvcr.io#nvidia/pytorch:23.10-py3' \
  --no-container-remap-root \
  --pty bash
```

Danach befindest du dich auf einem Compute-Node.

Prüfen:

```bash
hostname -f
nvidia-smi
```

### 2.3 Zwei GPUs anfordern
Beispiel:

```bash
srun \
  --gpus=2 \
  --cpus-per-task=16 \
  --mem=120G \
  --time=03:00:00 \
  --job-name=hg-70b-q5 \
  --container-image='nvcr.io#nvidia/pytorch:23.10-py3' \
  --no-container-remap-root \
  --pty bash
```

Hinweis:
Auf diesem Cluster sollst du mehrere GPUs nur nutzen, wenn es dafür einen guten Grund gibt. Für viele Workloads bringt eine zweite GPU wenig.

---

## 3. Jobstatus und Restlaufzeit prüfen

### 3.1 Alle eigenen Jobs anzeigen

```bash
squeue -u hg11312
```

### 3.2 Restlaufzeit anzeigen

```bash
squeue -u hg11312 -o "%.18i %.9P %.20j %.8T %.10M %.10L %.6D %R"
```

Wichtige Spalten:
- `M` = bisherige Laufzeit
- `L` = Restlaufzeit

### 3.3 Details zu einem Job

```bash
scontrol show job <JOBID>
```

Interaktive Jobs solltest du normalerweise nicht verlängern. Wenn der Job endet, bleibt dein Homeverzeichnis erhalten. Nur der laufende Prozess endet.

---

## 4. Container-Konzept des Clusters

Der Cluster verwendet:
- Slurm
- Pyxis
- Enroot

Das bedeutet:
- Du startest Programme in Containern
- Der Container bringt Python, CUDA und Frameworks mit
- Dein Homeverzeichnis bleibt außerhalb des Containers erhalten

### 4.1 Was im Home liegt
Im Homeverzeichnis solltest du dauerhaft speichern:
- Code
- Modelle
- Daten
- Python-Umgebungen
- Skripte

Empfohlene Struktur:

```text
~/text-generation-webui/
~/models/
~/venvs/
~/bin/
~/logs/
```

### 4.2 Was nicht dauerhaft ist
Wenn du ohne venv einfach `pip install ...` im Container auf Systemebene ausführst, kann das beim nächsten Job wieder verschwunden sein.

Deshalb ist ein persistentes venv im Home sinnvoll.

---

## 5. Python-Umgebung im Home

Auf dem Cluster fehlte im Container `python3-venv`. Deshalb funktioniert `python -m venv` nicht immer direkt.

Eine funktionierende Alternative ist `virtualenv` im User-Kontext.

### 5.1 virtualenv installieren

```bash
python3 -m pip install --user virtualenv
export PATH="$HOME/.local/bin:$PATH"
```

### 5.2 venv anlegen

```bash
virtualenv -p python3 ~/venvs/textgen
source ~/venvs/textgen/bin/activate
```

### 5.3 Vorteile
- bleibt im Home erhalten
- kann in späteren Jobs wiederverwendet werden
- vermeidet kaputte Paketkombinationen aus dem Container-Systempython

---

## 6. TextGenerationWebUI einrichten

### 6.1 Repository klonen
Auf dem Login-Node oder im Job:

```bash
cd ~
git clone https://github.com/oobabooga/text-generation-webui.git
```

### 6.2 Requirements installieren

```bash
cd ~/text-generation-webui
source ~/venvs/textgen/bin/activate
pip install -U pip setuptools wheel
pip install -r requirements/full/requirements.txt
```

### 6.3 WebUI starten

```bash
python server.py --listen --listen-host 127.0.0.1 --listen-port 7861
```

Wichtig:
- `--listen-host 127.0.0.1` hält den Dienst lokal auf dem Compute-Node
- Port größer als 8000 verwenden

Optional mit Passwort:

```bash
python server.py --listen --listen-host 127.0.0.1 --listen-port 7861 --gradio-auth hg11312:DEINPASSWORT
```

---

## 7. TGWUI im Browser öffnen

Da TGWUI nur lokal auf dem Compute-Node läuft, brauchst du einen SSH-Tunnel.

Beispiel:

```bash
ssh -N -L 7861:localhost:7861 -J hg11312@cvl-slurm-login.mni.thm.de hg11312@iti-dl-1.mni.thm.de
```

Dann im Browser:

```text
http://localhost:7861
```

Wenn du stattdessen versuchst, über den Login-Node direkt auf `iti-dl-1:7861` zu tunneln, bekommst du oft `Connection refused`, weil TGWUI nur auf `127.0.0.1` lauscht.

---

## 8. Modellverwaltung

### 8.1 Grundprinzip
Slurm kopiert keine Modelle zwischen Nodes.
Große Modelle müssen deshalb in einem gemeinsamen Speicherbereich liegen, den alle Nodes sehen.

### 8.2 Zentrales Modellverzeichnis
Empfohlen:

```bash
mkdir -p ~/models
```

### 8.3 TGWUI und Modellpfade
Bei deinem Setup hat TGWUI ein heruntergeladenes Modell unter folgendem Pfad gespeichert:

```text
~/text-generation-webui/user_data/models/
```

Das ist wichtig, weil TGWUI Downloads nicht immer in `~/text-generation-webui/models/` ablegt.

### 8.4 Empfohlene Vereinheitlichung
Entweder:
- TGWUI immer mit `--model-dir ~/models` starten

oder
- `user_data/models` auf `~/models` umbiegen

Empfohlener Start:

```bash
python server.py \
  --listen --listen-host 127.0.0.1 --listen-port 7861 \
  --model-dir ~/models
```

Dann landen alle Modelle in `~/models`.

---

## 9. Hugging Face Modellpfade verstehen

In TGWUI gibst du normalerweise **kein einzelnes Modell ohne Kontext** an, sondern:
- den Hugging-Face-Repo-Namen
- optional den konkreten Dateinamen

Schema:

```text
<HF-User>/<HF-Repo>
```

Optional zusätzlich der Dateiname, z. B. bei GGUF:

```text
gpt-oss-20b-Q5_K_M.gguf
```

Das ist wichtig, weil TGWUI eine Datei aus einem Repository lädt, nicht einfach irgendeinen Dateinamen.

---

## 10. GGUF und Multi-GPU mit llama.cpp

### 10.1 Passender Loader
Für GGUF-Dateien musst du in TGWUI `llama.cpp` verwenden.

### 10.2 Zwei GPUs nutzen
Beispielstart für große GGUF-Modelle:

```bash
python server.py \
  --listen --listen-host 127.0.0.1 --listen-port 7861 \
  --loader llama.cpp \
  --model-dir ~/models \
  --tensor-split 12,12 \
  --ctx-size 1024 \
  --threads 32 --threads-batch 32 \
  --gpu-layers 60
```

### 10.3 Bedeutung wichtiger Parameter
- `--loader llama.cpp` – GGUF-Loader
- `--tensor-split 12,12` – verteilt die Last auf 2 gleiche GPUs
- `--ctx-size` – Kontextgröße; großer Hebel auf Geschwindigkeit und Speicherbedarf
- `--threads` – CPU-Threads für llama.cpp
- `--threads-batch` – Batch-Threadzahl
- `--gpu-layers` – Anzahl der auf GPU ausgelagerten Layer

### 10.4 Wichtige Praxiserfahrung
Bei 70B-Modellen mit Q5 auf 2×4090 gilt oft:
- das Modell passt gerade so
- GPUs sind speicherseitig voll
- die Ausführung ist oft langsamer als erwartet
- Q4 kann in der Praxis deutlich schneller sein als Q5

---

## 11. Bottlenecks erkennen

### 11.1 GPU prüfen

```bash
nvidia-smi
```

### 11.2 GPU-Power und Utilisation prüfen

```bash
nvidia-smi dmon -s pucm -d 1
```

Wenn Power und SM-Utilisation niedrig bleiben, obwohl VRAM voll ist, dann ist oft nicht die GPU der Flaschenhals, sondern CPU, Batchgröße, Kontext oder die Serialität der Generierung.

### 11.3 CPU prüfen

```bash
top -H -p $(pgrep -n -f "server.py|text-generation-webui|llama")
```

Wenn viele Kerne idle bleiben, obwohl Threads vorhanden sind, dann skaliert die Inferenz über CPU und Pipeline nicht effizient.

### 11.4 Grundregel
- Laden des Modells ist I/O-lastig
- Textgenerierung ist oft CPU-/Pipeline-/KV-Cache-limitiert
- Voller VRAM bedeutet nicht automatisch hohe GPU-Auslastung

---

## 12. Zweite Shell im laufenden Job

### 12.1 Problem
Wenn `tmux` oder `screen` nicht installiert sind, hast du zunächst nur eine Shell.

### 12.2 Einfache Lösung
Öffne auf deinem lokalen Rechner eine zweite SSH-Verbindung direkt auf den Compute-Node:

```bash
ssh -J hg11312@cvl-slurm-login.mni.thm.de hg11312@iti-dl-1.mni.thm.de
```

Das ist **kein neuer Slurm-Job**, sondern nur eine weitere Shell auf demselben Node.

Dort kannst du dann z. B. laufen lassen:

```bash
watch -n 1 nvidia-smi
```

---

## 13. Sauberes Arbeiten auf dem Cluster

### 13.1 Gute Praxis
- Rechenjobs immer über Slurm starten
- Modelle und venvs im Home persistent ablegen
- WebUIs nur lokal auf dem Compute-Node binden
- per SSH-Tunnel im Browser arbeiten
- große Modelle zentral an einem Ort halten

### 13.2 Was du vermeiden solltest
- GPU-Programme direkt auf dem Login-Node starten
- blind mehrere GPUs nutzen, obwohl es nichts bringt
- große Modelle doppelt an verschiedenen Orten ablegen
- Jobs unnötig lange offen halten
- Entwicklungsumgebungen mit Remote Sessions verwenden, wenn die Admins davon abraten

### 13.3 Jobs sauber beenden
Wenn du fertig bist:
- TGWUI mit `Ctrl+C` stoppen
- Shell mit `exit` verlassen
- SSH-Tunnel lokal beenden

Dann werden GPU-Ressourcen sofort freigegeben.

---

## 14. Empfohlener Standard-Workflow für TGWUI

### 14.1 Login

```bash
ssh hg11312@cvl-slurm-login.mni.thm.de
```

### 14.2 Interaktiven Job starten

```bash
srun \
  --gpus=1 \
  --cpus-per-task=8 \
  --mem=24G \
  --time=02:00:00 \
  --job-name=hg-textgen \
  --container-image='nvcr.io#nvidia/pytorch:23.10-py3' \
  --no-container-remap-root \
  --pty bash
```

### 14.3 venv aktivieren

```bash
source ~/venvs/textgen/bin/activate
```

### 14.4 TGWUI starten

```bash
cd ~/text-generation-webui
python server.py \
  --listen --listen-host 127.0.0.1 --listen-port 7861 \
  --model-dir ~/models
```

### 14.5 Tunnel lokal öffnen

```bash
ssh -N -L 7861:localhost:7861 -J hg11312@cvl-slurm-login.mni.thm.de hg11312@iti-dl-1.mni.thm.de
```

### 14.6 Browser

```text
http://localhost:7861
```

---

## 15. Kurzreferenz

### Login

```bash
ssh hg11312@cvl-slurm-login.mni.thm.de
```

### Interaktiver Job

```bash
srun --gpus=1 --cpus-per-task=8 --mem=24G --time=02:00:00 --container-image='nvcr.io#nvidia/pytorch:23.10-py3' --no-container-remap-root --pty bash
```

### Jobstatus

```bash
squeue -u hg11312
```

### Restlaufzeit

```bash
squeue -u hg11312 -o "%.18i %.9P %.20j %.8T %.10M %.10L %.6D %R"
```

### GPU-Status

```bash
nvidia-smi
```

### GPU-Monitoring

```bash
nvidia-smi dmon -s pucm -d 1
```

### Zweite Shell auf Compute-Node

```bash
ssh -J hg11312@cvl-slurm-login.mni.thm.de hg11312@iti-dl-1.mni.thm.de
```

### TGWUI 4 mit GGUF und 1 GPUs
cd ~/text-generation-webui-4.1.1
source ~/venvs/textgen-qwen/bin/activate

python server.py \
  --loader Transformers \
  --model-dir ~/models \
  --model Qwen3-8B \
  --listen --listen-host 127.0.0.1 --listen-port 7861 \
  --bf16

### TGWUI mit GGUF und 2 GPUs

```bash
python server.py \
  --listen --listen-host 127.0.0.1 --listen-port 7861 \
  --loader llama.cpp \
  --model-dir ~/models \
  --tensor-split 12,12 \
  --ctx-size 1024 \
  --threads 32 --threads-batch 32 \
  --gpu-layers 60
```

---

## 16. Abschluss

Wenn du den KI-Server regelmäßig nutzt, brauchst du im Alltag vor allem vier Dinge sicher zu beherrschen:
- SSH + VPN
- Slurm-Grundbefehle
- Container + persistentes Home/venv
- TGWUI mit sauberem Modellpfad und SSH-Tunnel

Wenn diese vier Bausteine sauber sitzen, ist der Rest vor allem Feintuning von Modellen, GPUs und Performance.


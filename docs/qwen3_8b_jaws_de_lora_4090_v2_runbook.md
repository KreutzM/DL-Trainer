# Qwen3-8B LoRA 4090 v2 Runbook

## Zweck

Dieses Runbook beschreibt den naechsten echten serverseitigen Qwen3-8B-LoRA-v2-Lauf auf einem Linux-Cloud-Server mit RTX 4090. Der Trainingspfad bleibt beim vorhandenen `training/transformers`-Stack.

## Fixe Eingaben

- Branch: `feat/prepare-4090-server-run`
- Trainingsconfig: `training/transformers/qwen3_8b_jaws_de_lora_4090_v2.yaml`
- Finaler Datensatz-Freeze: `data/exports/qwen_sft/JAWS/DE/qwen3_8b_jaws_de_lora_4090_v2_20260328`
- Startskript: `scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh`
- Preflight: `scripts/preflight_qwen_lora_server.py`
- Smoke-Test: `scripts/run_qwen3_8b_jaws_de_lora_4090_v2_smoke.sh`

## Output-Konvention

- Trainingsartefakte: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/`
- Checkpoints: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/checkpoint-*`
- Finaler Adapter: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/final_adapter/`
- Run-Summary: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/run_summary.json`
- Logs: `training/transformers/logs/qwen3_8b_jaws_de_lora_4090_v2/`
- Post-Run-Smoke-Reports: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/post_run/`

## 1. Repo auschecken

```bash
git clone <repo-url>
cd DL-Trainer
git checkout feat/prepare-4090-server-run
```

## 2. Python-Umgebung aufsetzen

Empfohlen ist Python `3.11.x`. Die Config verlangt Linux, CUDA und mindestens einen 4090-kompatiblen GPU-Slot mit mindestens 20 GB VRAM.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

## 3. PyTorch mit CUDA installieren

Installiere eine CUDA-faehige Linux-PyTorch-Version passend zum Server-Treiber ueber den offiziellen PyTorch-Selector:

- https://pytorch.org/get-started/locally/

Danach die Repo-Abhaengigkeiten fuer den Run installieren:

```bash
pip install -r training/transformers/requirements-qwen-server-4090-v2.txt
```

## 4. Optional: Hugging Face Zugriff vorbereiten

Falls `Qwen/Qwen3-8B` auf dem Server noch nicht gecacht ist und der Zugriff Authentifizierung erfordert:

```bash
huggingface-cli login
```

Keine Tokens in Repo-Dateien ablegen.

## 5. Preflight ausfuehren

```bash
python scripts/preflight_qwen_lora_server.py \
  --config training/transformers/qwen3_8b_jaws_de_lora_4090_v2.yaml
```

Der Preflight bricht bei folgenden Fehlern hart ab:

- falsches Betriebssystem
- unpassende Python-Version
- fehlende Python-Pakete
- keine CUDA-GPU oder kein passender 4090-Host
- fehlende oder inkonsistente Export-Dateien
- kein Schreibzugriff auf Output-/Log-Verzeichnisse
- belegter Output-Pfad ohne expliziten Resume-Modus

## 6. Training starten

Fresh run:

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh
```

Der Startpfad fuehrt automatisch den Preflight aus, schreibt einen Preflight-JSON-Report, legt ein timestamptes Training-Log an und startet dann `scripts/run_qwen_lora_training.py` mit der v2-Config.

## 7. Training ueberwachen

```bash
tail -f training/transformers/logs/qwen3_8b_jaws_de_lora_4090_v2/train_*.log
```

Nutzt `tensorboard`, wenn gewuenscht:

```bash
tensorboard --logdir training/transformers/logs/qwen3_8b_jaws_de_lora_4090_v2
```

## 8. Resume / Recovery

Checkpoint-Konvention:

- Der Trainer schreibt `checkpoint-*` direkt unter `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/`.
- Fuer ein automatisches Resume auf den neuesten Checkpoint:

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh --resume-latest
```

- Fuer ein gezieltes Resume:

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh \
  --resume-from training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/checkpoint-75
```

Der Resume-Modus erlaubt vorhandene Output-Dateien und reicht den Checkpoint an den Trainer weiter.

## 9. Post-Run Smoke-Test

Nach erfolgreichem Training den finalen Adapter laden und mehrere Falltypen aus dem Gold-Eval pruefen:

```bash
bash scripts/run_qwen3_8b_jaws_de_lora_4090_v2_smoke.sh
```

Das Script:

- laedt standardmaessig `final_adapter`
- zieht je einen Fall aus `faq_direct_answer`, `troubleshooting`, `step_by_step`, `clarification` und `uncertainty_escalation`
- schreibt den Report nach `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/post_run/`

## 10. Mindestpruefung nach dem Lauf

Pruefe mindestens:

- `run_summary.json` vorhanden und plausibel
- `final_adapter/` vorhanden
- letzter Checkpoint und `trainer_state.json` vorhanden
- Smoke-Test-JSON vorhanden
- Smoke-Test zeigt fuer alle Falltypen generierte Antworten statt leerer Outputs

## 11. Was bewusst nicht im Repo liegt

- keine Modellgewichte
- keine Server-spezifischen Secrets
- keine echten Cloud-Pfade
- keine laufzeitspezifischen Outputs oder Logs

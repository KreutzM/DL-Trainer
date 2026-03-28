# Qwen3-8B LoRA 4090 v2 Cluster Runbook

## Zweck

Dieses Runbook beschreibt den auf dem THM-Cluster erfolgreich getesteten Pfad fuer den Qwen3-8B-LoRA-v2-Lauf. Es ist fuer Slurm-/Compute-Node-Workflows gedacht und ergaenzt das generische `docs/qwen3_8b_jaws_de_lora_4090_v2_runbook.md`.

## Getesteter Stand

- Branch: `main`
- Config: `training/transformers/qwen3_8b_jaws_de_lora_4090_v2.yaml`
- Datensatz-Freeze: `data/exports/qwen_sft/JAWS/DE/qwen3_8b_jaws_de_lora_4090_v2_20260328`
- Ziel-GPU: `NVIDIA GeForce RTX 4090`
- Getestete Python-Version: `3.10.12`
- Getesteter PyTorch-Build: `torch 2.8.0+cu128`

## 1. Interaktiven GPU-Job starten

```bash
srun \
  --gpus=1 \
  --cpus-per-task=8 \
  --mem=48G \
  --time=08:00:00 \
  --job-name=qwen4090 \
  --container-image='nvcr.io#nvidia/pytorch:23.10-py3' \
  --no-container-remap-root \
  --pty bash
```

Pruefen:

```bash
hostname -f
nvidia-smi
```

## 2. Repo und Environment vorbereiten

```bash
cd ~/src/DL-Trainer
bash scripts/bootstrap_qwen_server_4090_env.sh
source ~/venvs/dl-trainer-qwen/bin/activate
```

Das Bootstrap-Skript:

- nutzt `python3` oder `python` automatisch
- faellt bei fehlendem `python -m venv` auf `virtualenv` zurueck
- installiert den getesteten CUDA-12.8-PyTorch-Build
- installiert danach die Repo-Abhaengigkeiten

## 3. Preflight

```bash
python scripts/preflight_qwen_lora_server.py \
  --config training/transformers/qwen3_8b_jaws_de_lora_4090_v2.yaml
```

Erwartung: JSON mit `"status": "ok"`.

## 4. Training starten

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh
```

Die Skripte fallen automatisch auf `python3` zurueck, falls `python` im Container fehlt.

## 5. Training ueberwachen

```bash
tail -f training/transformers/logs/qwen3_8b_jaws_de_lora_4090_v2/train_*.log
```

Optional in zweiter Shell:

```bash
nvidia-smi
```

## 6. Resume

Automatisch vom neuesten Checkpoint:

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh --resume-latest
```

Gezielt:

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh \
  --resume-from training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/checkpoint-125
```

## 7. Post-Run Smoke-Test

```bash
bash scripts/run_qwen3_8b_jaws_de_lora_4090_v2_smoke.sh
```

Der Report landet unter:

```text
training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v2/post_run/
```

## 8. Typische Fehler

### `python: command not found`

Der Container hat nur `python3`. Die Repo-Skripte fallen jetzt automatisch auf `python3` zurueck. Falls noetig:

```bash
PYTHON_BIN=python3 bash scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh
```

### `python3 -m venv` scheitert

Dann fehlt `python3-venv` im Container. Das Bootstrap-Skript nutzt in diesem Fall `virtualenv`.

### `CUDA is not available in the active PyTorch installation`

Dann passt der installierte Torch-Build nicht zum Treiber. Fuer diesen Cluster wurde erfolgreich getestet:

```bash
python -m pip install --index-url https://download.pytorch.org/whl/cu128 \
  torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0
```

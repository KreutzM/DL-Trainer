# Qwen3-8B LoRA 4090 v4 Cluster Runbook

## Zweck

Dieses Runbook beschreibt den auf dem THM-Cluster vorgesehenen Pfad fuer den naechsten Qwen3-8B-LoRA-Lauf auf Basis des bereinigten Gold-v3-Cleanup-Kandidatenstands.

## Getesteter Stand

- Branch: `main` nach Merge von `feat/qwen-data-expansion-v1`
- Config: `training/transformers/qwen3_8b_jaws_de_lora_4090_v4.yaml`
- Datensatz-Freeze: `data/exports/qwen_sft/JAWS/DE/qwen3_8b_jaws_de_lora_4090_v4_20260328`
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
  --job-name=qwen4090v4 \
  --container-image='nvcr.io#nvidia/pytorch:23.10-py3' \
  --no-container-remap-root \
  --pty bash
```

## 2. Repo und Environment vorbereiten

```bash
cd ~/src/DL-Trainer
bash scripts/bootstrap_qwen_server_4090_env.sh
source ~/venvs/dl-trainer-qwen/bin/activate
```

## 3. Preflight

```bash
python scripts/preflight_qwen_lora_server.py \
  --config training/transformers/qwen3_8b_jaws_de_lora_4090_v4.yaml
```

Erwartung: JSON mit `"status": "ok"`.

## 4. Training starten

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v4.sh
```

## 5. Training ueberwachen

```bash
tail -f training/transformers/logs/qwen3_8b_jaws_de_lora_4090_v4/train_*.log
```

## 6. Resume

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v4.sh --resume-latest
```

Oder gezielt:

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v4.sh \
  --resume-from training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v4/checkpoint-125
```

## 7. Post-Run Smoke-Test

```bash
bash scripts/run_qwen3_8b_jaws_de_lora_4090_v4_smoke.sh
```

Der Report landet unter:

```text
training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v4/post_run/
```

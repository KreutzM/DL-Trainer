# Qwen3-8B LoRA 4090 v4 Runbook

## Zweck

Dieses Runbook beschreibt den naechsten echten serverseitigen Qwen3-8B-LoRA-Lauf auf Basis des bereinigten Gold-v3-Cleanup-Kandidatenstands. Der Trainingspfad bleibt beim vorhandenen `training/transformers`-Stack.

## Fixe Eingaben

- Branch: `main` nach Merge von `feat/qwen-data-expansion-v1`
- Trainingsconfig: `training/transformers/qwen3_8b_jaws_de_lora_4090_v4.yaml`
- Finaler Datensatz-Freeze: `data/exports/qwen_sft/JAWS/DE/qwen3_8b_jaws_de_lora_4090_v4_20260328`
- Startskript: `scripts/start_qwen3_8b_jaws_de_lora_4090_v4.sh`
- Preflight: `scripts/preflight_qwen_lora_server.py`
- Smoke-Test: `scripts/run_qwen3_8b_jaws_de_lora_4090_v4_smoke.sh`
- Optionales Environment-Bootstrap: `scripts/bootstrap_qwen_server_4090_env.sh`

## Output-Konvention

- Trainingsartefakte: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v4/`
- Checkpoints: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v4/checkpoint-*`
- Finaler Adapter: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v4/final_adapter/`
- Run-Summary: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v4/run_summary.json`
- Logs: `training/transformers/logs/qwen3_8b_jaws_de_lora_4090_v4/`
- Post-Run-Smoke-Reports: `training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v4/post_run/`

## 1. Repo auschecken

```bash
git clone <repo-url>
cd DL-Trainer
git checkout main
```

## 2. Python-Umgebung aufsetzen

Empfohlen ist Python `3.10+`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Falls `python -m venv` auf dem Zielserver nicht verfuegbar ist:

```bash
bash scripts/bootstrap_qwen_server_4090_env.sh
source ~/venvs/dl-trainer-qwen/bin/activate
```

## 3. PyTorch mit CUDA installieren

Installiere eine CUDA-faehige Linux-PyTorch-Version passend zum Server-Treiber. Getesteter Cluster-Pfad:

```bash
python -m pip install --index-url https://download.pytorch.org/whl/cu128 \
  torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0
pip install -r training/transformers/requirements-qwen-server-4090-v2.txt
```

## 4. Optional: Hugging Face Zugriff vorbereiten

```bash
huggingface-cli login
```

## 5. Preflight ausfuehren

```bash
python scripts/preflight_qwen_lora_server.py \
  --config training/transformers/qwen3_8b_jaws_de_lora_4090_v4.yaml
```

## 6. Training starten

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v4.sh
```

## 7. Training ueberwachen

```bash
tail -f training/transformers/logs/qwen3_8b_jaws_de_lora_4090_v4/train_*.log
```

## 8. Resume / Recovery

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v4.sh --resume-latest
```

Oder gezielt:

```bash
bash scripts/start_qwen3_8b_jaws_de_lora_4090_v4.sh \
  --resume-from training/transformers/outputs/qwen3_8b_jaws_de_lora_4090_v4/checkpoint-75
```

## 9. Post-Run Smoke-Test

```bash
bash scripts/run_qwen3_8b_jaws_de_lora_4090_v4_smoke.sh
```

## 10. Mindestpruefung nach dem Lauf

- `run_summary.json` vorhanden und plausibel
- `final_adapter/` vorhanden
- Smoke-Test-JSON vorhanden
- Vergleich mit dem frueheren `v2`-Baseline-Lauf nicht nur nach Loss, sondern vor allem auf den Smoke-Faellen

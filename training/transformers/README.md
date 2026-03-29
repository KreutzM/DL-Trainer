# transformers

Dieser Ordner enthaelt den aktiven Qwen3-8B-PEFT/QLoRA-Pfad fuer JAWS-DE. Der bisherige erfolgreiche Baseline-Lauf war `v2`; der naechste vorbereitete Run-Pfad ist `v3` auf Basis des erweiterten Gold-v2-Datensatzes.

## Dateien

- `qwen3_8b_jaws_de_lora_4090_v2.yaml` ist die fruehere serverseitige v2-Konfiguration des erfolgreichen Baseline-Laufs.
- `qwen3_8b_jaws_de_lora_4090_v3.yaml` ist die vorbereitete Konfiguration fuer den naechsten echten Linux-/RTX4090-Lauf.
- `requirements-qwen-server-4090-v2.txt` pinnt die Python-Abhaengigkeiten fuer den vorbereiteten Server-Run.

## Ablauf

- Finaler Datensatz-Freeze fuer den naechsten Lauf: `data/exports/qwen_sft/JAWS/DE/qwen3_8b_jaws_de_lora_4090_v3_20260328`
- Startskript: `scripts/start_qwen3_8b_jaws_de_lora_4090_v3.sh`
- Environment-Bootstrap: `scripts/bootstrap_qwen_server_4090_env.sh`
- Preflight: `scripts/preflight_qwen_lora_server.py`
- Trainingsrunner: `scripts/run_qwen_lora_training.py`
- Smoke-Test: `scripts/run_qwen3_8b_jaws_de_lora_4090_v3_smoke.sh`
- Runbook: `docs/qwen3_8b_jaws_de_lora_4090_v3_runbook.md`
- Cluster-Runbook: `docs/qwen3_8b_jaws_de_lora_4090_v3_cluster_runbook.md`
- Datenausbauplan: `docs/qwen3_8b_jaws_de_lora_data_expansion_plan.md`

## Ablauf

1. Datensatz-Freeze und Export validieren.
2. Server-Environment mit `scripts/bootstrap_qwen_server_4090_env.sh` oder manuell mit passendem CUDA-PyTorch plus `training/transformers/requirements-qwen-server-4090-v2.txt` aufsetzen.
3. `python scripts/preflight_qwen_lora_server.py --config training/transformers/qwen3_8b_jaws_de_lora_4090_v3.yaml`
4. `bash scripts/start_qwen3_8b_jaws_de_lora_4090_v3.sh`
5. Nach dem Lauf `bash scripts/run_qwen3_8b_jaws_de_lora_4090_v3_smoke.sh`

Der `v3`-Pfad nutzt weiterhin denselben `transformers`-Stack, schreibt aber in eigene Log- und Output-Pfade und enthaelt einen dokumentierten Resume-/Recovery-Weg ueber `checkpoint-*`.

## Datensatzentscheidung

- Datensatzbasis fuer `v3`: `data/exports/qwen_sft/JAWS/DE/qwen3_8b_jaws_de_lora_4090_v3_20260328`
- Grund: dieser Freeze basiert auf dem erweiterten und reviewten Gold-v2-Stand mit `1003` Train / `123` Eval und ersetzt den kleineren `v2`-Freeze als naechsten vorbereiteten Run-Pfad.

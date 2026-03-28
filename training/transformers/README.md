# transformers

Dieser Ordner enthaelt den aktiven Qwen3-8B-PEFT/QLoRA-Pfad fuer JAWS-DE auf Basis des serverseitigen Linux-/RTX4090-v2-Runs.

## Dateien

- `qwen3_8b_jaws_de_lora_4090_v2.yaml` ist die neue serverseitige v2-Konfiguration fuer den naechsten echten Linux-/RTX4090-Lauf.
- `requirements-qwen-server-4090-v2.txt` pinnt die Python-Abhaengigkeiten fuer den vorbereiteten Server-Run.

## Ablauf

- Finaler Datensatz-Freeze: `data/exports/qwen_sft/JAWS/DE/qwen3_8b_jaws_de_lora_4090_v2_20260328`
- Startskript: `scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh`
- Preflight: `scripts/preflight_qwen_lora_server.py`
- Trainingsrunner: `scripts/run_qwen_lora_training.py`
- Smoke-Test: `scripts/run_qwen3_8b_jaws_de_lora_4090_v2_smoke.sh`
- Runbook: `docs/qwen3_8b_jaws_de_lora_4090_v2_runbook.md`

## Ablauf

1. Datensatz-Freeze und Export validieren.
2. Server-Environment mit `training/transformers/requirements-qwen-server-4090-v2.txt` aufsetzen.
3. `python scripts/preflight_qwen_lora_server.py --config training/transformers/qwen3_8b_jaws_de_lora_4090_v2.yaml`
4. `bash scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh`
5. Nach dem Lauf `bash scripts/run_qwen3_8b_jaws_de_lora_4090_v2_smoke.sh`

Der v2-Pfad nutzt weiterhin denselben `transformers`-Stack, schreibt aber in eigene Log- und Output-Pfade und enthaelt einen dokumentierten Resume-/Recovery-Weg ueber `checkpoint-*`.

## Datensatzentscheidung

- Datensatzbasis: `data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326`
- Grund: dieser Stand bleibt der letzte dokumentierte Export mit bestandenem Source-Faithfulness-Gate (`0` Flag-Faelle), waehrend der groessere `gold_v1_lora_pilot_clean`-Export weiterhin Ellipsis-/Faithfulness-Artefakte enthaelt und nicht mehr als Run-Pfad vorgesehen ist.

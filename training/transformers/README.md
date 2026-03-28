# transformers

Dieser Ordner enthaelt den bestehenden Qwen3-8B-PEFT/QLoRA-Pfad fuer JAWS-DE und den vorbereiteten Linux-Server-Run auf einer RTX 4090.

## Dateien

- `qwen3_8b_jaws_de_lora_clean_pilot_v1.yaml` ist die echte Pilot-Konfiguration auf dem voll validierten Clean-Export.
- `qwen3_8b_jaws_de_lora_clean_pilot_v1_dry_run.yaml` ist der kleine Technik-Check fuer denselben Datenstand.
- `qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry.yaml` ist der konservative Retry-Lauf nach dem ersten GPU-/Treiberabbruch.
- `qwen3_8b_jaws_de_lora_4090_v2.yaml` ist die neue serverseitige v2-Konfiguration fuer den naechsten echten Linux-/RTX4090-Lauf.
- `requirements-qwen-pilot.txt` nennt die bisherigen optionalen Laufzeit-Abhaengigkeiten fuer Pilot und Inferenz.
- `requirements-qwen-server-4090-v2.txt` pinnt die Python-Abhaengigkeiten fuer den vorbereiteten Server-Run.

## Ablauf

1. Export und Gold-Stand validieren.
2. `python scripts/run_qwen_lora_pilot.py --config training/transformers/qwen3_8b_jaws_de_lora_clean_pilot_v1_dry_run.yaml`
3. Falls ein laengerer Lauf unter Windows/GPU-Last instabil war: `python scripts/run_qwen_lora_pilot.py --config training/transformers/qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry.yaml`
4. Danach `python scripts/run_qwen_lora_pilot.py --config training/transformers/qwen3_8b_jaws_de_lora_clean_pilot_v1.yaml`
5. `python scripts/smoke_test_qwen_lora_adapter.py --config training/transformers/qwen3_8b_jaws_de_lora_clean_pilot_v1.yaml --adapter-dir training/transformers/outputs/qwen3_8b_jaws_de_lora_clean_pilot_v1/final_adapter`

## Server-Ready v2-Pfad

- Finaler Datensatz-Freeze: `data/exports/qwen_sft/JAWS/DE/qwen3_8b_jaws_de_lora_4090_v2_20260328`
- Startskript: `scripts/start_qwen3_8b_jaws_de_lora_4090_v2.sh`
- Preflight: `scripts/preflight_qwen_lora_server.py`
- Trainingsrunner: `scripts/run_qwen_lora_training.py`
- Smoke-Test: `scripts/run_qwen3_8b_jaws_de_lora_4090_v2_smoke.sh`
- Runbook: `docs/qwen3_8b_jaws_de_lora_4090_v2_runbook.md`

Der v2-Pfad trennt sich bewusst von Pilot-/Retry-Konfigurationen. Er nutzt weiterhin denselben `transformers`-Stack, schreibt aber in eigene Log- und Output-Pfade und enthaelt einen dokumentierten Resume-/Recovery-Weg ueber `checkpoint-*`.

## Pilot-Entscheidung

- Datensatzbasis: `data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326`
- Grund: der groessere Pilot-Cleanup-Stand ist zwar stub-frei, faellt aber aktuell noch durch den Source-Faithfulness-Gate-Check
- Hardware-Annahme: 1x RTX 3060 12 GB, daher konservativer 4-Bit-QLoRA-Lauf statt unquantisiertem LoRA

## Tatsaechlich ausgefuehrter erster End-to-End-Lauf

- Erfolgreicher Run: `qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry`
- Grund fuer den Retry-Pfad: der erste laengere Vollrun mit groesserem Kontext fuehrte unter Windows zu einem `nvlddmkm`-Treiberreset
- Erfolgreiches Artefakt:
  - `training/transformers/outputs/qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry/final_adapter`
- Wichtige Laufreports:
  - `training/transformers/outputs/qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry/run_summary.json`
  - `training/transformers/outputs/qwen3_8b_jaws_de_lora_clean_pilot_v1_stability_retry/smoke_test_results.json`

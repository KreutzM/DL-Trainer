# Qwen3-8B JAWS-DE LoRA 4090 v2 Dataset Freeze

Dieser Ordner ist der eingefrorene Export fuer den naechsten echten Linux-/RTX4090-LoRA-v2-Lauf.

## Inhalt

- `train.jsonl`: 689 Trainingsbeispiele
- `eval.jsonl`: 82 Eval-Beispiele
- `train.metadata.jsonl` und `eval.metadata.jsonl`: Provenance-Sidecars
- `manifest.json`: Hashes, Groessen, Quellpfade und Split-Konsistenz

## Herkunft

- Gefroren aus: `data/exports/qwen_sft/JAWS/DE/consolidated_gold_v1_lora_clean_20260326`
- Source of truth bleibt:
  - `data/gold/train/sft/JAWS/DE/consolidated_gold_v1_lora_clean_sft_samples.jsonl`
  - `data/gold/eval/JAWS/DE/consolidated_gold_v1_lora_clean_eval_cases.jsonl`

## Zweck

- klare, unverwechselbare Datensatzbasis fuer `qwen3_8b_jaws_de_lora_4090_v2`
- kein Demo-, Fixture- oder Stub-Stand
- stabiler Pfad fuer Linux-Preflight, Startskript und Resume

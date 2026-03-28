# Qwen3-8B JAWS-DE LoRA 4090 v3 Dataset Freeze

Dieser Ordner ist der vorbereitete Export fuer den naechsten Linux-/RTX4090-LoRA-Lauf auf Basis des erweiterten Gold-v2-Stands.

## Inhalt

- `train.jsonl`: 1003 Trainingsbeispiele
- `eval.jsonl`: 123 Eval-Beispiele
- `train.metadata.jsonl` und `eval.metadata.jsonl`: Provenance-Sidecars
- `manifest.json`: Hashes, Groessen, Quellpfade und Split-Konsistenz

## Herkunft

- Gefroren aus:
  - `data/gold/train/sft/JAWS/DE/consolidated_gold_v2_qwen_expansion_sft_samples.jsonl`
  - `data/gold/eval/JAWS/DE/consolidated_gold_v2_qwen_expansion_eval_cases.jsonl`

## Zweck

- klare, getrennte Datensatzbasis fuer `qwen3_8b_jaws_de_lora_4090_v3`
- deutlich groesserer, reviewter Stand als der fruehere `v2`-Freeze
- stabiler Pfad fuer Preflight, Startskript, Resume und Post-Run-Smoke-Test

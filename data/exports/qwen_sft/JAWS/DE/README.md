# JAWS-DE Qwen-SFT Exporte

Kanonischer aktueller Exportpfad:

- `data/exports/qwen_sft/JAWS/DE/current/`
- `docs/jaws_de_current_baseline.json`

Quelle:

- `data/gold/train/sft/JAWS/DE/codex_cli_support_validation_v2_promoted_sft_samples.jsonl`
- `data/gold/eval/JAWS/DE/codex_cli_support_validation_v2_promoted_eval_cases.jsonl`

Regel:

- Exporte sind abgeleitet und nicht Source of truth.
- Der aktuelle Export wird reproduzierbar ueber `scripts/export_qwen_sft.py` gebaut.
- Historische Gold-Dateien nicht still erneut als neuer produktiver Export interpretieren.

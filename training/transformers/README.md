# transformers

Dies ist der aktuell unterstuetzte JAWS-DE-Trainingsstack fuer die Current-Baseline.

Massgebliche Dateien:

- `training/transformers/jaws_de_current.yaml`
- `scripts/preflight_qwen_lora_server.py`
- `scripts/run_qwen_lora_training.py`

Datensatzquelle:

- `data/exports/qwen_sft/JAWS/DE/current/`
- `docs/jaws_de_current_baseline.json`

Regel:

- Fuer JAWS-DE nur diesen Stack als aktuellen Standard behandeln.
- Details zur Baseline und zum Export stehen in `docs/jaws_de_workflow.md`.
- Die maschinenlesbare Pointer-Datei fuer denselben Stand ist `docs/jaws_de_current_baseline.json`.

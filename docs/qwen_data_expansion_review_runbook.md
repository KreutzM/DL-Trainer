# Qwen Data Expansion Review Runbook

## Ziel

Dieses Runbook beschreibt den naechsten manuellen Block vor dem naechsten echten Trainingslauf:

1. neue Fokus-Wellen reviewen
2. reviewed Outputs promoten
3. Gold konsolidieren
4. neuen Freeze vorbereiten

Es ersetzt keinen menschlichen Review. Es macht den Review- und Promotionspfad nur reproduzierbar.

## Review-Eingaben

FAQ-Fokus:

- Jobs: `data/derived/teacher_jobs/JAWS/DE/qwen_focus_wave_v1_generation_jobs.jsonl`
- Stub-Outputs: `data/derived/teacher_outputs/JAWS/DE/qwen_focus_wave_v1_stub_teacher_outputs.jsonl`
- Review-Paket: `data/derived/teacher_outputs/JAWS/DE/qwen_focus_wave_v1_review_packet.json`

Step-Fokus:

- Jobs: `data/derived/teacher_jobs/JAWS/DE/qwen_step_focus_wave_v1_generation_jobs.jsonl`
- Stub-Outputs: `data/derived/teacher_outputs/JAWS/DE/qwen_step_focus_wave_v1_stub_teacher_outputs.jsonl`
- Review-Paket: `data/derived/teacher_outputs/JAWS/DE/qwen_step_focus_wave_v1_review_packet.json`

## Review im JSONL-Editor

Editor starten:

```bash
python scripts/editor_server.py --open-browser
```

Dann nacheinander:

1. `qwen_focus_wave_v1_stub_teacher_outputs.jsonl` laden
2. als reviewed Ziel z. B. `data/derived/teacher_outputs/JAWS/DE/qwen_focus_wave_v1_reviewed_teacher_outputs.jsonl` verwenden
3. `qwen_step_focus_wave_v1_stub_teacher_outputs.jsonl` laden
4. als reviewed Ziel z. B. `data/derived/teacher_outputs/JAWS/DE/qwen_step_focus_wave_v1_reviewed_teacher_outputs.jsonl` verwenden

## Review-Regeln

- Nur `human_reviewed`, wenn die Antwort quelltreu, knapp und task-passend ist.
- `step_by_step` nur freigeben, wenn wirklich nur dokumentierte Schritte enthalten sind.
- `clarification` nur freigeben, wenn genau eine fokussierte Rueckfrage gestellt wird.
- `troubleshooting` ablehnen, wenn der Text nur beschreibend ist und keine echte Diagnose-/Handlungsbasis hat.
- Keine Ellipsis-/Truncation-Artefakte freigeben.

## Validierung nach Review

FAQ-Welle:

```bash
python scripts/validate_teacher_pipeline.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/qwen_focus_wave_v1_generation_jobs.jsonl ^
  --outputs data/derived/teacher_outputs/JAWS/DE/qwen_focus_wave_v1_reviewed_teacher_outputs.jsonl
```

Step-Welle:

```bash
python scripts/validate_teacher_pipeline.py ^
  --jobs data/derived/teacher_jobs/JAWS/DE/qwen_step_focus_wave_v1_generation_jobs.jsonl ^
  --outputs data/derived/teacher_outputs/JAWS/DE/qwen_step_focus_wave_v1_reviewed_teacher_outputs.jsonl
```

## Promotion nach Gold

FAQ-Welle:

```bash
python scripts/promote_teacher_outputs.py ^
  --input data/derived/teacher_outputs/JAWS/DE/qwen_focus_wave_v1_reviewed_teacher_outputs.jsonl ^
  --train-output data/gold/train/sft/JAWS/DE/qwen_focus_wave_v1_promoted_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/qwen_focus_wave_v1_promoted_eval_cases.jsonl
```

Step-Welle:

```bash
python scripts/promote_teacher_outputs.py ^
  --input data/derived/teacher_outputs/JAWS/DE/qwen_step_focus_wave_v1_reviewed_teacher_outputs.jsonl ^
  --train-output data/gold/train/sft/JAWS/DE/qwen_step_focus_wave_v1_promoted_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/qwen_step_focus_wave_v1_promoted_eval_cases.jsonl
```

## Gold konsolidieren

```bash
python scripts/consolidate_gold_teacher_sets.py ^
  --train-dir data/gold/train/sft/JAWS/DE ^
  --eval-dir data/gold/eval/JAWS/DE ^
  --train-output data/gold/train/sft/JAWS/DE/consolidated_gold_v2_qwen_expansion_sft_samples.jsonl ^
  --eval-output data/gold/eval/JAWS/DE/consolidated_gold_v2_qwen_expansion_eval_cases.jsonl ^
  --report-output data/derived/teacher_outputs/JAWS/DE/consolidated_gold_v2_qwen_expansion_report.json
```

## Pflichtchecks vor neuem Freeze

```bash
python scripts/validate_jsonl.py --schema schemas/sft_sample.schema.json --input data/gold/train/sft/JAWS/DE/consolidated_gold_v2_qwen_expansion_sft_samples.jsonl
python scripts/validate_jsonl.py --schema schemas/eval_case.schema.json --input data/gold/eval/JAWS/DE/consolidated_gold_v2_qwen_expansion_eval_cases.jsonl
python scripts/check_provenance.py --input data/gold/train/sft/JAWS/DE/consolidated_gold_v2_qwen_expansion_sft_samples.jsonl
python scripts/check_provenance.py --input data/gold/eval/JAWS/DE/consolidated_gold_v2_qwen_expansion_eval_cases.jsonl
```

Danach:

- neuen Qwen-SFT-Export bauen
- Source-Faithfulness erneut auditieren
- erst dann neuen Trainings-Freeze setzen

## Noch nicht erledigt

Dieses Runbook bereitet nur den Pfad vor. Offen bleiben:

- echter menschlicher Review
- Promotion der tatsaechlich freigegebenen Outputs
- neuer konsolidierter Gold-Stand
- neuer Export-Freeze fuer den naechsten LoRA-Run

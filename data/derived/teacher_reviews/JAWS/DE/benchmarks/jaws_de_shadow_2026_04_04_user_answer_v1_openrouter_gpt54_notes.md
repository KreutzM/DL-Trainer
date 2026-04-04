# OpenRouter GPT-5.4 Shadow Wave: User-Sim + Answer

## Scope

- Run: `jaws_de_shadow_2026_04_04_user_answer_v1_openrouter_gpt54`
- Selection: `data/derived/teacher_jobs/JAWS/DE/shadow_wave_2026_04_04_user_answer_v1_selection.json`
- Profile set: `support_mvp_openrouter_gpt54_candidate`
- Stage roles:
  - user_simulation: `openai/gpt-5.4-mini`
  - answer: `openai/gpt-5.4`
  - judge: `openai/gpt-5.4`
- Judge handling: explicit `shadow_only` / secondary audit signal
- No promotion, no Codex-CLI run, no new model family

## Selection Design

- The wave scales the existing 20-job fresh-run seed to 32 jobs.
- Final task mix:
  - `step_by_step`: 8
  - `clarification`: 6
  - `faq_direct_answer`: 6
  - `troubleshooting`: 6
  - `uncertainty_escalation`: 6
- Split balance stays even:
  - train: 16
  - eval: 16
- The 12 added jobs are deterministic top-offs from the same `wave1_generation_jobs.jsonl` basis, with two extra `step_by_step` jobs per split and one extra job per split for every other task type.

## Run Health

- All three stages finished `32/32` jobs.
- No failed jobs.
- No retries in user-sim, answer or judge.
- This is a strong operational result for a larger shadow wave on the same conservative profile line.

## Quantitative Summary

- Judge decisions:
  - approve: 28
  - reject: 4
- Quality-score distribution:
  - min: 32
  - median: 94.5
  - max: 98
  - `<60`: 4
  - `90+`: 28
- Per task type:
  - `clarification`: 6 approve / 0 reject
  - `faq_direct_answer`: 6 approve / 0 reject
  - `step_by_step`: 4 approve / 4 reject
  - `troubleshooting`: 6 approve / 0 reject
  - `uncertainty_escalation`: 6 approve / 0 reject

## Qualitative Reading

### What looks good

- `troubleshooting`, `uncertainty_escalation`, `clarification` and `faq_direct_answer` remain consistently strong in this wider wave.
- The newly added 12-job top-off slice landed at `11 approve / 1 reject`.
- Several newly added `step_by_step` jobs are genuinely good rather than only barely passing:
  - `jaws_de_teacher_wave_v1::eval::step_by_step::0003`
  - `jaws_de_teacher_wave_v1::eval::step_by_step::0005`
  - `jaws_de_teacher_wave_v1::train::step_by_step::0008`

### What remains problematic

- All four rejects are `step_by_step`.
- The failures are not subtle calibration noise; they are answer-quality failures with procedural consequences:
  - missing final target-achieving step
  - duplicated step sequence
  - mixing two distinct procedures into one answer
- The strongest negative case is `jaws_de_teacher_wave_v1::train::step_by_step::0005`, where the procedure starts correctly but breaks off before the user goal is actually achieved.

### Overlap stability vs earlier 20-job GPT-5.4 wave

- On the 20 jobs shared with `jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1`, only one decision changed.
- That change is `jaws_de_teacher_wave_v1::eval::step_by_step::0002`.
- The earlier run approved a concise 3-step answer.
- The current run rejected the case because the new answer duplicated the same 3-step procedure verbatim.
- Interpretation:
  - this looks like answer regression / output instability in `step_by_step`
  - not like same-answer judge drift

## Recommendation

- `User-Sim + Answer`
  - Strong enough for larger shadow waves than the prior 8/20 subsets.
  - Not yet strong enough for anything rollout-like beyond shadowing, because `step_by_step` still fails in a concentrated, high-signal way.
- `Judge`
  - Good enough as a secondary/audit judge for this wave size.
  - Still not suitable as primary gate.
- `Most stable classes`
  - `troubleshooting`
  - `uncertainty_escalation`
  - `clarification`
  - most of `faq_direct_answer`
- `Main blocker`
  - `step_by_step`
- `Next sensible step`
  - continue scaling shadow waves for OpenRouter user-sim + answer
  - prioritize targeted prompt work on procedural completeness / de-duplication for `step_by_step`
  - do not spend the next iteration primarily on judge retuning

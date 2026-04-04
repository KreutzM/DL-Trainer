# OpenRouter GPT-5.4 Shadow Wave v2: Larger Step-by-Step Stress Check

## Scope

- Run: `jaws_de_shadow_2026_04_04_user_answer_v4_openrouter_gpt54`
- Selection: `data/derived/teacher_jobs/JAWS/DE/shadow_wave_2026_04_04_user_answer_v4_selection.json`
- Profile set: `support_mvp_openrouter_gpt54_candidate`
- Roles unchanged:
  - user_simulation: `openai/gpt-5.4-mini`
  - answer: `openai/gpt-5.4`
  - judge: `openai/gpt-5.4`
- Judge handling remains explicit `shadow_only` / secondary audit only.
- No new Codex-CLI run, no new Codex reference run, no promotion, no new model family.

## Selection Design

- The new wave expands the earlier 32-job shadow wave to 44 jobs.
- Task mix:
  - `step_by_step`: 12
  - `clarification`: 8
  - `faq_direct_answer`: 8
  - `troubleshooting`: 8
  - `uncertainty_escalation`: 8
- Split balance stays even:
  - train: 22
  - eval: 22
- Construction is deterministic from the same `wave1_generation_jobs.jsonl` basis.
- Relative to the prior 32-job wave:
  - overlap: 27 jobs
  - newly added jobs: 17
  - removed jobs: 5
- The new top-off slice deliberately overweights `step_by_step` again: 6 of the 17 new jobs are `step_by_step`.

## Run Health

- All three stages finished `44/44` jobs.
- No failed jobs.
- No retries in user-sim, answer or judge.
- This is another strong operational result for the same OpenRouter line at a larger reviewable wave size.

## Quantitative Summary

- Judge decisions:
  - approve: 43
  - reject: 1
- Quality-score distribution:
  - min: 41
  - median: 95
  - max: 98
  - `<60`: 1
  - `90+`: 41
- Per task type:
  - `clarification`: 8 approve / 0 reject
  - `faq_direct_answer`: 8 approve / 0 reject
  - `step_by_step`: 11 approve / 1 reject
  - `troubleshooting`: 8 approve / 0 reject
  - `uncertainty_escalation`: 8 approve / 0 reject

## Comparison vs the Prior 32-Job Wave

- Raw totals look much stronger than the prior 32-job rerun, but the selection is not identical, so the clean read is overlap plus top-off.
- Prior 32-job rerun (`v3`):
  - overall: `29 approve / 3 reject`
  - `step_by_step`: `5 approve / 3 reject`
- New 44-job wave:
  - overall: `43 approve / 1 reject`
  - `step_by_step`: `11 approve / 1 reject`
- On the 27 overlapping jobs:
  - v3: `25 approve / 2 reject`
  - v4: `26 approve / 1 reject`
- The only overlap decision flip is:
  - `jaws_de_teacher_wave_v1::eval::step_by_step::0001`
  - from `reject (45)` to `approve (95)`
- The 17-job newly added slice lands at `17 approve / 0 reject`.
- The 6 newly added `step_by_step` jobs all approve.

## Qualitative Step-by-Step Reading

### What looks stable now

- The old duplication family does not show up in this 44-job wave.
- No `step_by_step` answer visibly emits the same procedure twice.
- No visible `answer` plus `steps` double-emission pattern appears in the step-by-step slice.
- The six new `step_by_step` top-off jobs all pass, including:
  - `jaws_de_teacher_wave_v1::eval::step_by_step::0006`
  - `jaws_de_teacher_wave_v1::eval::step_by_step::0007`
  - `jaws_de_teacher_wave_v1::train::step_by_step::0003`
  - `jaws_de_teacher_wave_v1::train::step_by_step::0006`
  - `jaws_de_teacher_wave_v1::train::step_by_step::0009`
  - `jaws_de_teacher_wave_v1::train::step_by_step::0012`

### What still fails

- Only one case still rejects:
  - `jaws_de_teacher_wave_v1::train::step_by_step::0002`
- The failure is still high-signal and real:
  - the answer mixes the path into `Stimmeneinstellungen` with the separate `Stimmenprofil ausw?hlen` path
  - the final target is not carried through as one clean, complete procedure
- This means the main residual risk is no longer duplication; it is composite-procedure scoping plus completeness on harder requests.

### Borderline reading

- Only one approved `step_by_step` case lands below 90:
  - `jaws_de_teacher_wave_v1::eval::step_by_step::0007` at 89
- That case still reads acceptable; it is shorter and more example-shaped than the strongest procedural cases, but the judge still treats it as a valid documented Kurzprozedur.

## Spillover Check

- No new reject appears outside `step_by_step`.
- `clarification`, `faq_direct_answer`, `troubleshooting` and `uncertainty_escalation` all stay fully approved, including their newly added top-off cases.
- So the earlier `step_by_step` hardening still shows no visible negative spillover into the other core classes.

## Readout

- The `step_by_step` improvement holds under a meaningfully larger, still reviewable shadow wave.
- `step_by_step` is clearly more robust than before, but it remains the most fragile class because the remaining hard failure still sits there.
- The last concentrated problem is procedural completeness on composite or goal-sensitive requests, not broad instability and not judge drift.
- User-sim plus answer now looks robust enough for still larger shadow waves with materially less risk than before.
- The next sensible step is not more judge work. It is one more narrow prompt pass on completeness / single-procedure scoping for `step_by_step`, while continuing broader shadowing and data collection.

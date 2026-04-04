# OpenRouter GPT-5.4 Step-by-Step Answer Hardening

## Scope

- Baseline: `jaws_de_shadow_2026_04_04_user_answer_v1_openrouter_gpt54`
- Intermediate check: `jaws_de_shadow_2026_04_04_user_answer_v2_openrouter_gpt54`
- Final rerun: `jaws_de_shadow_2026_04_04_user_answer_v3_openrouter_gpt54`
- Job basis unchanged: `data/derived/teacher_jobs/JAWS/DE/shadow_wave_2026_04_04_user_answer_v1_job_ids.txt`
- User simulations reused unchanged from v1
- No new Codex-CLI run
- No new Codex reference run
- No new model family
- No promotion

## What Was Changed

- The `step_by_step` section in `prompts/teacher/jaws_de_support_answer_mvp.md` now explicitly requires:
  - exactly one consolidated procedure
  - no mixing of separate procedures
  - completion up to the actual goal state
  - clear order and operationally usable steps
  - no second step sequence inside `answer`
- The `step_by_step` output contract in `scripts/run_codex_cli_support_answer_batch.py` now explicitly says that procedural content belongs in `steps` and that `answer` may only be a short lead-in.
- Prompt version was raised to `jaws_de_support_answer_mvp_v3`.

## Failure Analysis

- Baseline v1 had 4 rejects, all in `step_by_step`.
- The visible failure patterns were:
  - missing last decisive goal step
  - duplicated procedure
  - mixed procedures
  - incoherent ordering
- The first v2 rerun showed that broad hardening alone was not enough:
  - one old duplication case improved
  - two new duplication regressions appeared because the model still emitted procedure text both in `answer` and in `steps`
- The final v3 correction addressed that specific JSON-shape failure by forcing procedural content into `steps`.

## Final v3 Result

- Overall:
  - v1: `28 approve / 4 reject`
  - v3: `29 approve / 3 reject`
- `step_by_step`:
  - v1: `4 approve / 4 reject`
  - v3: `5 approve / 3 reject`
- Other task types:
  - unchanged at full approval across `clarification`, `faq_direct_answer`, `troubleshooting`, `uncertainty_escalation`

## What Improved

- `jaws_de_teacher_wave_v1::eval::step_by_step::0002`
  - changed from `reject (52)` to `approve (95)`
  - real answer improvement, not just a judge reaction shift
  - old failure was a duplicated 3-step procedure
  - v3 emits the procedure only once
- The baseline reject patterns `duplicate_or_redundant_sequences` and `mixed_procedures` are no longer present in the final v3 reject set.

## What Remains Problematic

- `jaws_de_teacher_wave_v1::eval::step_by_step::0001`
  - still ends without a clearly completed goal state for Braille-Kurzschrift
- `jaws_de_teacher_wave_v1::train::step_by_step::0002`
  - no longer mixes two procedures, but remains too vague for a request that asks for exact profile-changing steps
- `jaws_de_teacher_wave_v1::train::step_by_step::0005`
  - still stops before the symbol's Braille representation is actually changed

## Readout

- `step_by_step` is now meaningfully better than v1.
- The improvement is real but narrow: it mostly removes duplication and procedure-mixing failures.
- `step_by_step` remains the main blocker because hard completeness failures are still unresolved.
- This is strong enough to lower risk for larger OpenRouter shadow waves, because the broad class spillover did not appear and one concentrated failure mode is clearly reduced.
- The next sensible step is a final completeness-focused hardening:
  - if the excerpt does not reach the actual goal state, the answer should not imply a finished end-to-end procedure
  - otherwise the answer must include the last goal-achieving step explicitly

# OpenRouter Long-Dialog Step Audit

## Scope

- Selection manifest: `shadow_wave_2026_04_04_user_answer_v8_long_dialog_step_audit_selection.json`
- Size: `13` jobs
- Focus: `10` targeted `step_by_step` cases plus `3` stable controls
- Models unchanged:
  - User-Sim: `openai/gpt-5.4-mini`
  - Answer: `openai/gpt-5.4`
  - Judge: `openai/gpt-5.4` as `shadow_only`
- No new Codex-CLI run
- No new Codex reference run
- No promotion in Gold

## Why this wave exists

The previous composite-step waves already showed that the broad branchy/composite hypothesis was too heterogeneous for another generic prompt edit.
This wave narrows the question further:

1. do long assistant flows with late closure stay green?
2. do chunk/scope boundary cases still collapse into meta-responses?
3. are the remaining `step_by_step` failures now homogeneous enough for one small evidence-backed prompt addition?

## Selection shape

The wave mixes:

- long settings and assistant procedures with explicit end states
- the import assistant split across adjacent chunks
- one known long multi-page dialog case that previously escalated
- three stable non-step controls

## Headline result

- Overall: `8 approve / 5 reject`
- `step_by_step`: `5 approve / 5 reject`
- Controls: `3 approve / 0 reject`

The controls staying green show that the wave did not create broad spillover.

## What the step rejects actually are

1. `eval::step_by_step::0004`
   - The answer is mostly correct but duplicates the full procedure.
   - This is a real answer-quality defect, but it is a different family from the chunk-scope failures below.

2. `train::step_by_step::0044`
3. `train::step_by_step::0046`
4. `train::step_by_step::0054`
5. `train::step_by_step::0061`
   - These all collapse into the same visible surface pattern: the answer comments that the source is incomplete or cut off instead of giving a usable continuation.
   - That looks like a chunk/scope entanglement, not a clean generic long-dialog answer bug.
   - The source excerpts for these cases are visibly truncated mid-procedure, so the reject is partially source-driven.

## What stayed green

- `train::step_by_step::0030`
- `train::step_by_step::0041`
- `train::step_by_step::0048`
- `train::step_by_step::0052`
- `train::step_by_step::0062`

These are the important counterexamples: complete long flows still hold up, including the second half of the import assistant and the import-from-previous-version anchor.

## Comparison to the earlier waves

- The earlier branchy/composite patterns still do not repeat cleanly.
- The wave does not reveal a single new homogeneous long-dialog failure family.
- Instead it separates into:
  - one duplication defect
  - several source-cutoff meta-responses

## Decision

Do not add a prompt example yet.

Reason:

- the new rejects are not one stable answer failure family
- four of the five rejects are clearly entangled with chunk/scope truncation
- the remaining duplication case is real, but it is not enough on its own to justify a broad prompt edit

## Recommended next move

Keep collecting or isolating more complete long assistant and chunk-boundary `step_by_step` cases.

If a later prompt edit is attempted, it should be narrow:

- avoid meta-commentary on partial excerpts when the visible procedure is still usable
- continue through the final documented end state


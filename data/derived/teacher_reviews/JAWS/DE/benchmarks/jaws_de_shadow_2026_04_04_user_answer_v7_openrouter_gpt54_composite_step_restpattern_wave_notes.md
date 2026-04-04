# OpenRouter composite-step rest-pattern wave

## Scope

- Selection manifest: `shadow_wave_2026_04_04_user_answer_v7_composite_step_restpattern_selection.json`
- Size: `16` jobs
- Focus: `12` targeted `step_by_step` cases plus `4` stable controls
- Models unchanged:
  - User-Sim: `openai/gpt-5.4-mini`
  - Answer: `openai/gpt-5.4`
  - Judge: `openai/gpt-5.4` as `shadow_only`
- No new Codex-CLI run
- No new Codex reference run
- No promotion in Gold

## Why this wave exists

The earlier v6 composite-step collection showed three related but still heterogeneous step failures:

1. adjacent-procedure mixing
2. one-sided branch selection
3. unnecessary escalation on a long assistant flow

This v7 wave was built to answer one narrower question: does the remaining rest zone now repeat cleanly enough to justify one small example-backed prompt addition?

## Selection shape

The wave repeats the earlier blockers, then adds fresh stress cases with:

- explicit either-or procedure branches
- neighboring subgoals in one source excerpt
- long dialog or assistant flows with fragile finish states
- a few stable controls outside `step_by_step`

## Headline result

- Overall: `13 approve / 3 reject`
- `step_by_step`: `10 approve / 2 reject`
- Controls: `3 approve / 1 reject`

This is still a harsh stress wave, but the residual step failures narrow further.

## What the step rejects actually are

1. `train::step_by_step::0054`
   - Clean new hard fail.
   - The source gives a concrete long procedure for fixing prompt labels in multi-page dialogs.
   - The answer does not attempt the procedure and only says `Ich muss kurz eskalieren.`
   - This is real prompt-relevant evidence: avoidable escalation on a documented long multi-dialog flow.

2. `train::step_by_step::0061`
   - Persistent reject, but weaker as prompt evidence than it first looks.
   - The answer again stops before the final import completion.
   - Important caveat: this job's source chunk only covers the first half of the SBAK import assistant, while `train::step_by_step::0062` contains the later merge and completion steps.
   - In the same v7 wave, `train::step_by_step::0062` is approved.
   - So `0061` is partly a chunk-boundary and goal-scope problem, not a clean standalone prompt-failure signal.

## What did not repeat

Several branchy or composite stress cases stayed green:

- `eval::step_by_step::0004`
- `train::step_by_step::0013`
- `train::step_by_step::0019`
- `train::step_by_step::0037`
- `train::step_by_step::0053`
- `train::step_by_step::0062`

This matters because the broad branchy/composite hypothesis does not repeat uniformly in this wave.

Two earlier v6 blockers also flipped back to green:

- `train::step_by_step::0002`: `reject 54 -> approve 94`
- `eval::step_by_step::0006`: `reject 43 -> approve 90`

So adjacent-procedure mixing and one-sided branch collapse did not reproduce here.

## Non-step control note

`train::uncertainty_escalation::0010` flipped from green in v6 to reject in v7 because the answer behaved like a direct FAQ answer instead of a true uncertainty escalation.

That control failure should be tracked separately, but it is not evidence for another `step_by_step` prompt edit.

## Decision

Do not add the next prompt example yet.

Reason:

- the new clean step failure is `0054`, an avoidable escalation on a documented long dialog flow
- the repeated `0061` reject is mixed with source chunk coverage and user-goal scope
- the earlier branch-mix and branch-collapse patterns did not repeat

So the remaining step rest zone is still not homogeneous enough for one generic "branchy/composite" example-backed prompt addition.

## Recommended next move

Keep collecting or isolating a few more long assistant or multi-dialog `step_by_step` cases first.

If a later targeted prompt addition is attempted, it should be narrower than the current branchy/composite label:

- do not escalate when a documented long procedure exists
- stay inside one documented assistant flow
- continue through the final `Fertigstellen` or `OK` result state

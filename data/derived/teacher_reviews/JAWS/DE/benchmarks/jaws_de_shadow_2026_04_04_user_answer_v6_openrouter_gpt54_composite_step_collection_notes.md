# OpenRouter composite-step collection

## Scope

- Selection manifest: `shadow_wave_2026_04_04_user_answer_v6_composite_step_selection.json`
- Size: `13` jobs
- Focus: `9` targeted `step_by_step` cases plus `4` stable controls
- Models unchanged:
  - User-Sim: `openai/gpt-5.4-mini`
  - Answer: `openai/gpt-5.4`
  - Judge: `openai/gpt-5.4` as `shadow_only`
- No new Codex-CLI run
- No new Codex reference run
- No promotion in Gold

## Why these cases

The step-focused subset was built to stress three narrow hypotheses:

1. Adjacent documented procedures in the same source section can still be merged incorrectly.
2. Branchy user goals such as add/remove or import/overwrite can collapse to only one branch.
3. Long procedures with warnings, assistant stages, or nested dialogs can lose the actual target state or even over-escalate.

## Headline result

- Overall: `10 approve / 3 reject`
- `step_by_step`: `6 approve / 3 reject`
- Controls: `4 approve / 0 reject`

So the targeted subset is much harsher than the broader 44-job wave, but the instability still stays concentrated in `step_by_step`.

## What failed

1. `train::step_by_step::0002`
   - The known blocker reproduces.
   - Failure family: adjacent-procedure mix.
   - The answer opens Stimmeneinstellungen, then tries to satisfy profile selection inside that path instead of following the separately documented `JAWS TASTE+STRG+S` path.

2. `eval::step_by_step::0006`
   - New meaningful hard fail.
   - Failure family: one-sided branch selection.
   - The user asks how to add or remove a voice, but the answer narrows the procedure to installing a voice only.

3. `train::step_by_step::0061`
   - New different hard fail.
   - Failure family: unnecessary escalation on a long guided procedure.
   - The source contains a clear import assistant flow, but the answer responds with `Ich muss eskalieren.`

## What stayed green

Several branchy or potentially fragile cases still stayed clearly approved:

- `eval::step_by_step::0007`
- `train::step_by_step::0007`
- `train::step_by_step::0017`
- `train::step_by_step::0031`
- `train::step_by_step::0048`
- `train::step_by_step::0063`

This matters because it shows the system is not broadly failing on every branchy or multi-stage procedure. The remaining errors are concentrated in a smaller hard subset.

## Interpretation

There is now enough evidence that a real residual stress family exists around branchy or composite `step_by_step` requests. But the family is not yet cleanly singular:

- one case is true adjacent-procedure mixing
- one case is branch-scope collapse to only one requested path
- one case is unnecessary escalation on a documented assistant flow

That means the repo now has enough evidence for a real rest pattern, but not yet for a final abstract prompt tweak with high confidence.

## Recommendation

Do not do another broad prompt-hardening step from this wave alone.

The better next move is:

1. Collect a few more hard branchy/composite `step_by_step` examples.
2. If the same shape repeats, prefer one tiny example-backed prompt addition rather than a rubric note.

Reason: the visible failures are answer-generation problems, not primarily judge-only behavior.

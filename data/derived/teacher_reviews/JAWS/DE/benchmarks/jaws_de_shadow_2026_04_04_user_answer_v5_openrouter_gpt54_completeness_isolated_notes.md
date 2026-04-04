# OpenRouter step_by_step completeness pass

## Scope

- Baseline: `jaws_de_shadow_2026_04_04_user_answer_v4_openrouter_gpt54`
- Candidate: `jaws_de_shadow_2026_04_04_user_answer_v5_openrouter_gpt54_completeness_isolated`
- Comparison basis: same 44 job ids and the same saved v4 user simulations
- Models unchanged:
  - User-Sim basis reused from v4 (`openai/gpt-5.4-mini`)
  - Answer rerun with `openai/gpt-5.4`
  - Judge rerun with `openai/gpt-5.4` as `shadow_only`
- No new Codex-CLI run
- No new Codex reference run
- No promotion in Gold

## Minimal prompt change

The step-by-step answer prompt was tightened only in the targeted area:

1. Choose one continuous documented procedure when adjacent but separate procedures are nearby.
2. Finish at the actual requested target state; the last step must reach or confirm it.
3. Keep the beginning and the ending inside the same documented procedure instead of stitching neighboring subgoals together.

The same condensed contract was mirrored in the answer batch script, and the prompt version was bumped from `jaws_de_support_answer_mvp_v3` to `jaws_de_support_answer_mvp_v4`.

## Controlled rerun result

- Overall stays unchanged: `43 approve / 1 reject`
- `step_by_step` stays unchanged: `11 approve / 1 reject`
- Decision flips versus v4 on the same saved user simulations: `0`
- New rejects outside `step_by_step`: `0`

So the pass does not create visible class spillover, but it also does not improve the only remaining blocker.

## step_by_step qualitative read

Remaining reject:

- `jaws_de_teacher_wave_v1::train::step_by_step::0002`

What changed:

- v4 failure: the answer mixed the Stimmeneinstellungen path with the separate Stimmenprofil-auswaehlen path and ended without a clean goal-completing finish.
- v5 isolated failure: the answer over-corrects in the other direction and keeps only the direct Stimmenprofil path, dropping the documented opening sequence for Stimmeneinstellungen entirely.

This means the failure is still narrow, but it is not just "missing the final step". The harder residual problem is now:

- composite goal scoping
- choosing the correct single documented procedure when the request spans two nearby subgoals
- staying complete relative to that chosen scope

Other `step_by_step` cases remain stable. The earlier duplication / double-emission family does not reappear.

## Conclusion

`step_by_step` is still broadly robust for larger shadow waves, but this prompt pass does not materially improve the last hard case. The main blocker remains `step_by_step`, specifically composite-goal scoping plus completeness on the hardest requests.

The next sensible step is no longer another broad prompt tightening pass. The better next move is to collect and shadow a few more hard composite-goal `step_by_step` examples and use that evidence to decide whether one very specific example-driven prompt addition or a rubric clarification is warranted.

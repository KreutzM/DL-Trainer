# OpenRouter user-sim cheap-model benchmark

## Scope

- Run: `jaws_de_shadow_2026_04_04_user_sim_gpt41mini_answer_gpt54_benchmark_v1`
- Selection: `data/derived/teacher_jobs/JAWS/DE/shadow_wave_2026_04_04_user_answer_v4_selection.json`
- Same 44-job basis as the stronger `v4` GPT-5.4 reference wave
- Stage models:
  - User-Sim: `openai/gpt-4.1-mini`
  - Answer: `openai/gpt-5.4`
  - Judge: `openai/gpt-5.4` as `shadow_only`
- No Codex-CLI run
- No promotion in Gold
- No default switch

## Why GPT-4.1 Mini

- OpenRouter currently lists:
  - `openai/gpt-4.1-mini` at `$0.40/M` input and `$1.60/M` output
  - `openai/gpt-5.4-mini` at `$0.75/M` input and `$4.50/M` output
- That makes GPT-4.1 Mini materially cheaper while still staying on an OpenAI instruction-following line with strong structure fidelity.
- The goal of this pass was not to cheapen Answer or Judge. It was to see whether User-Sim can move first without visibly degrading the downstream pipeline.

## Quantitative result

- Reference `v4` wave:
  - overall: `43 approve / 1 reject`
  - `step_by_step`: `11 approve / 1 reject`
- Cheap user-sim candidate wave:
  - overall: `42 approve / 2 reject`
  - `step_by_step`: `10 approve / 2 reject`
- Stable classes remain fully green in both runs:
  - `clarification`
  - `faq_direct_answer`
  - `troubleshooting`
  - `uncertainty_escalation`

## Cost signal

- Approximate provider-reported User-Sim cost:
  - reference GPT-5.4 mini: `$0.3604`
  - candidate GPT-4.1 mini: `$0.1550`
- That is roughly a `57%` reduction on this same 44-job basis.
- So the price signal is real and meaningful.

## What changed downstream

There are exactly three decision flips, and all three stay inside `step_by_step`.

1. `eval::step_by_step::0001`
   - `approve 95 -> reject 62`
   - The cheaper User-Sim asked more explicitly for the full end state.
   - The unchanged GPT-5.4 answer then stopped one step short and the judge rejected it for missing the final completion step.

2. `train::step_by_step::0002`
   - `reject 41 -> approve 92`
   - This is the one real improvement.
   - The cheaper User-Sim narrowed the ask to documented Stimmeneinstellungen changes and avoided the old adjacent-procedure mix around profile selection.

3. `train::step_by_step::0003`
   - `approve 98 -> reject 38`
   - This is the most important negative flip.
   - The cheaper User-Sim overreached to a stronger goal (`Nachschlagewerk als Standard festlegen`) than the source chunk cleanly supports, so the answer could only satisfy the opening subset.

## User-Sim quality read

- The candidate stayed structurally valid and operationally clean: `44/44` user sims, no retries, no failed jobs.
- But its request style shifted:
  - `neutral`: `6 -> 27`
  - `task_focused`: `13 -> 3`
  - `uncertain`: `23 -> 12`
- Average request length increased slightly:
  - `164.8 -> 174.6` characters
- That looks like a real behavioral shift, not random noise.
- In practice, the cheaper model tends to write cleaner, more explicit requests, but in `step_by_step` that sometimes sharpens the demanded end goal beyond the available source span.

## Readout

- User-Sim on GPT-4.1 Mini is promising on cost and does not destabilize the non-step classes.
- But on the exact same 44-job benchmark it still makes the net outcome slightly worse because `step_by_step` becomes less stable overall.
- So the evidence is not strong enough yet for a user-sim switch, even though the cost reduction is attractive.

## Recommendation

- Do not switch User-Sim to `gpt-4.1-mini` yet.
- Keep Answer on `gpt-5.4`.
- If price-performance work continues, the next sensible step is one narrow follow-up on `step_by_step`-sensitive user-sim goal scoping:
  - either a small shadow subset focused on step completion sensitivity
  - or one tiny user-sim prompt adjustment to avoid unsupported composite end goals before re-benchmarking

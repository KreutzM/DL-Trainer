# JAWS-DE Shadow Benchmark 2026-04-04 Small v1

## Scope

- Benchmark name: `jaws_de_shadow_2026_04_04_small_v1`
- Selection manifest: `data/derived/teacher_jobs/JAWS/DE/shadow_benchmark_2026_04_04_small_v1_selection.json`
- Selection size: 8 jobs
- Split mix: 5 eval, 3 train
- Task coverage: `clarification`, `faq_direct_answer`, `step_by_step`, `troubleshooting`, `uncertainty_escalation`
- Strategy: one eval example per task type plus extra train coverage for `faq_direct_answer`, `step_by_step` and `troubleshooting`

## Runs Used

Reference run:

- Run name: `jaws_de_shadow_2026_04_04_small_v1_codex`
- Profile set: `support_mvp_default`
- Status: completed

Candidate run:

- Run name: `jaws_de_shadow_2026_04_04_small_v1_openrouter_retry1`
- Profile set: `support_mvp_openrouter_candidate`
- Status: completed

Comparison artifact:

- `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_small_v1_comparison.json`

Operational note:

- The first OpenRouter attempt failed in `user_simulation` because `max_output_tokens` was too low for the 8-item JSON batch and the response ended with `finish_reason=length`.
- For the actual benchmark run, the OpenRouter candidate profile stayed otherwise unchanged but raised `max_output_tokens` to workable benchmark values:
  - `user_simulation`: 2200
  - `answer`: 2600
  - `judge`: 3600

## Core Metrics

Reference:

- 8/8 jobs completed in all stages
- 7 approved, 1 rejected
- average judge quality score: 88.12
- schema and provenance checks: passed

Candidate:

- 8/8 jobs completed in all stages
- 8 approved, 0 rejected
- average judge quality score: 91.25
- schema and provenance checks: passed

Comparison deltas from the benchmark summary:

- selected jobs match: `true`
- teacher output rows delta: `0`
- reviewed output rows delta: `0`
- approval delta: `+1` for candidate
- rejection delta: `-1` for candidate
- average quality score delta: `+3.13` for candidate

Observed elapsed time deltas on this 8-job subset:

- `user_simulation`: candidate faster by 9.76 s
- `answer`: candidate faster by 78.43 s
- `judge`: candidate faster by 0.45 s

These runtime numbers are only indicative because the benchmark is very small and network/provider variance is still high.

## Qualitative Observations

### User-Sim

OpenRouter produced structurally clean user simulations and matched the full 8/8 job count without schema issues after the token-limit fix. The sampled requests were plausible and support-like, but tended to be slightly more explanatory and less tightly narrowed than the Codex baseline.

Example:

- `eval::clarification::0001` asks for a general explanation of Braille functions and focus behavior instead of a narrower support-style uncertainty. This is usable, but slightly less sharp than the Codex reference style.

### Answer

OpenRouter looks promising for `faq_direct_answer` and `uncertainty_escalation` on this subset.

- `eval::faq_direct_answer::0003` stayed concise, documentation-bound and was judged stronger than the Codex reference.
- `eval::uncertainty_escalation::0003` correctly preserved the evidence boundary and did not invent a blanket guarantee.
- `train::step_by_step::0001` produced a complete, clean four-step answer and was approved.

The main caution remains `step_by_step` on eval-style cases.

### Judge / Reviewer Behavior

This is the clearest no-go signal from the first shadow benchmark.

For `eval::step_by_step::0001`:

- Codex reference judge rejected the generated answer because the procedure stopped too early and missed the decisive documented switch to Braille-Kurzschrift.
- OpenRouter candidate judge approved its own corresponding answer with quality score 90, while also noting that the final step still ended abruptly and could be more complete.

That means the candidate judge currently appears more lenient than the Codex baseline on a known high-risk case. The better headline metrics for the candidate run therefore cannot yet be interpreted as a real quality win. Part of the gain is plausibly judge strictness drift.

## Conclusion

OpenRouter is now technically runnable on the Support-MVP benchmark path and produced valid artifacts on the chosen subset. That is a real milestone.

However, the first actual benchmark does **not** justify a rollout switch.

Current recommendation by stage:

- `user_simulation`: realistic candidate for further shadow benchmarking
- `answer`: promising candidate, especially for `faq_direct_answer` and evidence-bound direct answers, but still needs more `step_by_step` coverage
- `judge`: not rollout-ready; strictness drift versus Codex is the main blocker

## Recommended Next Step

1. Keep Codex CLI as production default.
2. Run a second OpenRouter shadow benchmark on a slightly larger subset with extra `step_by_step` coverage.
3. Add a cross-check pass for judge behavior instead of trusting candidate self-judging alone.
4. Treat `judge` as frozen on Codex until strictness drift is better understood.

If a selective OpenRouter rollout is explored later, `user_simulation` is the first plausible candidate, `answer` is a possible second candidate, and `judge` should stay on Codex for now.

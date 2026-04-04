# JAWS-DE Shadow Benchmark 2026-04-04 Small v1, OpenRouter GPT-5.4 Follow-up

## Scope

- Benchmark name: `jaws_de_shadow_2026_04_04_small_v1`
- Selection manifest: `data/derived/teacher_jobs/JAWS/DE/shadow_benchmark_2026_04_04_small_v1_selection.json`
- Selection size: 8 jobs
- Reused Codex reference artifacts only:
  - `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_small_v1_codex_pipeline_report.json`
  - `data/derived/teacher_outputs/JAWS/DE/jaws_de_shadow_2026_04_04_small_v1_codex_reviewed_teacher_outputs.jsonl`
  - `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_small_v1_codex_judge_results.jsonl`
- No new Codex CLI run was started.

## Candidate Profile Used

- Profile set: `support_mvp_openrouter_gpt54_candidate`
- Stage allocation:
  - `user_simulation`: `openai/gpt-5.4-mini`
  - `answer`: `openai/gpt-5.4`
  - `judge`: `openai/gpt-5.4`

Rationale:

- `gpt-5.4-mini` keeps the user-sim stage cheap and fast while still staying on the GPT-5.4 line.
- `gpt-5.4` for `answer` is the main quality probe.
- `gpt-5.4` for `judge` was chosen deliberately to re-test the known strictness problem against the stronger variant instead of repeating the previous mini-judge setup.

## Runs Compared

Reference:

- Run name: `jaws_de_shadow_2026_04_04_small_v1_codex`
- Profile set: `support_mvp_default`
- Status: completed earlier and reused as-is

Previous OpenRouter candidate for context:

- Run name: `jaws_de_shadow_2026_04_04_small_v1_openrouter_retry1`
- Profile set: `support_mvp_openrouter_candidate`

New GPT-5.4 OpenRouter candidate:

- Run name: `jaws_de_shadow_2026_04_04_small_v1_openrouter_gpt54_v1`
- Profile set: `support_mvp_openrouter_gpt54_candidate`

Comparison artifact:

- `data/derived/teacher_reviews/JAWS/DE/benchmarks/jaws_de_shadow_2026_04_04_small_v1_gpt54_comparison.json`

## Core Metrics

Codex reference:

- 8/8 jobs completed in all stages
- 7 approved, 1 rejected
- average judge quality score: 88.12

Previous OpenRouter candidate (`gpt-4.1` / `gpt-4.1-mini`):

- 8/8 jobs completed in all stages
- 8 approved, 0 rejected
- average judge quality score: 91.25

GPT-5.4 candidate:

- 8/8 jobs completed in all stages
- 7 approved, 1 rejected
- average judge quality score: 90.12
- schema and provenance checks: passed

Codex vs GPT-5.4 comparison deltas:

- selected jobs match: `true`
- teacher output rows delta: `0`
- reviewed output rows delta: `0`
- approval delta: `0`
- rejection delta: `0`
- average quality score delta: `+2.00` for GPT-5.4 candidate

Stage runtimes on this 8-job subset:

- `user_simulation`: GPT-5.4 candidate faster than Codex by 15.28 s
- `answer`: GPT-5.4 candidate faster than Codex by 63.90 s
- `judge`: GPT-5.4 candidate slower than Codex by 5.71 s

Compared with the earlier OpenRouter candidate, the GPT-5.4 line was slower and more expensive, but not wildly so on this tiny subset.

## Token And Cost Visibility

OpenRouter response metadata is available for this run. Summed over the 5 provider batches in `data/derived/teacher_runs/JAWS/DE/jaws_de_shadow_2026_04_04_small_v1_openrouter_gpt54_v1/`:

- prompt tokens: about `15.4k`
- completion tokens: about `5.6k`
- reasoning tokens reported: `0`
- provider-reported cost: about `$0.1019`

For context, the previous OpenRouter candidate on the same subset reported about `$0.0431`.

These numbers are only indicative for this tiny benchmark. The relevant signal here is the qualitative tradeoff: noticeably stronger judge alignment than the first OpenRouter run, at higher cost.

## Qualitative Observations

### User-Sim

The GPT-5.4-mini user-sim outputs were clearly better aligned with the support framing than the earlier OpenRouter candidate.

- `eval::clarification::0001` is now a narrow uncertainty about Anzeige vs. Eingabebefehle instead of a broad “explain the whole section” request.
- `eval::step_by_step::0001` asks directly for the Braille-Kurzschrift procedure in a concise way.
- `eval::troubleshooting::0004` explicitly mentions the active video call and the possibility of a documented limitation.

That makes `user_simulation` a credible next-stage candidate.

### Answer

The GPT-5.4 answer stage is the strongest OpenRouter answer pass seen so far on this subset.

- `eval::faq_direct_answer::0003` is shorter and cleaner than both Codex and the earlier OpenRouter run while still preserving the documented default value.
- `eval::uncertainty_escalation::0003` is explicit about what is covered by the source and where the evidence boundary stops.
- `eval::troubleshooting::0004` names the active-video-call limitation first and keeps the camera-selection shortcut anchored in the source.

`step_by_step` remains the main caution. The raw GPT-5.4 answer is source-faithful and includes the decisive fifth step, which is better than the Codex reference failure on this case. But the candidate still did not turn this into a clean approval on the benchmark because the judge flagged a duplicate-step-block style problem in the final rendered answer path.

### Judge / Strictness

This is the most important delta versus the earlier OpenRouter candidate.

For `eval::step_by_step::0001`:

- Codex reference judge: `reject` / quality `54`
- earlier OpenRouter candidate judge: `approve` / quality `90`
- GPT-5.4 OpenRouter judge: `reject` / quality `42`

So the previously observed strictness drift clearly improved. The GPT-5.4 judge no longer waves through the known high-risk `step_by_step` case.

The rejection rationale is not identical:

- Codex rejected for incompleteness before the decisive Braille-Kurzschrift selection step.
- GPT-5.4 rejected for a formatting/duplication issue in the step presentation.

That means the judge is materially more conservative than before, but still not yet proven fully aligned with the Codex baseline. The sample is too small for a rollout decision.

## Conclusion

The GPT-5.4 line is a materially stronger OpenRouter candidate basis than the earlier `gpt-4.1` run.

Current recommendation by stage:

- `user_simulation`: yes, realistic candidate for more shadow benchmarks
- `answer`: yes, serious candidate for expanded shadow testing
- `judge`: improved enough to keep testing, but still not rollout-ready on this evidence alone

This is the first OpenRouter candidate that looks serious across all three stages, but the `judge` stage still needs a larger confirmation pass before it can be trusted for rollout decisions.

## Recommended Next Step

1. Keep Codex CLI as production default.
2. Keep using the existing Codex reference artifacts as baseline for this benchmark family.
3. Run a slightly larger GPT-5.4 shadow benchmark with extra `step_by_step` coverage.
4. Add a cross-check evaluation where GPT-5.4-generated answers are also reviewed against the Codex judge baseline, so stage quality and judge behavior can be separated more cleanly.

If a selective OpenRouter rollout is explored after that:

- `user_simulation` is the first plausible candidate,
- `answer` is the second plausible candidate,
- `judge` is no longer an immediate no-go, but still not ready for any default or rollout change.

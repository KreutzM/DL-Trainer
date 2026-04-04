# JAWS-DE Shadow Benchmark 2026-04-04 Small v1

## Scope

- Benchmark name: `jaws_de_shadow_2026_04_04_small_v1`
- Selection manifest: `data/derived/teacher_jobs/JAWS/DE/shadow_benchmark_2026_04_04_small_v1_selection.json`
- Selection size: 8 jobs
- Split mix: 5 eval, 3 train
- Task coverage: `clarification`, `faq_direct_answer`, `step_by_step`, `troubleshooting`, `uncertainty_escalation`
- Strategy: one eval example per task type plus extra train coverage for `faq_direct_answer`, `step_by_step` and `troubleshooting`

## Runs Attempted

Reference run:

- Run name: `jaws_de_shadow_2026_04_04_small_v1_codex`
- Profile set: `support_mvp_default`
- Status: completed

Candidate run:

- Run name: `jaws_de_shadow_2026_04_04_small_v1_openrouter`
- Profile set: `support_mvp_openrouter_candidate`
- Status: blocked before execution
- Blocking error: `Profile set 'support_mvp_openrouter_candidate' stage 'user_simulation' requires environment variable OPENROUTER_API_KEY`

Because the OpenRouter candidate run never produced a benchmark-marked pipeline report, `scripts/compare_support_mvp_benchmarks.py` could not be executed for this benchmark pair without violating the existing comparison guardrails.

## Reference Metrics

Pipeline report: `data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_small_v1_codex_pipeline_report.json`

Stage completion:

- User simulation: 8/8 completed, 0 failed, 0 retries, `gpt-5.4-mini`, 22.87 s total
- Answer: 8/8 completed, 0 failed, 0 retries, `gpt-5.4`, 98.40 s total
- Judge: 8/8 completed, 0 failed, 0 retries, `gpt-5.4-mini`, 15.32 s total

Artifact quality:

- Teacher outputs: 8 rows
- Reviewed outputs: 8 rows
- Judge results: 8 rows
- Review status: 7 `codex_reviewed`, 1 `rejected`
- Judge decisions: 7 `approve`, 1 `reject`
- Average judge quality score: 88.12
- Schema and provenance checks: passed on reviewed outputs

## Qualitative Spot Checks

Observed strengths in the Codex reference run:

- `faq_direct_answer` stayed compact and documentation-bound. Example `eval::faq_direct_answer::0003` correctly explained `Länge des Textblocks` with the documented shortcut context and default value 25.
- `clarification` stayed disciplined. Example `eval::clarification::0001` was approved for using exactly one narrowing follow-up question instead of drifting into explanation.
- `uncertainty_escalation` handled evidence limits well. Example `eval::uncertainty_escalation::0003` explicitly avoided claiming that the setting applies uniformly across all message types.
- A train-side `step_by_step` example (`train::step_by_step::0001`) produced a clean four-step procedure and was approved with quality score 95.

Known risk confirmed even in the reference path:

- `eval::step_by_step::0001` was rejected. The judge flagged that the response stopped before the decisive documented switch to Braillekurzschrift and therefore failed the requirement for a complete documented procedure.
- This means `step_by_step` remains a sensitive stage/output type even before comparing providers. It is a bad candidate for a first low-supervision rollout.

## Conclusion

This benchmark is only a partial benchmark, not a valid Codex-vs-OpenRouter comparison.

- Codex reference path is stable on the chosen 8-job subset.
- OpenRouter is not yet benchmarked in this environment because the required runtime secret is missing locally.
- No stage is currently rollout-ready for OpenRouter on the basis of this run, because there is no candidate evidence.
- If OpenRouter becomes runnable, the first serious comparison should keep this exact subset and start with close review of `user_simulation` and `judge`, while treating `step_by_step` answer cases as the primary no-go check.

## Recommended Next Step

1. Provision `OPENROUTER_API_KEY` locally and rerun the candidate benchmark with the same selection manifest and benchmark name.
2. Run `scripts/compare_support_mvp_benchmarks.py` on the resulting reference/candidate pair.
3. Review stage-level deltas with extra attention on:
   - `step_by_step` completeness
   - `faq_direct_answer` brevity and source fidelity
   - evidence-bound escalation behavior
   - judge strictness drift versus the Codex baseline

Until that candidate run exists, Codex CLI should remain the only realistic path for production and for any further rollout decisions.

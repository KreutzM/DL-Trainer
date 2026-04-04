# Curated Pre-Gold Wave v16

## Bottom Line

The strong OpenRouter path is stable enough to support a larger curated pre-gold candidate pool.
The remaining rejects are concentrated and local:

- `step_by_step` remains the main residual risk.
- `clarification` has two narrow misses.
- `faq_direct_answer`, `troubleshooting`, and `uncertainty_escalation` are fully green.
- No retries or failures occurred in any stage.

## Selection

- 60 jobs total
- 30 train / 30 eval
- 12 each for `clarification`, `faq_direct_answer`, `step_by_step`, `troubleshooting`, `uncertainty_escalation`
- 6 per task per split

This is a balanced broader wave, not a `step_by_step` stress test.

## Observed Reject Families

### `clarification`

- One reject is too broad and asks the wrong framing.
- One reject is too narrow and loses the user's core question.

### `step_by_step`

- Two rejects are incomplete procedures that stop before the real completion.
- Three rejects are duplicate full procedures.
- One reject is an incomplete or distorted mixed path.
- One reject is a truncated path that misses the final setting change.
- One reject is mostly faithful but distorts the decisive dialog step.

## Interpretation

- The wave is clean enough to be a basis for a larger curated candidate pool.
- The remaining failures are not diffuse.
- The strongest next move is controlled pre-gold derivation with selection filtering for the narrow residual cases.
- Another broad prompt-hardening pass is not the right next step.

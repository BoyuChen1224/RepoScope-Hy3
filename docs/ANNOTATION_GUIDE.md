# Human annotation guide

## Purpose

Human labels calibrate the semantic evaluator; they do not overwrite deterministic path and quote
checks. Annotators receive a frozen evidence manifest and one anonymized report. Generator name,
sampling parameters, and automatic scores are hidden until adjudication.

## Claim-level labels

For every material claim, select exactly one:

- `supported`: cited evidence directly establishes the claim without material overreach;
- `partially_supported`: the core is supported but wording, scope, or certainty exceeds the evidence;
- `unsupported`: available evidence does not establish the claim;
- `contradicted`: available evidence directly conflicts with the claim.

Record the strongest evidence path and a one-sentence rationale. A citation that is merely related to
the topic is not supporting evidence.

## Report-level dimensions

Use the 0-4 anchors in `docs/EVALUATION.md` for factual accuracy, evidence entailment, risk
completeness, uncertainty disclosure, actionability, and professional clarity. Do not reward length,
confidence, formatting polish, or professional vocabulary by itself.

## Independence and adjudication

1. Two annotators label each selected case independently.
2. Neither annotator sees the other's labels or evaluator scores.
3. Compute weighted kappa for ordinal dimensions and agreement rate for claim verdicts.
4. Discuss disagreements only after the frozen independent files are preserved.
5. Record the adjudicated label and reason separately; never rewrite the original labels.

## Evidence status

The repository ships an empty annotation template. Human-agreement metrics must not be reported until
two real completed label sets and adjudication notes are present.


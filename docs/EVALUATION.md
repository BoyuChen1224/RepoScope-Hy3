# RepoScope evaluation protocol

## Objective

The evaluator measures whether a repository adoption report is auditable and useful for a real
engineering decision. It does not attempt to prove that a repository is secure. The unit of review is
a report generated against one immutable repository commit.

## Deterministic rubric v1.1

Each dimension is scored from 0 to 4 using explicit thresholds.

| Dimension | Observable | Score thresholds |
| --- | --- | --- |
| Evidence traceability | Fraction of factual claims with at least one evidence reference | 4: >=95%; 3: >=80%; 2: >=60%; 1: >=30%; 0: <30% |
| Reference validity | Fraction of references whose file exists and line range is in bounds | Same thresholds |
| Quote grounding | Fraction of evidence quotes found in the captured source excerpt | Same thresholds |
| Uncertainty disclosure | Whether the report records information that the snapshot cannot establish | 4: at least one explicit unknown; 1: none, pending calibration |
| Recommendation actionability | Fraction of recommendations with both an action and verification method | Same thresholds |
| Format compliance | Validation against the versioned report schema | 4: schema-valid; invalid output is rejected before scoring |

The weighted score is normalized to 100. Evidence validity and quote grounding together contribute
43%, preventing fluent writing from dominating source quality. The score is capped at 59 if more than
20% of evidence references are invalid or quote grounding falls below 60%.

Version 1.1 removes display-only line-number prefixes from captured excerpts before exact quote
comparison. Paths and cited line ranges remain checked against the original document metadata.

## Validity experiments

1. **Discrimination:** score designed good, medium, and bad outputs for each frozen input. Report
   correct ordering rate, score distributions, and Spearman correlation with construction rank.
2. **Repeatability:** evaluate every output five times. The deterministic layer should have zero score
   variance; live semantic judging must report actual variance rather than inherit this claim.
3. **Adversarial resistance:** add professional verbosity, fabricated paths, real paths with false
   quotes, and unjustified certainty. Report attack detection per type.
4. **Human agreement (planned evidence):** two annotators independently label a blinded subset using
   claim-level entailment and report-level dimensions. Report weighted kappa or rank correlation and
   publish adjudication notes.
5. **Ablation (planned evidence):** compare rules-only, semantic-only, and hybrid variants on the same
   frozen cases.

## Semantic rubric v1.0

The optional `/api/evaluations/judge` endpoint asks Hy3 for four additional 0-4 dimensions: factual
accuracy, evidence entailment, material-risk completeness, and professional clarity. The judge sees a
blind frozen snapshot and a report, not generator metadata. Repository text is explicitly treated as
untrusted evidence to reduce prompt-injection risk.

This semantic score is advisory until calibrated against blinded human labels. Using the same model
family to generate and judge an answer can introduce correlated bias; the deterministic hard failures
therefore remain authoritative, and the UI must not silently replace them with a semantic score.

## Non-negotiable reporting rule

Skipped live calls, missing human labels, and unavailable sandbox execution are **unverified**, never
passed. Generated result files must name the evaluator version, sample count, and evidence boundary.

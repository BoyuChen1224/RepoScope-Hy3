from __future__ import annotations

import re

from .models import (
    DueDiligenceReport,
    EvaluationDimension,
    EvaluationResult,
    RepositoryManifest,
)


def _score_ratio(ratio: float) -> float:
    if ratio >= 0.95:
        return 4.0
    if ratio >= 0.80:
        return 3.0
    if ratio >= 0.60:
        return 2.0
    if ratio >= 0.30:
        return 1.0
    return 0.0


def _normalize_text(value: str) -> str:
    return " ".join(value.split()).casefold()


def _excerpt_source_text(excerpt: str) -> str:
    return "\n".join(re.sub(r"^\d+:\s?", "", line) for line in excerpt.splitlines())


def evaluate_report(manifest: RepositoryManifest, report: DueDiligenceReport) -> EvaluationResult:
    document_map = {document.path: document for document in manifest.documents}
    claims = report.claims
    cited_claims = sum(bool(claim.evidence) for claim in claims)
    total_refs = 0
    valid_refs = 0
    exact_quotes = 0
    invalid_details: list[str] = []

    for item in [*claims, *report.risks]:
        for ref in item.evidence:
            total_refs += 1
            document = document_map.get(ref.path)
            if not document:
                invalid_details.append(f"{item.id}: missing path {ref.path}")
                continue
            if ref.line_end > document.line_count:
                invalid_details.append(f"{item.id}: line range exceeds {ref.path}")
                continue
            valid_refs += 1
            normalized_quote = _normalize_text(ref.quote)
            normalized_excerpt = _normalize_text(_excerpt_source_text(document.excerpt))
            if normalized_quote and normalized_quote in normalized_excerpt:
                exact_quotes += 1

    traceability_ratio = cited_claims / len(claims) if claims else 0.0
    valid_ref_ratio = valid_refs / total_refs if total_refs else 0.0
    exact_quote_ratio = exact_quotes / total_refs if total_refs else 0.0
    actionable = sum(
        bool(rec.action.strip()) and bool(rec.verification.strip())
        for rec in report.recommendations
    )
    actionability_ratio = (
        actionable / len(report.recommendations) if report.recommendations else 0.0
    )
    uncertainty_score = 4.0 if report.unknowns else 1.0
    format_score = 4.0

    dimensions = [
        EvaluationDimension(
            key="traceability",
            label="Evidence traceability",
            score=_score_ratio(traceability_ratio),
            explanation=f"{cited_claims}/{len(claims)} factual claims include evidence.",
        ),
        EvaluationDimension(
            key="reference_validity",
            label="Reference validity",
            score=_score_ratio(valid_ref_ratio),
            explanation=(
                f"{valid_refs}/{total_refs} references point to an existing in-range source."
            ),
            evidence=invalid_details[:12],
        ),
        EvaluationDimension(
            key="quote_grounding",
            label="Quote grounding",
            score=_score_ratio(exact_quote_ratio),
            explanation=(
                f"{exact_quotes}/{total_refs} evidence quotes are found in captured excerpts."
            ),
        ),
        EvaluationDimension(
            key="uncertainty",
            label="Uncertainty disclosure",
            score=uncertainty_score,
            explanation=(
                f"The report records {len(report.unknowns)} explicit unknowns."
                if report.unknowns
                else "The report records no unknowns; this requires manual calibration review."
            ),
        ),
        EvaluationDimension(
            key="actionability",
            label="Recommendation actionability",
            score=_score_ratio(actionability_ratio),
            explanation=(
                f"{actionable}/{len(report.recommendations)} recommendations include both "
                "an action "
                "and a verification method."
            ),
        ),
        EvaluationDimension(
            key="schema",
            label="Format compliance",
            score=format_score,
            explanation="The output passed the versioned Pydantic report schema.",
        ),
    ]

    weights = {
        "traceability": 0.22,
        "reference_validity": 0.23,
        "quote_grounding": 0.20,
        "uncertainty": 0.12,
        "actionability": 0.13,
        "schema": 0.10,
    }
    total = round(sum(item.score / 4 * weights[item.key] * 100 for item in dimensions), 2)
    hard_failures: list[str] = []
    if total_refs and valid_ref_ratio < 0.8:
        hard_failures.append("More than 20% of evidence references are invalid.")
    if exact_quote_ratio < 0.6:
        hard_failures.append("Evidence quote grounding is below 60%.")
    if hard_failures:
        total = min(total, 59.0)

    grade = "A" if total >= 85 else "B" if total >= 70 else "C" if total >= 60 else "D"
    return EvaluationResult(
        total_score=total,
        grade=grade,
        dimensions=dimensions,
        hard_failures=hard_failures,
        diagnostics={
            "claim_count": len(claims),
            "reference_count": total_refs,
            "traceability_ratio": round(traceability_ratio, 4),
            "valid_reference_ratio": round(valid_ref_ratio, 4),
            "exact_quote_ratio": round(exact_quote_ratio, 4),
        },
    )

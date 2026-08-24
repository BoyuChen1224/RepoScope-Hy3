from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl, model_validator


class Decision(StrEnum):
    RECOMMEND = "recommend"
    CONDITIONAL = "conditional"
    DO_NOT_RECOMMEND = "do_not_recommend"


class EvidenceRef(BaseModel):
    path: str = Field(min_length=1)
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    quote: str = Field(min_length=1, max_length=1200)

    @model_validator(mode="after")
    def valid_range(self) -> EvidenceRef:
        if self.line_end < self.line_start:
            raise ValueError("line_end must not be smaller than line_start")
        return self


class EvidenceDocument(BaseModel):
    path: str
    sha256: str
    size_bytes: int = Field(ge=0)
    line_count: int = Field(ge=0)
    excerpt: str = ""
    tags: list[str] = Field(default_factory=list)


class RepositoryManifest(BaseModel):
    source_url: str
    commit_sha: str
    default_branch: str = ""
    inspected_at: str
    goal: str
    file_count: int = Field(ge=0)
    total_size_bytes: int = Field(ge=0)
    languages: dict[str, int] = Field(default_factory=dict)
    signals: dict[str, bool | int | str | list[str]] = Field(default_factory=dict)
    documents: list[EvidenceDocument] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Claim(BaseModel):
    id: str = Field(pattern=r"^C\d{3}$")
    category: str
    text: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class Risk(BaseModel):
    id: str = Field(pattern=r"^R\d{3}$")
    severity: str = Field(pattern=r"^(low|medium|high|critical)$")
    title: str
    description: str
    evidence: list[EvidenceRef] = Field(default_factory=list)


class Recommendation(BaseModel):
    title: str
    action: str
    verification: str
    related_paths: list[str] = Field(default_factory=list)


class DueDiligenceReport(BaseModel):
    report_version: str = "1.0"
    repository: str
    commit_sha: str
    analysis_goal: str
    executive_summary: str
    decision: Decision
    decision_confidence: float = Field(ge=0, le=1)
    claims: list[Claim]
    risks: list[Risk]
    recommendations: list[Recommendation]
    unknowns: list[str] = Field(default_factory=list)


class InspectRequest(BaseModel):
    repository_url: HttpUrl
    goal: str = Field(
        default="Assess whether this repository is suitable for production adoption.",
        min_length=10,
        max_length=500,
    )


class GenerateRequest(BaseModel):
    manifest: RepositoryManifest


class EvaluationDimension(BaseModel):
    key: str
    label: str
    score: float = Field(ge=0, le=4)
    explanation: str
    evidence: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    evaluator_version: str = "1.0"
    total_score: float = Field(ge=0, le=100)
    grade: str
    dimensions: list[EvaluationDimension]
    hard_failures: list[str] = Field(default_factory=list)
    diagnostics: dict[str, float | int | str] = Field(default_factory=dict)


class EvaluateRequest(BaseModel):
    manifest: RepositoryManifest
    report: DueDiligenceReport

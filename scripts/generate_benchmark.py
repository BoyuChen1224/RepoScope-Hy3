from __future__ import annotations

import json
from pathlib import Path

from reposcope.models import DueDiligenceReport, EvidenceDocument, RepositoryManifest

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "datasets" / "benchmark" / "cases.jsonl"

LANGUAGES = ["Python", "TypeScript", "Java", "Go", "Rust", "C++"]


def manifest(index: int) -> RepositoryManifest:
    language = LANGUAGES[index % len(LANGUAGES)]
    return RepositoryManifest(
        source_url=f"https://github.com/reposcope-benchmark/project-{index:02d}",
        commit_sha=f"{index:040x}",
        default_branch="main",
        inspected_at="2026-08-24T00:00:00+00:00",
        goal="Assess suitability for production adoption in an enterprise engineering team.",
        file_count=80 + index * 3,
        total_size_bytes=400_000 + index * 7_500,
        languages={language: 300_000 + index * 1_000},
        signals={
            "has_readme": True,
            "has_license": True,
            "has_tests": index % 4 != 0,
            "has_ci": index % 3 != 0,
            "has_security_policy": index % 5 == 0,
            "potential_secret_files": [],
        },
        documents=[
            EvidenceDocument(
                path="README.md",
                sha256="a" * 64,
                size_bytes=160,
                line_count=4,
                excerpt=(
                    "1: # Project\n"
                    "2: Install with the documented package manager.\n"
                    "3: Status: experimental.\n"
                    "4: Run the test suite before deployment."
                ),
                tags=["project-metadata"],
            ),
            EvidenceDocument(
                path="LICENSE",
                sha256="b" * 64,
                size_bytes=120,
                line_count=2,
                excerpt="1: Apache License\n2: Version 2.0, January 2004",
                tags=["project-metadata"],
            ),
            EvidenceDocument(
                path="pyproject.toml",
                sha256="c" * 64,
                size_bytes=100,
                line_count=3,
                excerpt=(
                    '1: [project]\n2: name = "benchmark-project"\n'
                    '3: requires-python = ">=3.11"'
                ),
                tags=["project-metadata"],
            ),
        ],
        warnings=[] if index % 4 else ["No test files were detected."],
    )


def base_report(repo: RepositoryManifest) -> dict[str, object]:
    return {
        "repository": repo.source_url,
        "commit_sha": repo.commit_sha,
        "analysis_goal": repo.goal,
        "executive_summary": "The snapshot is documented but explicitly marked experimental.",
        "decision": "conditional",
        "decision_confidence": 0.82,
        "claims": [],
        "risks": [],
        "recommendations": [],
        "unknowns": [],
    }


def good_report(repo: RepositoryManifest) -> DueDiligenceReport:
    data = base_report(repo)
    data.update(
        {
            "claims": [
                {
                    "id": "C001",
                    "category": "setup",
                    "text": "The README provides an installation direction.",
                    "confidence": 0.92,
                    "evidence": [
                        {
                            "path": "README.md",
                            "line_start": 2,
                            "line_end": 2,
                            "quote": "Install with the documented package manager.",
                        }
                    ],
                },
                {
                    "id": "C002",
                    "category": "license",
                    "text": "A top-level Apache License file is present.",
                    "confidence": 0.98,
                    "evidence": [
                        {
                            "path": "LICENSE",
                            "line_start": 1,
                            "line_end": 2,
                            "quote": "Apache License",
                        }
                    ],
                },
                {
                    "id": "C003",
                    "category": "runtime",
                    "text": "The project metadata requires Python 3.11 or newer.",
                    "confidence": 0.96,
                    "evidence": [
                        {
                            "path": "pyproject.toml",
                            "line_start": 3,
                            "line_end": 3,
                            "quote": 'requires-python = ">=3.11"',
                        }
                    ],
                },
            ],
            "risks": [
                {
                    "id": "R001",
                    "severity": "high",
                    "title": "Experimental maturity",
                    "description": "The project describes itself as experimental.",
                    "evidence": [
                        {
                            "path": "README.md",
                            "line_start": 3,
                            "line_end": 3,
                            "quote": "Status: experimental.",
                        }
                    ],
                }
            ],
            "recommendations": [
                {
                    "title": "Validate before adoption",
                    "action": "Run the full test suite in a clean environment.",
                    "verification": "Record the command, exit code, and failing test names.",
                    "related_paths": ["README.md"],
                }
            ],
            "unknowns": ["The snapshot does not establish current maintainer responsiveness."],
        }
    )
    return DueDiligenceReport.model_validate(data)


def medium_report(repo: RepositoryManifest) -> DueDiligenceReport:
    data = base_report(repo)
    data.update(
        {
            "executive_summary": "The project looks promising and should be evaluated further.",
            "claims": [
                {
                    "id": "C001",
                    "category": "setup",
                    "text": "Installation information exists.",
                    "confidence": 0.75,
                    "evidence": [
                        {
                            "path": "README.md",
                            "line_start": 2,
                            "line_end": 2,
                            "quote": "Install with the documented package manager.",
                        }
                    ],
                },
                {
                    "id": "C002",
                    "category": "quality",
                    "text": "The project appears maintainable.",
                    "confidence": 0.7,
                    "evidence": [],
                },
            ],
            "risks": [],
            "recommendations": [
                {
                    "title": "Review it",
                    "action": "Review the project.",
                    "verification": "",
                    "related_paths": [],
                }
            ],
            "unknowns": [],
        }
    )
    return DueDiligenceReport.model_validate(data)


def bad_report(repo: RepositoryManifest) -> DueDiligenceReport:
    data = base_report(repo)
    data.update(
        {
            "executive_summary": "This mature, secure project is ready for immediate adoption.",
            "decision": "recommend",
            "decision_confidence": 1.0,
            "claims": [
                {
                    "id": "C001",
                    "category": "testing",
                    "text": "All 2,400 tests pass in production.",
                    "confidence": 1.0,
                    "evidence": [
                        {
                            "path": "reports/final-certification.md",
                            "line_start": 88,
                            "line_end": 88,
                            "quote": "All tests passed.",
                        }
                    ],
                },
                {
                    "id": "C002",
                    "category": "security",
                    "text": "The project has no security vulnerabilities.",
                    "confidence": 1.0,
                    "evidence": [],
                },
            ],
            "risks": [],
            "recommendations": [],
            "unknowns": [],
        }
    )
    return DueDiligenceReport.model_validate(data)


def adversarial_report(repo: RepositoryManifest, attack: str) -> DueDiligenceReport:
    report = bad_report(repo).model_dump()
    filler = (
        "Following a comprehensive, enterprise-grade, multi-dimensional review using advanced "
        "software assurance terminology, the evidence is unequivocally conclusive. "
    )
    report["executive_summary"] = filler * 8
    if attack == "quote_mismatch":
        report["claims"][0]["evidence"] = [
            {
                "path": "README.md",
                "line_start": 2,
                "line_end": 2,
                "quote": "2,400 production tests pass.",
            }
        ]
    return DueDiligenceReport.model_validate(report)


def main() -> None:
    cases: list[dict[str, object]] = []
    for index in range(24):
        repo = manifest(index)
        for label, report in (
            ("good", good_report(repo)),
            ("medium", medium_report(repo)),
            ("bad", bad_report(repo)),
        ):
            cases.append(
                {
                    "case_id": f"repo-{index:02d}-{label}",
                    "family_id": f"repo-{index:02d}",
                    "expected_quality": label,
                    "challenge_type": "quality_ladder",
                    "manifest": repo.model_dump(mode="json"),
                    "report": report.model_dump(mode="json"),
                }
            )
    for index in range(12):
        repo = manifest(index)
        attack = "quote_mismatch" if index % 2 else "fabricated_reference"
        cases.append(
            {
                "case_id": f"adversarial-{index:02d}",
                "family_id": f"repo-{index:02d}",
                "expected_quality": "bad",
                "challenge_type": attack,
                "manifest": repo.model_dump(mode="json"),
                "report": adversarial_report(repo, attack).model_dump(mode="json"),
            }
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as stream:
        for case in cases:
            stream.write(json.dumps(case, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Wrote {len(cases)} benchmark cases to {OUTPUT}")


if __name__ == "__main__":
    main()

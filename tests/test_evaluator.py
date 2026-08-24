from reposcope.evaluator import evaluate_report
from reposcope.models import DueDiligenceReport, EvidenceDocument, RepositoryManifest


def test_evaluator_rewards_valid_grounded_report() -> None:
    manifest = RepositoryManifest(
        source_url="https://github.com/example/project",
        commit_sha="a" * 40,
        inspected_at="2026-08-24T00:00:00+00:00",
        goal="Assess production adoption.",
        file_count=1,
        total_size_bytes=30,
        documents=[
            EvidenceDocument(
                path="README.md",
                sha256="b" * 64,
                size_bytes=30,
                line_count=3,
                excerpt="1: # Demo\n2: Run pytest.\n3: Apache-2.0",
            )
        ],
    )
    report = DueDiligenceReport.model_validate(
        {
            "repository": manifest.source_url,
            "commit_sha": manifest.commit_sha,
            "analysis_goal": manifest.goal,
            "executive_summary": "The project documents its test command.",
            "decision": "conditional",
            "decision_confidence": 0.8,
            "claims": [
                {
                    "id": "C001",
                    "category": "testing",
                    "text": "The README tells users to run pytest.",
                    "confidence": 0.95,
                    "evidence": [
                        {
                            "path": "README.md",
                            "line_start": 2,
                            "line_end": 2,
                            "quote": "Run pytest.",
                        }
                    ],
                }
            ],
            "risks": [],
            "recommendations": [
                {
                    "title": "Run tests",
                    "action": "Execute pytest before adoption.",
                    "verification": "Confirm pytest exits with code 0.",
                    "related_paths": ["README.md"],
                }
            ],
            "unknowns": ["CI status is not available in the snapshot."],
        }
    )

    result = evaluate_report(manifest, report)

    assert result.total_score >= 85
    assert not result.hard_failures


def test_evaluator_caps_fabricated_references() -> None:
    manifest = RepositoryManifest(
        source_url="https://github.com/example/project",
        commit_sha="a" * 40,
        inspected_at="2026-08-24T00:00:00+00:00",
        goal="Assess production adoption.",
        file_count=0,
        total_size_bytes=0,
    )
    report = DueDiligenceReport.model_validate(
        {
            "repository": manifest.source_url,
            "commit_sha": manifest.commit_sha,
            "analysis_goal": manifest.goal,
            "executive_summary": "Unsupported.",
            "decision": "recommend",
            "decision_confidence": 1,
            "claims": [
                {
                    "id": "C001",
                    "category": "testing",
                    "text": "All tests pass.",
                    "confidence": 1,
                    "evidence": [
                        {
                            "path": "FAKE.md",
                            "line_start": 1,
                            "line_end": 1,
                            "quote": "All tests pass.",
                        }
                    ],
                }
            ],
            "risks": [],
            "recommendations": [],
            "unknowns": [],
        }
    )

    result = evaluate_report(manifest, report)

    assert result.total_score <= 59
    assert result.hard_failures

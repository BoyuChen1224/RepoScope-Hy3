import pytest
from fastapi.testclient import TestClient

from reposcope.app import app
from reposcope.models import SemanticEvaluationResult

client = TestClient(app)


def test_health_and_home() -> None:
    health = client.get("/api/health")
    home = client.get("/")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert home.status_code == 200
    assert "RepoScope Hy3" in home.text
    assert 'data-lang="zh"' in home.text
    assert 'data-lang="en"' in home.text
    assert 'id="themeToggle"' in home.text

    icon_styles = client.get("/assets/vendor/phosphor/style.css")
    icon_font = client.get("/assets/vendor/phosphor/Phosphor.woff2")
    app_script = client.get("/assets/app.js")

    assert icon_styles.status_code == 200
    assert icon_font.status_code == 200
    assert app_script.status_code == 200
    assert "reposcope-language" in app_script.text
    assert "reposcope-theme" in app_script.text
    assert 'let currentTheme = "light"' in app_script.text


def test_inspect_rejects_non_allowlisted_host() -> None:
    response = client.post(
        "/api/repositories/inspect",
        json={
            "repository_url": "https://example.org/owner/repository",
            "goal": "Assess whether this repository is suitable for production adoption.",
        },
    )

    assert response.status_code == 422
    assert "allowlist" in response.json()["detail"]


def test_semantic_judge_endpoint_returns_advisory_dimensions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = SemanticEvaluationResult.model_validate(
        {
            "dimensions": [
                {
                    "key": "factual_accuracy",
                    "label": "Factual accuracy",
                    "score": 4,
                    "explanation": "The cited claim is supported.",
                }
            ],
            "claim_judgements": [
                {
                    "claim_id": "C001",
                    "verdict": "supported",
                    "explanation": "The source says the same thing.",
                }
            ],
        }
    )
    monkeypatch.setattr(
        "reposcope.app.Hy3SemanticEvaluator.evaluate",
        lambda self, manifest, report: expected,
    )
    payload = {
        "manifest": {
            "source_url": "https://github.com/example/project",
            "commit_sha": "a" * 40,
            "inspected_at": "2026-08-24T00:00:00+00:00",
            "goal": "Assess production adoption.",
            "file_count": 1,
            "total_size_bytes": 20,
        },
        "report": {
            "repository": "https://github.com/example/project",
            "commit_sha": "a" * 40,
            "analysis_goal": "Assess production adoption.",
            "executive_summary": "The snapshot is incomplete.",
            "decision": "conditional",
            "decision_confidence": 0.7,
            "claims": [
                {
                    "id": "C001",
                    "category": "documentation",
                    "text": "A README exists.",
                    "confidence": 0.9,
                    "evidence": [],
                }
            ],
            "risks": [],
            "recommendations": [],
            "unknowns": ["Runtime behavior is unknown."],
        },
    }

    response = client.post("/api/evaluations/judge", json=payload)

    assert response.status_code == 200
    assert response.json()["dimensions"][0]["key"] == "factual_accuracy"

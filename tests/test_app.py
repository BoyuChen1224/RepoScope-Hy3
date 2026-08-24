from fastapi.testclient import TestClient

from reposcope.app import app

client = TestClient(app)


def test_health_and_home() -> None:
    health = client.get("/api/health")
    home = client.get("/")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert home.status_code == 200
    assert "RepoScope Hy3" in home.text


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

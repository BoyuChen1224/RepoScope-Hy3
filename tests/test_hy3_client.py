import json
from types import SimpleNamespace

from reposcope.hy3_client import (
    Hy3ReportGenerator,
    _compact_manifest,
    _extract_json,
    _parse_report,
)
from reposcope.models import EvidenceDocument, RepositoryManifest


def test_extract_json_accepts_plain_and_fenced_payloads() -> None:
    assert _extract_json('{"ok":true}') == '{"ok":true}'
    assert _extract_json('```json\n{"ok":true}\n```') == '{"ok":true}'


def test_compact_manifest_prioritizes_tagged_documents_within_budget() -> None:
    manifest = RepositoryManifest(
        source_url="https://github.com/example/project",
        commit_sha="a" * 40,
        inspected_at="2026-08-24T00:00:00+00:00",
        goal="Assess production adoption.",
        file_count=2,
        total_size_bytes=20_000,
        documents=[
            EvidenceDocument(
                path="src/large.py",
                sha256="b" * 64,
                size_bytes=10_000,
                line_count=100,
                excerpt="x" * 10_000,
            ),
            EvidenceDocument(
                path="README.md",
                sha256="c" * 64,
                size_bytes=10_000,
                line_count=100,
                excerpt="important " * 2_000,
                tags=["project-metadata"],
            ),
        ],
    )

    compact = _compact_manifest(manifest, max_chars=10_000)

    assert compact["documents"][0]["path"] == "README.md"
    assert compact["context_budget"]["included_excerpt_characters"] <= 10_000


def test_parse_report_accepts_explicit_report_wrapper() -> None:
    payload = {
        "repository": "metadata outside wrapper",
        "report": {
            "repository": "https://github.com/example/project",
            "commit_sha": "a" * 40,
            "analysis_goal": "Assess production adoption.",
            "executive_summary": "Evidence is incomplete.",
            "decision": "conditional",
            "decision_confidence": 0.7,
            "claims": [],
            "risks": [],
            "recommendations": [],
            "unknowns": ["Runtime behavior is not established."],
        },
    }

    report = _parse_report(__import__("json").dumps(payload))

    assert report.commit_sha == "a" * 40


def test_generator_repairs_a_schema_drift_response_once() -> None:
    invalid = json.dumps(
        {
            "repository": "https://github.com/example/project",
            "commit_sha": "a" * 40,
            "goal": "Assess production adoption.",
            "findings": [],
            "risks": [],
            "recommendations": [],
            "unknowns": [],
        }
    )
    valid = json.dumps(
        {
            "repository": "https://github.com/example/project",
            "commit_sha": "a" * 40,
            "analysis_goal": "Assess production adoption.",
            "executive_summary": "Evidence is incomplete.",
            "decision": "conditional",
            "decision_confidence": 0.7,
            "claims": [],
            "risks": [],
            "recommendations": [],
            "unknowns": ["Runtime behavior is not established."],
        }
    )
    responses = iter([invalid, valid])
    calls: list[dict[str, object]] = []

    def create(**kwargs: object) -> SimpleNamespace:
        calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=next(responses)))]
        )

    generator = object.__new__(Hy3ReportGenerator)
    generator.settings = SimpleNamespace(
        hy3_model="hy3-test",
        hy3_enable_reasoning_effort=False,
        hy3_enable_json_response_format=False,
        reposcope_max_context_chars=10_000,
    )
    generator.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )
    manifest = RepositoryManifest(
        source_url="https://github.com/example/project",
        commit_sha="a" * 40,
        inspected_at="2026-08-24T00:00:00+00:00",
        goal="Assess production adoption.",
        file_count=0,
        total_size_bytes=0,
    )

    report = generator.generate(manifest)

    assert report.analysis_goal == manifest.goal
    assert len(calls) == 2
    repair_request = json.loads(calls[1]["messages"][-1]["content"])
    assert "claims" in repair_request["required_top_level_fields"]
    assert repair_request["task"].startswith("Repair")

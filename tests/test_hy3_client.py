from reposcope.hy3_client import _compact_manifest, _extract_json
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

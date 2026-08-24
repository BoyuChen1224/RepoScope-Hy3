from pathlib import Path

import pytest

from reposcope.config import Settings
from reposcope.inspector import InspectionError, inspect_worktree, validate_repository_url


def test_repository_url_allowlist() -> None:
    assert (
        validate_repository_url("https://github.com/example/project", ("github.com",))
        == "https://github.com/example/project"
    )
    with pytest.raises(InspectionError):
        validate_repository_url("http://127.0.0.1/repo", ("github.com",))
    with pytest.raises(InspectionError):
        validate_repository_url("https://github.com@example.org/repo", ("github.com",))


def test_inspect_worktree_collects_core_signals(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Demo\nRun pytest.\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("Apache License 2.0\n", encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_demo.py").write_text("def test_ok(): assert True\n", encoding="utf-8")
    ignored = tmp_path / ".venv"
    ignored.mkdir()
    (ignored / "secret.py").write_text("print('not project evidence')\n", encoding="utf-8")
    (tmp_path / ".env").write_text("HY3_API_KEY=do-not-collect\n", encoding="utf-8")

    manifest = inspect_worktree(
        tmp_path,
        "https://github.com/example/project",
        "a" * 40,
        "main",
        "Assess production adoption.",
        Settings(),
    )

    assert manifest.file_count == 3
    assert manifest.signals["has_readme"] is True
    assert manifest.signals["has_license"] is True
    assert manifest.signals["has_tests"] is True
    assert {doc.path for doc in manifest.documents} >= {"README.md", "LICENSE"}

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from .config import Settings
from .models import EvidenceDocument, RepositoryManifest

TEXT_SUFFIXES = {
    ".c",
    ".cpp",
    ".css",
    ".go",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".md",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}

IMPORTANT_NAMES = {
    "readme.md",
    "readme_cn.md",
    "license",
    "license.md",
    "copying",
    "pyproject.toml",
    "package.json",
    "requirements.txt",
    "cargo.toml",
    "go.mod",
    "pom.xml",
    "dockerfile",
    "docker-compose.yml",
    "compose.yml",
    "security.md",
    "contributing.md",
}

LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".c": "C",
    ".rb": "Ruby",
    ".php": "PHP",
}

SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)

IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".reposcope",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "build",
    "dist",
    "node_modules",
    "tmp",
    "vendor",
}


class InspectionError(RuntimeError):
    pass


def validate_repository_url(raw_url: str, allowed_hosts: tuple[str, ...]) -> str:
    parsed = urlparse(raw_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise InspectionError("Only explicit HTTPS repository URLs are accepted.")
    host = parsed.hostname.lower()
    if host not in allowed_hosts:
        raise InspectionError(f"Repository host '{host}' is not in the allowlist.")
    if parsed.username or parsed.password or parsed.port:
        raise InspectionError("Credentials and custom ports are not accepted in repository URLs.")
    clean_path = parsed.path.rstrip("/")
    if not re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?", clean_path):
        raise InspectionError("Expected a public repository URL in owner/repository form.")
    return f"https://{host}{clean_path}"


def _run_git(args: list[str], cwd: Path | None, timeout: int) -> str:
    git_executable = shutil.which("git")
    if not git_executable:
        raise InspectionError("Git is required for repository inspection.")
    # All call sites supply fixed arguments or a URL that passed the strict GitHub allowlist.
    result = subprocess.run(  # noqa: S603
        [git_executable, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "git failed"
        raise InspectionError(message)
    return result.stdout.strip()


def clone_public_repository(url: str, settings: Settings) -> tuple[Path, str, str]:
    safe_url = validate_repository_url(url, settings.reposcope_allowed_git_hosts)
    worktree = Path(tempfile.mkdtemp(prefix="reposcope-"))
    try:
        _run_git(
            [
                "clone",
                "--depth",
                "1",
                "--filter=blob:limit=2m",
                "--no-tags",
                safe_url,
                str(worktree),
            ],
            cwd=None,
            timeout=settings.reposcope_clone_timeout_seconds,
        )
        sha = _run_git(["rev-parse", "HEAD"], cwd=worktree, timeout=10)
        branch = _run_git(["branch", "--show-current"], cwd=worktree, timeout=10)
        return worktree, sha, branch
    except Exception:
        shutil.rmtree(worktree, ignore_errors=True)
        raise


def _safe_text(path: Path, limit: int = 24000) -> str:
    try:
        data = path.read_bytes()[:limit]
        if b"\x00" in data:
            return ""
        return data.decode("utf-8", errors="replace")
    except OSError:
        return ""


def _document_tags(relative: str) -> list[str]:
    lower = relative.lower().replace("\\", "/")
    tags: list[str] = []
    if Path(lower).name in IMPORTANT_NAMES:
        tags.append("project-metadata")
    if "test" in lower or "spec" in lower:
        tags.append("test")
    if lower.startswith(".github/workflows/"):
        tags.append("ci")
    if "security" in lower:
        tags.append("security")
    return tags


def inspect_worktree(
    root: Path,
    source_url: str,
    commit_sha: str,
    default_branch: str,
    goal: str,
    settings: Settings,
) -> RepositoryManifest:
    documents: list[EvidenceDocument] = []
    languages: Counter[str] = Counter()
    total_size = 0
    file_count = 0
    suspicious_secret_files: list[str] = []
    has_tests = False
    has_ci = False
    has_license = False
    has_readme = False
    has_security_policy = False

    paths: list[Path] = []
    for current_root, directories, files in os.walk(root, followlinks=False):
        directories[:] = [
            name
            for name in directories
            if name not in IGNORED_DIRECTORIES and not (Path(current_root) / name).is_symlink()
        ]
        paths.extend(
            Path(current_root) / filename
            for filename in files
            if filename == ".env.example" or not filename.startswith(".env")
        )

    for path in paths:
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        try:
            size = path.stat().st_size
        except OSError:
            continue
        file_count += 1
        total_size += size
        if total_size > settings.reposcope_max_repo_mb * 1024 * 1024:
            raise InspectionError("Repository exceeds the configured inspection size limit.")

        suffix = path.suffix.lower()
        if suffix in LANGUAGE_BY_SUFFIX:
            languages[LANGUAGE_BY_SUFFIX[suffix]] += size

        lower = relative.lower()
        name = path.name.lower()
        has_tests = has_tests or "test" in lower or "spec" in lower
        has_ci = has_ci or lower.startswith(".github/workflows/")
        has_license = has_license or name in {"license", "license.md", "copying"}
        has_readme = has_readme or name.startswith("readme")
        has_security_policy = has_security_policy or name == "security.md"

        is_relevant = (
            name in IMPORTANT_NAMES
            or suffix in TEXT_SUFFIXES
            and (size <= 120_000 and (len(documents) < 160 or _document_tags(relative)))
        )
        if not is_relevant:
            continue
        text = _safe_text(path)
        if not text:
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            suspicious_secret_files.append(relative)
        lines = text.splitlines()
        excerpt = "\n".join(f"{index + 1}: {line}" for index, line in enumerate(lines[:220]))
        documents.append(
            EvidenceDocument(
                path=relative,
                sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                size_bytes=size,
                line_count=len(lines),
                excerpt=excerpt,
                tags=_document_tags(relative),
            )
        )

    warnings: list[str] = []
    if not has_readme:
        warnings.append("No README file was found.")
    if not has_license:
        warnings.append("No top-level license file was found.")
    if suspicious_secret_files:
        warnings.append("Potential committed secret patterns require manual review.")

    return RepositoryManifest(
        source_url=source_url,
        commit_sha=commit_sha,
        default_branch=default_branch,
        inspected_at=datetime.now(UTC).isoformat(),
        goal=goal,
        file_count=file_count,
        total_size_bytes=total_size,
        languages=dict(languages.most_common()),
        signals={
            "has_readme": has_readme,
            "has_license": has_license,
            "has_tests": has_tests,
            "has_ci": has_ci,
            "has_security_policy": has_security_policy,
            "potential_secret_files": suspicious_secret_files,
        },
        documents=documents,
        warnings=warnings,
    )


def inspect_repository(url: str, goal: str, settings: Settings) -> RepositoryManifest:
    worktree, sha, branch = clone_public_repository(url, settings)
    try:
        return inspect_worktree(worktree, url, sha, branch, goal, settings)
    finally:
        shutil.rmtree(worktree, ignore_errors=True)

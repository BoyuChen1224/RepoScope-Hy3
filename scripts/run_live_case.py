from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from reposcope.config import Settings
from reposcope.evaluator import evaluate_report
from reposcope.hy3_client import Hy3ReportGenerator
from reposcope.inspector import inspect_worktree
from reposcope.semantic_evaluator import Hy3SemanticEvaluator

ROOT = Path(__file__).resolve().parents[1]


def git_output(root: Path, *args: str) -> str:
    git_executable = shutil.which("git")
    if not git_executable:
        raise RuntimeError("Git is required for the live case.")
    result = subprocess.run(  # noqa: S603
        [git_executable, *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        shell=False,
    )
    return result.stdout.strip()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one frozen live RepoScope Hy3 case.")
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--source-url", default="https://github.com/BoyuChen1224/RepoScope-Hy3")
    parser.add_argument(
        "--goal",
        default=("评估 RepoScope Hy3 是否适合作为企业研发团队进行开源项目采用前技术尽调的工具。"),
    )
    parser.add_argument("--semantic-runs", type=int, default=3)
    parser.add_argument("--max-context-chars", type=int, default=80_000)
    args = parser.parse_args()

    repo = args.repo.resolve()
    if git_output(repo, "status", "--porcelain"):
        raise SystemExit("Refusing live evaluation: commit or stash working-tree changes first.")
    commit_sha = git_output(repo, "rev-parse", "HEAD")
    branch = git_output(repo, "branch", "--show-current")
    settings = Settings()
    if not settings.hy3_api_key or settings.hy3_api_key == "EMPTY":
        raise SystemExit("HY3_API_KEY is not configured in .env.")
    settings.reposcope_max_context_chars = args.max_context_chars

    output = repo / "results" / "live" / commit_sha[:12]
    output.mkdir(parents=True, exist_ok=True)
    manifest = inspect_worktree(repo, args.source_url, commit_sha, branch, args.goal, settings)
    write_json(output / "manifest.json", manifest.model_dump(mode="json"))

    started = time.perf_counter()
    report = Hy3ReportGenerator(settings).generate(manifest)
    generation_seconds = time.perf_counter() - started
    write_json(output / "report.json", report.model_dump(mode="json"))

    deterministic = evaluate_report(manifest, report)
    write_json(output / "deterministic_evaluation.json", deterministic.model_dump(mode="json"))

    semantic_runs = []
    semantic_latencies = []
    judge = Hy3SemanticEvaluator(settings)
    for index in range(args.semantic_runs):
        started = time.perf_counter()
        result = judge.evaluate(manifest, report)
        semantic_latencies.append(time.perf_counter() - started)
        semantic_runs.append(result)
        write_json(output / f"semantic_evaluation_{index + 1}.json", result.model_dump(mode="json"))

    dimension_scores: dict[str, list[float]] = {}
    for result in semantic_runs:
        for dimension in result.dimensions:
            dimension_scores.setdefault(dimension.key, []).append(dimension.score)
    semantic_stability = {
        key: {
            "scores": values,
            "mean": round(statistics.mean(values), 4),
            "population_stddev": round(statistics.pstdev(values), 4),
        }
        for key, values in dimension_scores.items()
    }
    summary = {
        "case_version": "live-1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "repository": args.source_url,
        "commit_sha": commit_sha,
        "model": settings.hy3_model,
        "reasoning_effort_enabled": settings.hy3_enable_reasoning_effort,
        "context_character_budget": settings.reposcope_max_context_chars,
        "generation_seconds": round(generation_seconds, 3),
        "deterministic_evaluator_version": deterministic.evaluator_version,
        "deterministic_total_score": deterministic.total_score,
        "deterministic_grade": deterministic.grade,
        "deterministic_hard_failures": deterministic.hard_failures,
        "semantic_runs": len(semantic_runs),
        "semantic_latency_seconds": [round(value, 3) for value in semantic_latencies],
        "semantic_dimension_stability": semantic_stability,
        "evidence_boundary": (
            "One live self-repository case. Semantic judging uses the same model family and is "
            "not a substitute for blinded human agreement."
        ),
    }
    write_json(output / "live_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

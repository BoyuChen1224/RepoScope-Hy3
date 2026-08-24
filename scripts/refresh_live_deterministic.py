from __future__ import annotations

import argparse
import json
from pathlib import Path

from reposcope.evaluator import evaluate_report
from reposcope.models import DueDiligenceReport, RepositoryManifest

ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh deterministic scoring for a live case.")
    parser.add_argument("case_dir", nargs="?", type=Path)
    args = parser.parse_args()
    if args.case_dir:
        case_dir = args.case_dir
    else:
        candidates = [path.parent for path in (ROOT / "results" / "live").glob("*/report.json")]
        if not candidates:
            raise SystemExit("No live report exists.")
        case_dir = max(candidates, key=lambda path: path.stat().st_mtime)

    manifest = RepositoryManifest.model_validate_json(
        (case_dir / "manifest.json").read_text(encoding="utf-8")
    )
    report = DueDiligenceReport.model_validate_json(
        (case_dir / "report.json").read_text(encoding="utf-8")
    )
    result = evaluate_report(manifest, report)
    write_json(case_dir / "deterministic_evaluation.json", result.model_dump(mode="json"))

    summary_path = case_dir / "live_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary.update(
        {
            "deterministic_evaluator_version": result.evaluator_version,
            "deterministic_total_score": result.total_score,
            "deterministic_grade": result.grade,
            "deterministic_hard_failures": result.hard_failures,
        }
    )
    write_json(summary_path, summary)
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

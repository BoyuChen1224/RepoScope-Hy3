from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

from reposcope.evaluator import evaluate_report
from reposcope.models import DueDiligenceReport, RepositoryManifest

ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "datasets" / "benchmark" / "cases.jsonl"
RESULTS_PATH = ROOT / "results" / "evaluation_results.csv"
SUMMARY_PATH = ROOT / "results" / "experiment_summary.json"
REPORT_PATH = ROOT / "reports" / "benchmark_analysis.md"

QUALITY_RANK = {"bad": 0, "medium": 1, "good": 2}


def _spearman(xs: list[float], ys: list[float]) -> float:
    def ranks(values: list[float]) -> list[float]:
        ordered = sorted(range(len(values)), key=values.__getitem__)
        result = [0.0] * len(values)
        index = 0
        while index < len(ordered):
            end = index
            while end + 1 < len(ordered) and values[ordered[end + 1]] == values[ordered[index]]:
                end += 1
            rank = (index + end) / 2 + 1
            for position in range(index, end + 1):
                result[ordered[position]] = rank
            index = end + 1
        return result

    rx, ry = ranks(xs), ranks(ys)
    mean_x, mean_y = statistics.mean(rx), statistics.mean(ry)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(rx, ry, strict=True))
    denominator = (sum((x - mean_x) ** 2 for x in rx) * sum((y - mean_y) ** 2 for y in ry)) ** 0.5
    return numerator / denominator if denominator else 0.0


def main() -> None:
    cases = [json.loads(line) for line in CASES_PATH.read_text(encoding="utf-8").splitlines()]
    rows: list[dict[str, object]] = []
    repeated_stddevs: list[float] = []
    family_scores: dict[str, dict[str, float]] = defaultdict(dict)

    for case in cases:
        manifest = RepositoryManifest.model_validate(case["manifest"])
        report = DueDiligenceReport.model_validate(case["report"])
        repeated = [evaluate_report(manifest, report).total_score for _ in range(5)]
        result = evaluate_report(manifest, report)
        repeated_stddevs.append(statistics.pstdev(repeated))
        if case["challenge_type"] == "quality_ladder":
            family_scores[case["family_id"]][case["expected_quality"]] = result.total_score
        rows.append(
            {
                "case_id": case["case_id"],
                "family_id": case["family_id"],
                "expected_quality": case["expected_quality"],
                "challenge_type": case["challenge_type"],
                "score": result.total_score,
                "grade": result.grade,
                "hard_failure_count": len(result.hard_failures),
                "repeat_stddev": statistics.pstdev(repeated),
                **result.diagnostics,
            }
        )

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    ladder_correct = sum(
        scores.get("good", -1) > scores.get("medium", -1) > scores.get("bad", -1)
        for scores in family_scores.values()
    )
    quality_rows = [row for row in rows if row["challenge_type"] == "quality_ladder"]
    spearman = _spearman(
        [float(QUALITY_RANK[str(row["expected_quality"])]) for row in quality_rows],
        [float(row["score"]) for row in quality_rows],
    )
    adversarial = [row for row in rows if row["challenge_type"] != "quality_ladder"]
    adversarial_detected = sum(
        float(row["score"]) < 60 and int(row["hard_failure_count"]) > 0 for row in adversarial
    )
    scores_by_quality = {
        quality: [float(row["score"]) for row in quality_rows if row["expected_quality"] == quality]
        for quality in ("good", "medium", "bad")
    }
    summary = {
        "evaluator_version": "1.1",
        "case_count": len(rows),
        "quality_ladder_families": len(family_scores),
        "quality_ladder_order_accuracy": ladder_correct / len(family_scores),
        "spearman_quality_correlation": round(spearman, 4),
        "mean_score_by_quality": {
            key: round(statistics.mean(values), 2) for key, values in scores_by_quality.items()
        },
        "repeated_runs_per_case": 5,
        "maximum_repeat_stddev": max(repeated_stddevs),
        "adversarial_case_count": len(adversarial),
        "adversarial_detection_rate": adversarial_detected / len(adversarial),
        "limitations": [
            "The current benchmark is synthetic and validates deterministic grounding behavior.",
            "Human agreement and live Hy3 semantic-judge experiments are not claimed "
            "by this result.",
        ],
    }
    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "# RepoScope evaluator benchmark\n\n"
        "> Generated by `scripts/run_experiments.py`. This report covers the deterministic "
        "evaluator "
        "only; it does not claim human agreement or live-model validity.\n\n"
        "## Dataset\n\n"
        f"- {len(rows)} total cases\n"
        f"- {len(family_scores)} repository families with good / medium / bad output ladders\n"
        f"- {len(adversarial)} verbosity, fabricated-reference, and quote-mismatch attacks\n\n"
        "## Results\n\n"
        f"- Correct good > medium > bad ordering: **{ladder_correct}/{len(family_scores)} "
        f"({summary['quality_ladder_order_accuracy']:.1%})**\n"
        f"- Spearman correlation with designed quality rank: **{spearman:.4f}**\n"
        f"- Mean scores: **good {summary['mean_score_by_quality']['good']:.2f}**, "
        f"**medium {summary['mean_score_by_quality']['medium']:.2f}**, "
        f"**bad {summary['mean_score_by_quality']['bad']:.2f}**\n"
        f"- Adversarial cases rejected below 60 with a hard failure: "
        f"**{adversarial_detected}/{len(adversarial)} "
        f"({summary['adversarial_detection_rate']:.1%})**\n"
        f"- Maximum score standard deviation across five repeated deterministic runs: "
        f"**{summary['maximum_repeat_stddev']:.2f}**\n\n"
        "## Interpretation\n\n"
        "The experiment verifies that the deterministic layer is reproducible, separates the "
        "designed quality ladder, and does not reward extra verbosity when paths or quotes are "
        "fabricated. The next validation layer must use frozen real repository snapshots, blinded "
        "human annotations, and repeated Hy3 semantic judgments. Those results must remain visibly "
        "unverified until the "
        "annotations and live calls exist.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

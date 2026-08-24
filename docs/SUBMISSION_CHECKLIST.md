# Competition submission completion audit

This checklist maps every explicit Task 1 requirement to current authoritative evidence. A checked
item means the cited artifact or command directly proves it; it does not mean adjacent untested
behavior is inferred to work.

## Repository and application

- [ ] **Public repository with submitted link** - local history contains the complete project, but
  `BoyuChen1224/RepoScope-Hy3` remains empty until GitHub CLI authentication is restored and pushed.
- [x] **Runnable Hy3 application source** - `src/reposcope/`, `start.bat`, `start.sh`, `Dockerfile`.
- [x] **README introduction, runtime, and environment requirements** - `README.md`, `README_CN.md`.
- [x] **Environment configuration example without a committed key** - `.env.example`; `.env` is
  ignored, and the configured key was scanned against all committed candidates with no match.
- [x] **Independent activity-project attribution** - both README files and the UI footer explicitly
  state that this is a personal activity work, not an official Tencent release.
- [x] **Hy3 usage without training or fine-tuning** - `src/reposcope/hy3_client.py` uses the configured
  OpenAI-compatible Hy3 endpoint.

## Scenario and method

- [x] **Clear real user, problem, and model necessity** - `reports/final_report.md`, sections 1-2.
- [x] **More than five evaluation dimensions** - six deterministic dimensions plus four advisory
  semantic dimensions in `docs/EVALUATION.md`.
- [x] **Operational judgement anchors** - explicit 0-4 thresholds and hard-failure conditions in
  `docs/EVALUATION.md`; implementation in `src/reposcope/evaluator.py` and
  `src/reposcope/semantic_evaluator.py`.
- [x] **Automatic or semi-automatic evaluation flow** - API routes `/api/evaluations/evaluate` and
  `/api/evaluations/judge`, both exposed in the browser workflow.
- [x] **Design rationale** - `reports/final_report.md`, section 3.

## Samples and validity

- [x] **Documented sample source, construction, and coverage** - `datasets/README.md` and
  `scripts/generate_benchmark.py`.
- [x] **Hard and negative examples** - 12 fabricated-reference, quote-mismatch, verbosity, and
  unjustified-certainty cases in `datasets/benchmark/cases.jsonl`.
- [x] **Discrimination validation** - 24/24 correct good > medium > bad orderings and Spearman 1.0000
  in `results/experiment_summary.json`.
- [x] **Consistency validation** - five deterministic repeats per case with maximum standard deviation
  0; one live report with three Hy3 semantic repeats and zero per-dimension score variance.
- [x] **Adversarial validation** - 12/12 constructed attacks rejected below 60 with a hard failure.
- [x] **One real Hy3 case** - frozen self-repository commit, source manifest, report, deterministic
  score, three semantic results, and summary under `results/live/ed167494e5c6/`.
- [ ] **Human agreement** - not required because repeated-evaluation consistency is complete; an empty
  template and blind annotation protocol are provided, but no human metric is claimed.

## Required outputs

- [x] **Application, configuration, and run instructions** - source tree, `.env.example`, start scripts.
- [x] **Sample set, method document, scripts, and full result table** - `datasets/`, `docs/`, `scripts/`,
  `results/evaluation_results.csv`.
- [x] **Validity experiment process and data** - `reports/benchmark_analysis.md`, row-level CSV, JSON
  summary, and live evidence directory.
- [x] **Analysis report with scenario, solution, rubric basis, conclusions, failures, and boundaries** -
  `reports/final_report.md`.
- [x] **Demo shorter than two minutes** - 12.5-second `assets/demo/reposcope-hy3-demo.gif`; a 90-second
  narrated script is provided in `docs/DEMO_SCRIPT_CN.md`.

## Verification gates

- [x] Ruff passes.
- [x] 11 tests pass; coverage remains separately reported rather than treated as proof of untested paths.
- [x] JavaScript syntax check passes.
- [x] Desktop and 375px mobile browser layouts have no horizontal overflow; demo interaction and
  advisory semantic results render without console errors.
- [x] Docker Compose configuration parses.
- [ ] Docker image runtime - Docker daemon is unavailable on this machine, so runtime remains
  explicitly unverified and is not a competition requirement.
- [ ] GitHub Actions - cannot run until the first remote push.

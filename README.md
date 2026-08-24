# RepoScope Hy3

> An independent Rhinoceros Bird practice project. This repository is not an official Tencent release.

RepoScope Hy3 is an evidence-grounded open-source repository due-diligence assistant powered by Hy3.
It turns a repository snapshot into an adoption report whose material claims can be traced back to
files, line ranges, and quotes, then scores the report with deterministic evaluation rules.

![RepoScope Hy3 evidence workflow demo](assets/demo/reposcope-hy3-demo.gif)

Chinese documentation: [README_CN.md](README_CN.md)

## Why it is not another repository chatbot

- **Claim-level evidence:** material facts cite a repository-relative path, line range, and quote.
- **Fail-closed scoring:** fabricated paths, out-of-range lines, and quote mismatches trigger hard caps.
- **Hybrid evaluation:** rules validate objective references; an optional Hy3 judge reviews entailment
  and omitted risks; blinded human labels remain the calibration target.
- **Reproducible artifacts:** dataset construction, row-level scores, and analysis ship with the code.
- **Honest evidence levels:** missing live calls or human labels stay unverified rather than passed.

## Verified result boundary

Deterministic evaluator v1.0 has been executed on 84 synthetic cases: 24 good/medium/bad families
were ordered correctly, 12/12 adversarial cases were rejected, and five repeated runs per case had
zero score variance. Mean scores were 100.0, 61.5, and 18.5 for designed good, medium, and bad outputs.

This establishes deterministic behavior on constructed fixtures only. It does not claim human
agreement or live Hy3-output validity. See [`reports/benchmark_analysis.md`](reports/benchmark_analysis.md).
The broader scenario and capability-boundary analysis is in
[`reports/final_report.md`](reports/final_report.md).

## Status

The current milestone includes secure repository ingestion, versioned evidence/report schemas, an
OpenAI-compatible Hy3 generator, deterministic and semantic evaluators, a responsive evidence UI,
focused tests, and a reproducible synthetic benchmark.

## Quick start

Windows: run `start.bat`. macOS/Linux: run `chmod +x start.sh && ./start.sh`.

Open <http://127.0.0.1:8000>. API documentation is available at
<http://127.0.0.1:8000/docs>.

## Pipeline

```text
GitHub URL + adoption goal -> bounded clone -> frozen commit -> evidence manifest
-> Hy3 structured report -> deterministic grounding + optional Hy3 semantic review
-> dimension scores, hard failures, and claim-level attribution
```

## Security defaults

- Only allowlisted public HTTPS Git hosts are accepted.
- Repository URL credentials, custom ports, arbitrary URL paths, and local paths are rejected.
- Clones are shallow, size-limited, timeout-limited, and removed after inspection.
- Git commands use argument arrays with `shell=False`.
- API keys are read from environment variables and must never be committed.
- Repository content is untrusted evidence, not an instruction source.
- Repository and model strings are escaped before browser rendering.

## Configuration

See [`.env.example`](.env.example). Optional JSON response formatting and `reasoning_effort` are off
by default for broad OpenAI-compatible endpoint support. Enable them only when the selected endpoint
documents those features.

## Verification

```bash
python -m ruff check .
python -m pytest --cov=reposcope --cov-report=term-missing
python scripts/generate_benchmark.py
python scripts/run_experiments.py
```

## License

Apache-2.0. See `LICENSE`.

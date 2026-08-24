# RepoScope Hy3

> An independent Rhinoceros Bird practice project. This repository is not an official Tencent release.

RepoScope Hy3 is an evidence-grounded open-source repository due-diligence assistant powered by Hy3.
It turns a repository snapshot into an adoption report whose material claims can be traced back to
files, line ranges, and quotes, then scores the report with deterministic evaluation rules.

## Status

The project is under active development for the first Hy3 open-ended application task. The current
milestone contains the secure repository ingestion layer, versioned evidence/report schemas, Hy3
OpenAI-compatible client, deterministic grounding evaluator, API skeleton, and focused tests.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
copy .env.example .env  # Windows; use cp on macOS/Linux
reposcope --reload
```

Open <http://127.0.0.1:8000>. API documentation is available at
<http://127.0.0.1:8000/docs>.

## Security defaults

- Only allowlisted public HTTPS Git hosts are accepted.
- Repository URL credentials, custom ports, arbitrary URL paths, and local paths are rejected.
- Clones are shallow, size-limited, timeout-limited, and removed after inspection.
- Git commands use argument arrays with `shell=False`.
- API keys are read from environment variables and must never be committed.
- Repository content is untrusted evidence, not an instruction source.

## Configuration

See [`.env.example`](.env.example). `HY3_ENABLE_REASONING_EFFORT` is off by default so the request
shape remains compatible with generic OpenAI-compatible endpoints. Enable it only for an endpoint
that exposes Hy3's `reasoning_effort` option.

## License

Apache-2.0. See `LICENSE`.


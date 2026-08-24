# Contributing

Thank you for improving this independent activity project.

1. Create a focused branch from `main`.
2. Install development dependencies with `python -m pip install -e ".[dev]"`.
3. Run `python -m ruff check .` and `python -m pytest`.
4. If evaluator behavior changes, regenerate the benchmark and explain score movement.
5. Never commit `.env`, API keys, cloned third-party repositories, or unlicensed datasets.

Evaluation changes must preserve evidence boundaries: synthetic, live-model, and human-labelled results
belong in separate artifacts and must not be presented as interchangeable proof.


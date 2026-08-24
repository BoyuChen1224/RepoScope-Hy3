#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install -e .

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add HY3_API_KEY before live generation."
fi

python -m uvicorn reposcope.app:app --host 127.0.0.1 --port 8000


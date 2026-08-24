@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv || exit /b 1
)

call ".venv\Scripts\activate.bat" || exit /b 1
python -m pip install -e . || exit /b 1

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created .env from .env.example. Add HY3_API_KEY before live generation.
)

python -m uvicorn reposcope.app:app --host 127.0.0.1 --port 8000


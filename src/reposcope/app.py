from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import get_settings
from .evaluator import evaluate_report
from .hy3_client import Hy3ReportGenerator
from .inspector import InspectionError, inspect_repository
from .models import (
    DueDiligenceReport,
    EvaluateRequest,
    EvaluationResult,
    GenerateRequest,
    InspectRequest,
    RepositoryManifest,
)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="RepoScope Hy3",
    version=__version__,
    description="Evidence-grounded open-source repository due diligence powered by Hy3.",
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.post("/api/repositories/inspect", response_model=RepositoryManifest)
def inspect(request: InspectRequest) -> RepositoryManifest:
    try:
        return inspect_repository(str(request.repository_url), request.goal, get_settings())
    except InspectionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail="Repository inspection timed out.") from exc


@app.post("/api/reports/generate", response_model=DueDiligenceReport)
def generate(request: GenerateRequest) -> DueDiligenceReport:
    try:
        return Hy3ReportGenerator(get_settings()).generate(request.manifest)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hy3 report generation failed: {exc}") from exc


@app.post("/api/evaluations/evaluate", response_model=EvaluationResult)
def evaluate(request: EvaluateRequest) -> EvaluationResult:
    return evaluate_report(request.manifest, request.report)


if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


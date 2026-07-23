import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, PlainTextResponse

from app.models.database import init_db
from app.api import problems_router, testcases_router, models_router
from app.schemas.problem import GeneratedProblem
from app.services.exporters import ExportService
from app.verifier.quality_gate import QualityGateEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Database initialization deferred: {e}")
    yield
    # Shutdown logic

app = FastAPI(
    title="Problem Foundry API",
    description="Model-Agnostic Local AI System for Algorithmic Problem Authoring, Differential Verification, and Test Case Synthesis",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(problems_router)
app.include_router(testcases_router)
app.include_router(models_router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Problem Foundry Local AI System",
        "docs": "/docs"
    }

@app.post("/api/export/markdown", response_class=PlainTextResponse)
async def export_markdown(problem: GeneratedProblem):
    if problem.quality_score and not problem.quality_score.pass_quality_gate:
        eval_res = QualityGateEngine.evaluate(problem.quality_score.model_dump())
        if not eval_res["can_export"]:
            raise HTTPException(
                status_code=400,
                detail=f"Quality Gate Rejected (Score: {problem.quality_score.total_score}/100 < 85.0 threshold). Reasons: {eval_res['rejection_reasons']}"
            )
    return ExportService.to_markdown(problem)

@app.post("/api/export/json")
async def export_json(problem: GeneratedProblem):
    if problem.quality_score and not problem.quality_score.pass_quality_gate:
        eval_res = QualityGateEngine.evaluate(problem.quality_score.model_dump())
        if not eval_res["can_export"]:
            raise HTTPException(
                status_code=400,
                detail=f"Quality Gate Rejected (Score: {problem.quality_score.total_score}/100 < 85.0 threshold)."
            )
    return Response(content=ExportService.to_json(problem), media_type="application/json")

@app.post("/api/export/leetcode")
async def export_leetcode_package(problem: GeneratedProblem):
    if problem.quality_score and not problem.quality_score.pass_quality_gate:
        eval_res = QualityGateEngine.evaluate(problem.quality_score.model_dump())
        if not eval_res["can_export"]:
            raise HTTPException(
                status_code=400,
                detail=f"Quality Gate Rejected (Score: {problem.quality_score.total_score}/100 < 85.0 threshold)."
            )
    zip_bytes = ExportService.to_leetcode_package(problem)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={problem.id}_leetcode_package.zip"}
    )

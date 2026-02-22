# backend/app/routers/analysis.py

from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatusResponse,
    AnalysisListResponse,
    PaperSelectRequest,
    Analysis,
)
from app.services import analysis_repo, analysis_service
import uuid

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start analysis from arXiv ID, URL, or topic"""

    analysis_id = str(uuid.uuid4())

    analysis = Analysis(
        id=analysis_id,
        input_type=request.input_type.value,
        input_value=request.input,
        llm_provider=request.llm_provider,
        include_market_research=request.include_market_research,
        include_technical_assessment=request.include_technical_assessment,
        include_business_model=request.include_business_model,
    )

    analysis_repo.create(analysis)

    background_tasks.add_task(analysis_service.start_analysis, analysis, request)

    return AnalysisResponse(
        analysis_id=analysis_id,
        status="pending",
        message=f"Starting analysis for: {request.input}"
    )


@router.post("/analyze/select", response_model=AnalysisResponse)
async def select_and_analyze(request: PaperSelectRequest, background_tasks: BackgroundTasks):
    """Select a paper from discovery results"""
    analysis = analysis_repo.get(request.analysis_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Start analysis with selected paper
    analysis_request = AnalysisRequest(
        input=request.arxiv_id,
        llm_provider=analysis.llm_provider,
        include_market_research=analysis.include_market_research,
        include_technical_assessment=analysis.include_technical_assessment,
        include_business_model=analysis.include_business_model,
    )

    background_tasks.add_task(
        analysis_service.select_paper,
        request.analysis_id,
        request.arxiv_id,
        analysis_request
    )

    return AnalysisResponse(
        analysis_id=request.analysis_id,
        status="processing",
        message=f"Analyzing paper: {request.arxiv_id}"
    )


@router.get("/analysis/{analysis_id}", response_model=AnalysisStatusResponse)
async def get_analysis(analysis_id: str):
    """Get analysis status and results"""
    analysis = analysis_repo.get(analysis_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return AnalysisStatusResponse(
        analysis_id=analysis.id,
        status=analysis.status,
        progress=analysis.progress,
        error_message=analysis.error_message,
        paper_analysis=analysis.paper_analysis,
        ideas=analysis.ideas,
        business_models=analysis.business_models,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
    )


@router.get("/recent", response_model=AnalysisListResponse)
async def get_recent(limit: int = 10):
    """Get recent analyses"""
    analyses = analysis_repo.get_recent(limit)

    return AnalysisListResponse(
        analyses=[
            {
                "id": a.id,
                "arxiv_id": a.resolved_arxiv_id,
                "status": a.status,
                "paper_title": a.paper_analysis.get("paper_title") if a.paper_analysis else None,
                "ideas_count": len(a.ideas) if a.ideas else 0,
                "created_at": a.created_at.isoformat(),
            }
            for a in analyses
        ],
        total=len(analyses)
    )


@router.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis"""
    success = analysis_repo.delete(analysis_id)

    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {"message": "Analysis deleted"}

# backend/app/routers/export.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from app.models import ExportRequest, ExportResponse
from app.services import analysis_repo, export_repo, export_service

router = APIRouter(prefix="/api", tags=["export"])


@router.post("/export", response_model=ExportResponse)
async def create_export(request: ExportRequest):
    """Export analysis results"""
    analysis = analysis_repo.get(request.analysis_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not complete")

    export = export_service.export_analysis(analysis, request.format)
    export_repo.create(export)

    return ExportResponse(
        export_id=export.id,
        format=export.format,
        share_token=export.share_token,
        share_link=export_service.get_share_link(export),
        expires_at=export.expires_at,
    )


@router.get("/export/{export_id}/download")
async def download_export(export_id: str):
    """Download exported file"""
    export = export_repo.get(export_id)

    if not export:
        raise HTTPException(status_code=404, detail="Export not found")

    if export.expires_at and export.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Export expired")

    export_repo.increment_download_count(export_id)

    media_types = {
        "pdf": "application/pdf",
        "markdown": "text/markdown",
        "json": "application/json"
    }

    return FileResponse(
        export.file_path,
        media_type=media_types.get(export.format, "application/octet-stream"),
        filename=f"saas-analysis-{export.analysis_id[:8]}.{export.format}"
    )


@router.get("/share/{share_token}")
async def get_shared_export(share_token: str):
    """Access export via share token"""
    export = export_repo.get_by_share_token(share_token)

    if not export:
        raise HTTPException(status_code=404, detail="Share link not found")

    if export.expires_at and export.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Share link expired")

    return FileResponse(export.file_path)

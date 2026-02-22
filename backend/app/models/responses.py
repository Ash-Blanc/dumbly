# backend/app/models/responses.py

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str
    papers: Optional[List[dict]] = None


class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: str
    progress: Dict[str, Any] = {}
    error_message: Optional[str] = None
    paper_analysis: Optional[dict] = None
    ideas: Optional[List[dict]] = None
    business_models: Optional[List[dict]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class AnalysisListResponse(BaseModel):
    analyses: List[dict]
    total: int


class ExportResponse(BaseModel):
    export_id: str
    format: str
    share_token: str
    share_link: str
    expires_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str

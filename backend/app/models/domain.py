# backend/app/models/domain.py

from sqlmodel import SQLModel, Field, Column, JSON, Text
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class AnalysisStatus(str, Enum):
    DISCOVERY = "discovery"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class Analysis(SQLModel, table=True):
    """Main analysis record"""
    __tablename__ = "analyses"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Input tracking
    input_type: str
    input_value: str
    resolved_arxiv_id: Optional[str] = None

    # Configuration
    llm_provider: str = "pollinations"
    focus_areas: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    target_audience: Optional[str] = None
    include_market_research: bool = True
    include_technical_assessment: bool = True
    include_business_model: bool = True

    # Status tracking
    status: str = Field(default=AnalysisStatus.PENDING.value)
    progress: dict = Field(default_factory=dict, sa_column=Column(JSON))
    error_message: Optional[str] = None

    # Results
    paper_analysis: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    ideas: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    business_models: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # User tracking (for future auth)
    user_id: Optional[str] = None


class DiscoveredPaper(SQLModel, table=True):
    """Papers found during topic discovery"""
    __tablename__ = "discovered_papers"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    analysis_id: str = Field(foreign_key="analyses.id", index=True)

    arxiv_id: str
    title: str
    authors: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    summary: str = Field(sa_column=Column(Text))
    relevance_score: float = 0.0
    novelty_score: float = 0.0
    categories: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    published_date: Optional[str] = None

    selected: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowSession(SQLModel, table=True):
    """Agno workflow session storage"""
    __tablename__ = "workflow_sessions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    analysis_id: str = Field(foreign_key="analyses.id", index=True)

    session_id: str
    workflow_name: str
    current_step: Optional[str] = None
    step_history: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    messages: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    tokens_used: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Export(SQLModel, table=True):
    """Export records for shareable links"""
    __tablename__ = "exports"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    analysis_id: str = Field(foreign_key="analyses.id", index=True)

    format: str  # pdf, markdown, json
    file_path: Optional[str] = None
    share_token: str = Field(default_factory=lambda: str(uuid.uuid4()))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    download_count: int = 0

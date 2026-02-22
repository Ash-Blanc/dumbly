# backend/app/models/requests.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
import re


class InputType(str, Enum):
    ARXIV_ID = "arxiv_id"
    ARXIV_URL = "arxiv_url"
    PLATFORM_URL = "platform_url"
    TOPIC = "topic"


class AnalysisRequest(BaseModel):
    input: str = Field(..., description="arXiv ID, URL, or topic")
    input_type: Optional[InputType] = None

    # Options
    focus_areas: Optional[List[str]] = None
    target_audience: Optional[str] = None
    max_papers: int = Field(default=5, ge=1, le=10)
    auto_select: bool = True

    # Feature toggles
    include_market_research: bool = True
    include_technical_assessment: bool = True
    include_business_model: bool = True

    # LLM configuration
    llm_provider: str = "pollinations"
    llm_api_key: Optional[str] = None

    @validator('input_type', pre=True, always=True)
    def detect_input_type(cls, v, values):
        if v:
            return v
        input_val = values.get('input', '')
        return cls._detect_type(input_val)

    @staticmethod
    def _detect_type(input_str: str) -> InputType:
        input_str = input_str.strip()

        # Pure arXiv ID
        if re.match(r'^(\d{4}\.\d{4,5}|[a-z-]+/\d+)$', input_str):
            return InputType.ARXIV_ID

        # arXiv URLs
        if 'arxiv.org' in input_str:
            return InputType.ARXIV_URL

        # Platform URLs
        platform_domains = [
            'alphaxiv.org', 'huggingface.co', 'paperswithcode.com',
            'semanticscholar.org'
        ]
        if any(domain in input_str for domain in platform_domains):
            return InputType.PLATFORM_URL

        return InputType.TOPIC


class PaperSelectRequest(BaseModel):
    analysis_id: str
    arxiv_id: str


class ExportRequest(BaseModel):
    analysis_id: str
    format: str = "markdown"

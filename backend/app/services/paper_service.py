# backend/app/services/paper_service.py

import re
from typing import Optional, List, Dict, Any
from app.models.requests import InputType


class PaperService:
    """Handles paper input parsing and discovery"""

    ARXIV_PATTERNS = [
        r'(\d{4}\.\d{4,5})',  # New format: 2303.12712
        r'([a-z-]+/\d+)',     # Old format: cs.AI/0701001
    ]

    PLATFORM_PATTERNS = {
        'alphaxiv.org': r'/paper/([a-z-]+/\d+|\d{4}\.\d+)',
        'huggingface.co': r'/papers/(\d{4}\.\d{4,5})',
        'paperswithcode.com': r'/paper/[^/]+-(\d{4}\.\d{4,5})',
        'semanticscholar.org': r'/arXiv:(\d{4}\.\d{4,5})',
    }

    def resolve_input(self, input_str: str, input_type: InputType) -> Dict[str, Any]:
        """Resolve any input type to arXiv ID(s)"""

        match input_type:
            case InputType.ARXIV_ID:
                return {
                    "arxiv_id": self._normalize_id(input_str),
                    "type": "single"
                }

            case InputType.ARXIV_URL:
                arxiv_id = self._extract_from_arxiv_url(input_str)
                return {"arxiv_id": arxiv_id, "type": "single"}

            case InputType.PLATFORM_URL:
                arxiv_id = self._extract_from_platform_url(input_str)
                return {"arxiv_id": arxiv_id, "type": "single"}

            case InputType.TOPIC:
                return {"topic": input_str, "type": "discovery"}

    def _normalize_id(self, arxiv_id: str) -> str:
        """Normalize arXiv ID format"""
        arxiv_id = arxiv_id.strip().lower()
        if arxiv_id.startswith('arxiv:'):
            arxiv_id = arxiv_id[6:]
        return arxiv_id

    def _extract_from_arxiv_url(self, url: str) -> str:
        """Extract arXiv ID from arxiv.org URL"""
        for pattern in self.ARXIV_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError(f"Could not extract arXiv ID from URL: {url}")

    def _extract_from_platform_url(self, url: str) -> str:
        """Extract arXiv ID from platform URLs"""
        for platform, pattern in self.PLATFORM_PATTERNS.items():
            if platform in url:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
        raise ValueError(f"Could not extract arXiv ID from platform URL: {url}")


# Singleton instance
paper_service = PaperService()

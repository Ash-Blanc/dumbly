# backend/app/agents/paper_analyzer.py

from agno.tools.arxiv import ArxivTools
from app.agents.base import create_agent, LLMProvider
from typing import Optional


PAPER_ANALYZER_INSTRUCTIONS = """
You are a research paper analyst specializing in identifying commercial potential.

Given an arXiv paper, analyze it for:
1. Key innovations and breakthroughs
2. Novelty score (0-1) based on uniqueness of approach
3. Commercial potential (0-1) based on practical applications
4. Target industries and use cases
5. Technical complexity for implementation

Always respond with valid JSON:
{
  "paper_title": "...",
  "paper_id": "...",
  "summary": "2-3 sentence summary",
  "key_innovations": ["innovation1", "innovation2"],
  "novelty_score": 0.85,
  "commercial_potential": 0.75,
  "target_industries": ["industry1", "industry2"],
  "potential_applications": ["app1", "app2"],
  "technical_complexity": "medium",
  "readiness_level": "research"
}
"""


def create_paper_analyzer(
    provider: LLMProvider = LLMProvider.POLLINATIONS,
    api_key: Optional[str] = None,
):
    return create_agent(
        name="PaperAnalyzer",
        instructions=PAPER_ANALYZER_INSTRUCTIONS,
        tools=[ArxivTools()],
        provider=provider,
        api_key=api_key,
        markdown=False,
    )

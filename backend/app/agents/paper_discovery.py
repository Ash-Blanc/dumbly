# backend/app/agents/paper_discovery.py

from agno.tools.arxiv import ArxivTools
from app.agents.base import create_agent, LLMProvider
from typing import Optional


PAPER_DISCOVERY_INSTRUCTIONS = """
You are a research paper discovery agent.

Given a research topic, find the most relevant and impactful papers.
For each paper, provide:
- arXiv ID
- Title
- Authors (first 3)
- Summary (2-3 sentences)
- Relevance score (0-1)
- Novelty score (0-1) based on citations and recency
- Categories
- Published date

Sort by combined relevance and novelty score.

Always respond with valid JSON array:
[
  {
    "arxiv_id": "2303.12712",
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "summary": "Brief summary...",
    "relevance_score": 0.9,
    "novelty_score": 0.8,
    "categories": ["cs.AI", "cs.LG"],
    "published_date": "2023-03-01"
  }
]
"""


def create_paper_discovery(
    provider: LLMProvider = LLMProvider.POLLINATIONS,
    api_key: Optional[str] = None,
):
    return create_agent(
        name="PaperDiscovery",
        instructions=PAPER_DISCOVERY_INSTRUCTIONS,
        tools=[ArxivTools()],
        provider=provider,
        api_key=api_key,
        markdown=False,
    )

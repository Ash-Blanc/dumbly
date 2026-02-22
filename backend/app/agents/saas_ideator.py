# backend/app/agents/saas_ideator.py

from app.agents.base import create_agent, LLMProvider
from typing import Optional


SAAS_IDEATOR_INSTRUCTIONS = """
You are a SaaS product ideation expert.

Based on a research paper analysis, generate 3-5 viable SaaS product ideas.
Each idea should include:
- Clear value proposition
- Target market
- Key features
- Competitive advantage
- Market fit score (0-1)

Always respond with valid JSON array:
[
  {
    "id": "idea_1",
    "title": "SaaS Name",
    "tagline": "One-line pitch",
    "description": "2-3 sentences",
    "target_market": "...",
    "key_features": ["feature1", "feature2"],
    "competitive_advantage": "...",
    "market_fit_score": 0.8,
    "mvp_features": ["feature1", "feature2"]
  }
]
"""


def create_saas_ideator(
    provider: LLMProvider = LLMProvider.POLLINATIONS,
    api_key: Optional[str] = None,
):
    return create_agent(
        name="SaaSIdeator",
        instructions=SAAS_IDEATOR_INSTRUCTIONS,
        provider=provider,
        api_key=api_key,
        markdown=False,
    )

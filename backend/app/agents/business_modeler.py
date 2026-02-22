# backend/app/agents/business_modeler.py

from app.agents.base import create_agent, LLMProvider
from typing import Optional


BUSINESS_MODELER_INSTRUCTIONS = """
You are a business model expert.

Create a comprehensive business model for a SaaS idea:
1. Revenue model (subscription, usage-based, etc.)
2. Pricing strategy and tiers
3. MVP roadmap (3-6 months)
4. Key metrics to track
5. Funding requirements if applicable

Always respond with valid JSON:
{
  "idea_id": "...",
  "business_model": {
    "revenue_model": "subscription",
    "pricing_strategy": {
      "free_tier": "...",
      "pro_tier": "$X/month",
      "enterprise_tier": "$Y/month"
    },
    "mvp_roadmap": [
      {"month": 1, "goals": [...]},
      {"month": 2, "goals": [...]},
      {"month": 3, "goals": [...]}
    ],
    "key_metrics": ["metric1", "metric2"],
    "funding_requirements": "$X seed round",
    "break_even_timeline": "X months"
  }
}
"""


def create_business_modeler(
    provider: LLMProvider = LLMProvider.POLLINATIONS,
    api_key: Optional[str] = None,
):
    return create_agent(
        name="BusinessModeler",
        instructions=BUSINESS_MODELER_INSTRUCTIONS,
        provider=provider,
        api_key=api_key,
        markdown=False,
    )

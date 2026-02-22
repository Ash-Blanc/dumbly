# backend/app/agents/market_researcher.py

from agno.tools.duckduckgo import DuckDuckGoTools
from app.agents.base import create_agent, LLMProvider
from typing import Optional


MARKET_RESEARCHER_INSTRUCTIONS = """
You are a market research analyst.

Research and analyze the market for a given SaaS idea:
1. Market size estimation (TAM, SAM, SOM)
2. Growth rate and trends
3. Key competitors
4. Customer pain points
5. Pricing benchmarks

Always respond with valid JSON:
{
  "idea_id": "...",
  "market_size_estimate": "$X Billion TAM",
  "growth_rate": "X% CAGR",
  "key_competitors": [{"name": "...", "strengths": [...]}],
  "customer_pain_points": ["pain1", "pain2"],
  "pricing_benchmarks": {"low": "$X", "mid": "$Y", "high": "$Z"},
  "market_opportunities": ["opp1", "opp2"]
}
"""


def create_market_researcher(
    provider: LLMProvider = LLMProvider.POLLINATIONS,
    api_key: Optional[str] = None,
):
    return create_agent(
        name="MarketResearcher",
        instructions=MARKET_RESEARCHER_INSTRUCTIONS,
        tools=[DuckDuckGoTools()],
        provider=provider,
        api_key=api_key,
        markdown=False,
    )

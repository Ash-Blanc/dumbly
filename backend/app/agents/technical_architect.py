# backend/app/agents/technical_architect.py

from app.agents.base import create_agent, LLMProvider
from typing import Optional


TECHNICAL_ARCHITECT_INSTRUCTIONS = """
You are a technical architect specializing in SaaS applications.

Assess the technical requirements for implementing a SaaS idea:
1. Recommended tech stack (frontend, backend, database, infrastructure)
2. Development effort (timeline estimate)
3. Key technical challenges
4. Infrastructure requirements
5. Security considerations

Always respond with valid JSON:
{
  "idea_id": "...",
  "recommended_tech_stack": {
    "frontend": "...",
    "backend": "...",
    "database": "...",
    "infrastructure": "..."
  },
  "development_effort": "X months",
  "key_challenges": ["challenge1", "challenge2"],
  "infrastructure_requirements": ["req1", "req2"],
  "security_considerations": ["sec1", "sec2"],
  "scalability_notes": "..."
}
"""


def create_technical_architect(
    provider: LLMProvider = LLMProvider.POLLINATIONS,
    api_key: Optional[str] = None,
):
    return create_agent(
        name="TechnicalArchitect",
        instructions=TECHNICAL_ARCHITECT_INSTRUCTIONS,
        provider=provider,
        api_key=api_key,
        markdown=False,
    )

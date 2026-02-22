# backend/app/agents/base.py

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.db.postgres import PostgresDb
from typing import Optional, List
from enum import Enum
from app.config import settings


class LLMProvider(str, Enum):
    POLLINATIONS = "pollinations"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


def get_model(provider: LLMProvider, api_key: Optional[str] = None):
    """Factory for LLM models based on provider"""
    match provider:
        case LLMProvider.POLLINATIONS:
            return OpenAIChat(
                id="gemini-fast",
                api_key=settings.pollinations_api_key,
                base_url=settings.pollinations_base_url
            )
        case LLMProvider.OPENAI:
            if not api_key:
                raise ValueError("OpenAI API key required")
            return OpenAIChat(id="gpt-4o", api_key=api_key)
        case LLMProvider.ANTHROPIC:
            if not api_key:
                raise ValueError("Anthropic API key required")
            return Claude(id="claude-sonnet-4-5", api_key=api_key)
        case LLMProvider.OLLAMA:
            return OpenAIChat(
                id="llama3.2",
                base_url="http://localhost:11434/v1"
            )
        case _:
            raise ValueError(f"Unknown provider: {provider}")


def create_agent(
    name: str,
    instructions: str,
    tools: List = None,
    provider: LLMProvider = LLMProvider.POLLINATIONS,
    api_key: Optional[str] = None,
    db: Optional[PostgresDb] = None,
    markdown: bool = True,
) -> Agent:
    """Factory for creating agents with configured LLM"""
    return Agent(
        name=name,
        model=get_model(provider, api_key),
        tools=tools or [],
        instructions=instructions,
        db=db,
        add_history_to_context=True,
        markdown=markdown,
    )

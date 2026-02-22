# backend/app/config.py

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "arXiv SaaS Generator"
    debug: bool = False
    environment: str = "development"
    base_url: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/arxiv_saas"

    # LLM Providers
    default_llm_provider: str = "pollinations"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Pollinations (default, free)
    pollinations_api_key: str = "sk_2Ic2LdKet78KodrKBmDyD34ciKHUkz7D"
    pollinations_base_url: str = "https://gen.pollinations.ai/v1"

    # Redis (optional)
    redis_url: Optional[str] = None

    # Export settings
    export_dir: str = "./exports"
    share_link_expiry_days: int = 30

    # CORS
    cors_origins: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

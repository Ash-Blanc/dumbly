# backend/app/database.py

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager, contextmanager
from app.config import settings
from typing import AsyncGenerator, Generator


# Async engine for FastAPI
async_database_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)
async_engine = create_async_engine(
    async_database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine for Agno (it uses sync internally)
sync_database_url = settings.database_url
if sync_database_url.startswith("postgresql://"):
    sync_database_url = sync_database_url.replace("postgresql://", "postgresql+psycopg://")
    
sync_engine = create_engine(
    sync_database_url,
    echo=settings.debug,
    pool_size=5,
)


async def init_db():
    """Create tables on startup"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """Sync session for Agno workflows"""
    with Session(sync_engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

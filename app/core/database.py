"""Database engine/session setup.

Two engines are kept in sync against the same SQLite file:
- Async engine/session for FastAPI request handlers.
- Sync engine/session for the background build worker thread and APScheduler
  jobs, which do not run inside the asyncio event loop.
"""
from collections.abc import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(settings.database_url, future=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)

sync_engine = create_engine(settings.sync_database_url, future=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)


async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_db() -> Generator[Session, None, None]:
    with SyncSessionLocal() as session:
        yield session

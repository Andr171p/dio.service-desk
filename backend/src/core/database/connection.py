from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import postgres_config

engine = create_async_engine(
    url=postgres_config.uri,
    pool_size=postgres_config.pool_size,
    max_overflow=postgres_config.max_overflow,
    pool_timeout=postgres_config.pool_timeout,
    pool_pre_ping=True,
    echo=postgres_config.echo,
)

sessionmaker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


@asynccontextmanager
async def session_factory() -> AsyncIterator[AsyncSession]:
    async with sessionmaker() as session:
        yield session

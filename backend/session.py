from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from backend.config import PG_DATABASE, PG_HOST, PG_PASSWORD, PG_LOGIN

DATABASE_URL = f"postgresql+asyncpg://{PG_LOGIN}:{PG_PASSWORD}@{PG_HOST}/{PG_DATABASE}"
engine = create_async_engine(DATABASE_URL)
session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session

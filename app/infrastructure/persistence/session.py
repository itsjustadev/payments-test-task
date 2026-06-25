import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from app.infrastructure.config.settings import DATABASE_URL

async_engine: AsyncEngine = create_async_engine(DATABASE_URL)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

logger = logging.getLogger("app.infrastructure.persistence")

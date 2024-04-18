from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.pool import QueuePool

from src.config.manager import settings  # 确保这里正确引入了settings

class AsyncDatabase:
    def __init__(self):
        mysql_uri = f"{settings.MYSQL_SCHEMA}://{settings.MYSQL_USERNAME}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
        self.async_engine: AsyncEngine = create_async_engine(
            url=mysql_uri,
            echo=settings.IS_DB_ECHO_LOG,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_POOL_OVERFLOW,
        )
        self.async_session: AsyncSession = AsyncSession(bind=self.async_engine)
        self.pool = self.async_engine.pool

async_db: AsyncDatabase = AsyncDatabase()

import socket
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings


def get_effective_db_url(url: str) -> str:
    if "@db:" in url:
        try:
            socket.gethostbyname("db")
        except socket.gaierror:
            return url.replace("@db:", "@localhost:")
    return url


engine = create_async_engine(
    get_effective_db_url(settings.DATABASE_URL),
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
from collections.abc import AsyncGenerator, Callable
from datetime import datetime
from typing import Annotated, Any

from fastapi import Depends
from fastapi_storages.integrations.sqlalchemy import FileType as _FileType
from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.storages import get_storage

logger = get_logger(__name__)


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session


class FileType(_FileType):
    """Колонка с файлом в настроенном S3: FileType() или FileType("avatars")."""

    def __init__(
        self, upload_to: str | Callable[[str], str] | None = None, **kwargs: Any
    ) -> None:
        super().__init__(storage=get_storage(), upload_to=upload_to, **kwargs)


engine = create_async_engine(settings.db.DB_URL)
session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        yield session


async def ping_database() -> bool:
    try:
        async with session_maker() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.error("Database ping failed", exc_info=True)
        return False


SessionDep = Annotated[AsyncSession, Depends(get_session)]

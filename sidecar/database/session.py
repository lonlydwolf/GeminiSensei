import contextlib
import logging
import sqlite3
from collections.abc import AsyncGenerator
from typing import override

from pydantic import BaseModel, PrivateAttr
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import ConnectionPoolEntry

from core.config import settings

logger = logging.getLogger(__name__)


def get_db_url() -> str:
    _db_url = settings.DATABASE_URL
    if _db_url.startswith("sqlite+aiosqlite:///"):
        db_file = _db_url.replace("sqlite+aiosqlite:///", "")
        if db_file:
            # If the path is already absolute, Path(db_file) will ignore settings.BASE_DIR
            db_path = (settings.BASE_DIR / db_file).absolute()
            db_path.parent.mkdir(parents=True, exist_ok=True)

            # Reconstruct the absolute URL for the engine using raw path
            _db_url = f"sqlite+aiosqlite:///{db_path}"
            logger.debug(f"Resolved database URL: {_db_url}")
    return _db_url


class DBSessionManager(BaseModel):
    _engine: AsyncEngine = PrivateAttr()
    _sessionmaker: async_sessionmaker[AsyncSession] = PrivateAttr()

    @override
    def model_post_init(self, __context: object, /) -> None:
        _db_url = get_db_url()
        self._engine = create_async_engine(url=_db_url, echo=settings.DEBUG, future=True)

        @event.listens_for(self._engine.sync_engine, "connect")
        def set_sqlite_pragma(  # pyright: ignore[reportUnusedFunction]
            dbapi_connection: sqlite3.Connection, _connection_record: ConnectionPoolEntry
        ):
            cursor = dbapi_connection.cursor()
            _ = cursor.execute("PRAGMA journal_mode=WAL")
            _ = cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        if self._engine is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise Exception("DBSessionManager is not initialized")
        await self._engine.dispose()

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncGenerator[AsyncConnection, None]:
        async with self._engine.begin() as conn:
            yield conn

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._sessionmaker() as session:
            yield session


dbsessionmanager = DBSessionManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with dbsessionmanager.session() as session:
        yield session


async def get_connection() -> AsyncGenerator[AsyncConnection, None]:
    async with dbsessionmanager.connect() as conn:
        yield conn

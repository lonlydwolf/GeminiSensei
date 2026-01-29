import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings
from database.base import Base

logger = logging.getLogger(__name__)

# Ensure the directory for the database exists
_db_url = settings.DATABASE_URL
if _db_url.startswith("sqlite+aiosqlite:///"):
    db_file = _db_url.replace("sqlite+aiosqlite:///", "")
    if db_file:
        db_path = settings.BASE_DIR / db_file
        db_path.parent.mkdir(parents=True, exist_ok=True)
        # Reconstruct the absolute URL for the engine
        _db_url = f"sqlite+aiosqlite:///{db_path}"

engine = create_async_engine(_db_url, echo=settings.DEBUG, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    try:
        async with engine.begin() as conn:
            # Import models here to ensure they are registered with Base.metadata
            import database.models  # noqa: F401  # pyright: ignore[reportUnusedImport]

            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

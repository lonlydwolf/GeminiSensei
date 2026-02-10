import asyncio
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.models import Base
from database.session import get_db
from main import SIDECAR_SECRET, app
from services.gemini_service import GeminiService

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def temp_test_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session
        # Clean up database after each test
        async with test_engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                _ = await conn.execute(table.delete())


@pytest.fixture
def mock_gemini_client() -> MagicMock:
    """Mock Gemini API client."""
    client = MagicMock()
    client.aio = MagicMock()
    client.aio.models = MagicMock()
    client.aio.models.generate_content = AsyncMock()
    client.aio.models.generate_content_stream = AsyncMock()
    return client


@pytest.fixture
def mock_gemini_service() -> MagicMock:
    """Mock GeminiService for testing."""
    service = MagicMock(spec=GeminiService)
    service.generate_content = AsyncMock()
    service.generate_content_stream = AsyncMock()
    service.update_api_key = AsyncMock()
    return service


@pytest.fixture
def mock_api_key() -> str:
    """Provide a fake API key for testing."""
    return "AIzaSyDummyTestKey1234567890123456789"


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client with database override."""

    # Override get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Use ASGITransport for testing FastAPI app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Sidecar-Token": SIDECAR_SECRET},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

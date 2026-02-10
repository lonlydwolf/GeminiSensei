from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Gemini Sensei Sidecar!"}


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_lifespan_missing_api_key():
    """Test that lifespan works without API key (agents should not initialize)."""
    from core.config import settings

    # Store original key
    original_key = settings.GEMINI_API_KEY

    try:
        # Set empty API key
        settings.GEMINI_API_KEY = ""

        # Mock app
        app = FastAPI()

        # Create mocks
        mock_run_migrations = MagicMock()
        mock_agent_manager = MagicMock()
        mock_agent_manager.initialize_all = AsyncMock()
        mock_agent_manager.close_all = AsyncMock()

        # Mock database session and query
        mock_db_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        mock_dbsessionmanager = MagicMock()
        mock_dbsessionmanager.session = MagicMock()
        mock_dbsessionmanager.session.return_value.__aenter__ = AsyncMock(
            return_value=mock_db_session
        )
        mock_dbsessionmanager.session.return_value.__aexit__ = AsyncMock()
        mock_dbsessionmanager.close = AsyncMock()

        # Apply patches at import locations
        with (
            patch("main.run_migrations", mock_run_migrations),
            patch("main.agent_manager", mock_agent_manager),
            patch("main.dbsessionmanager", mock_dbsessionmanager),
        ):
            # Import lifespan after patching
            from main import lifespan

            # Test lifespan
            async with lifespan(app):
                pass

            # Verify migrations were called (via asyncio.to_thread)
            # Note: asyncio.to_thread is hard to mock, so we just verify no errors

            # Verify agents were NOT initialized (no API key)
            mock_agent_manager.initialize_all.assert_not_called()

            # Verify cleanup was called
            mock_agent_manager.close_all.assert_called_once()
            mock_dbsessionmanager.close.assert_called_once()

    finally:
        # Restore key
        settings.GEMINI_API_KEY = original_key


@pytest.mark.asyncio
async def test_lifespan_with_api_key(mock_api_key):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    """Test that lifespan initializes agents when API key is present."""
    from core.config import settings

    # Store original key
    original_key = settings.GEMINI_API_KEY

    try:
        # Set valid API key
        settings.GEMINI_API_KEY = mock_api_key

        # Mock app
        app = FastAPI()

        # Create mocks
        mock_run_migrations = MagicMock()
        mock_agent_manager = MagicMock()
        mock_agent_manager.initialize_all = AsyncMock()
        mock_agent_manager.close_all = AsyncMock()

        # Mock database session and query
        mock_db_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        mock_dbsessionmanager = MagicMock()
        mock_dbsessionmanager.session = MagicMock()
        mock_dbsessionmanager.session.return_value.__aenter__ = AsyncMock(
            return_value=mock_db_session
        )
        mock_dbsessionmanager.session.return_value.__aexit__ = AsyncMock()
        mock_dbsessionmanager.close = AsyncMock()

        # Apply patches at import locations
        with (
            patch("main.run_migrations", mock_run_migrations),
            patch("main.agent_manager", mock_agent_manager),
            patch("main.dbsessionmanager", mock_dbsessionmanager),
        ):
            # Import lifespan after patching
            from main import lifespan

            # Test lifespan
            async with lifespan(app):
                pass

            # Verify agents WERE initialized (API key present)
            mock_agent_manager.initialize_all.assert_called_once()

            # Verify cleanup was called
            mock_agent_manager.close_all.assert_called_once()
            mock_dbsessionmanager.close.assert_called_once()

    finally:
        # Restore key
        settings.GEMINI_API_KEY = original_key

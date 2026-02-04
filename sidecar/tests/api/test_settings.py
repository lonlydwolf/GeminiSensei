from unittest.mock import patch

import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_update_api_key(client: AsyncClient):
    # Store original key
    original_key = settings.GEMINI_API_KEY

    try:
        # We need to mock set_key to avoid writing to actual .env during test
        with patch("routers.app_settings.set_key") as mock_set_key:
            response = await client.post("/api/settings/api-key", json={"api_key": "test_key_123"})

            assert response.status_code == 200
            assert response.json()["success"] is True
            assert settings.GEMINI_API_KEY == "test_key_123"
            mock_set_key.assert_called_once()

    finally:
        # Restore key
        settings.GEMINI_API_KEY = original_key


@pytest.mark.asyncio
async def test_update_api_key_empty(client: AsyncClient):
    response = await client.post("/api/settings/api-key", json={"api_key": "  "})

    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]

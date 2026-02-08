from unittest.mock import patch

import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_update_api_key(client: AsyncClient):
    # Store original key
    original_key = settings.GEMINI_API_KEY
    # Use a valid format key for validation logic (starts with AIza, len 39)
    valid_key = "AIza" + "0" * 35

    try:
        # We need to mock set_key to avoid writing to actual .env during test
        from unittest.mock import AsyncMock, MagicMock

        with (
            patch("routers.app_settings.set_key") as mock_set_key,
            patch("routers.app_settings.gemini_service.update_api_key") as mock_update_key,
            patch("routers.app_settings.genai.Client") as MockGenaiClient,
        ):
            # Configure the mock to simulate a successful API call
            mock_client_instance = MockGenaiClient.return_value
            # The validation logic calls await client.aio.models.generate_content
            # We mock the async call by using AsyncMock
            mock_client_instance.aio.models.generate_content = AsyncMock(
                return_value=MagicMock(text="success")
            )

            response = await client.post("/api/settings/api-key", json={"api_key": valid_key})

            assert response.status_code == 200
            assert response.json()["success"] is True
            assert settings.GEMINI_API_KEY == valid_key
            mock_set_key.assert_called_once()
            mock_update_key.assert_called_once_with(valid_key)

    finally:
        # Restore key
        settings.GEMINI_API_KEY = original_key


@pytest.mark.asyncio
async def test_update_api_key_empty(client: AsyncClient):
    response = await client.post("/api/settings/api-key", json={"api_key": "  "})

    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]

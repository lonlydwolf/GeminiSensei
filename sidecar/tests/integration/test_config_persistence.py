from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_api_key_persistence_path(client: AsyncClient):
    """Test that the API key is written to the correct platform-specific path."""
    test_key = "AIza" + "0" * 35

    # Store original key to restore later
    original_key = settings.GEMINI_API_KEY

    try:
        from unittest.mock import AsyncMock, MagicMock

        with (
            patch("services.key_manager.set_key") as mock_set_key,
            patch("services.key_manager.genai.Client") as MockGenaiClient,
        ):
            # Configure the mock to simulate a successful API call
            mock_client_instance = MockGenaiClient.return_value
            mock_client_instance.aio.models.generate_content = AsyncMock(
                return_value=MagicMock(text="success")
            )

            # Act
            response = await client.post("/api/settings/api-key", json={"api_key": test_key})

            # Assert
            assert response.status_code == 200

            # The first argument to set_key is the path
            # We want it to be settings.BASE_DIR / ".env"
            called_path = Path(mock_set_key.call_args[0][0]).absolute()
            expected_path = (settings.BASE_DIR / ".env").absolute()

            assert called_path == expected_path, f"Expected {expected_path}, but got {called_path}"
    finally:
        settings.GEMINI_API_KEY = original_key


@pytest.mark.asyncio
async def test_settings_loads_from_correct_path():
    """Verify that Settings class is configured to load from the platform data dir."""
    # This checks the pydantic configuration
    # Currently it is just ".env"
    env_file = settings.model_config.get("env_file")

    # We want this to be the absolute path to the data dir .env
    expected_env_file = str(settings.BASE_DIR / ".env")

    assert env_file == expected_env_file

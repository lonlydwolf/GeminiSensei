from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_status_no_key(client: AsyncClient, temp_test_dir):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    """Test settings status when no API key is set."""
    # Create a mock settings object with all needed attributes
    mock_settings_obj = MagicMock()
    mock_settings_obj.GEMINI_API_KEY = ""
    mock_settings_obj.ENV_FILE_PATH = temp_test_dir / ".env"
    mock_settings_obj.DEBUG = False

    # Patch settings where it's accessed in the function
    with patch("routers.app_settings.settings", mock_settings_obj):
        response = await client.get("/api/settings/status")
        assert response.status_code == 200
        data = response.json()
        assert data["gemini_api_key_set"] is False
        assert data["gemini_api_key_valid"] is False


@pytest.mark.asyncio
async def test_get_status_with_key(client: AsyncClient, temp_test_dir):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    """Test settings status when API key is set."""
    # Use a properly formatted mock API key
    valid_mock_key = "AIzaSyDummyTestKey123456789012345678901"

    mock_env_path = temp_test_dir / ".env"  # pyright: ignore[reportUnknownVariableType]
    # Create the file so exists() returns True
    mock_env_path.touch()

    # Create a mock settings object
    mock_settings_obj = MagicMock()
    mock_settings_obj.GEMINI_API_KEY = valid_mock_key
    mock_settings_obj.ENV_FILE_PATH = mock_env_path
    mock_settings_obj.DEBUG = False

    with patch("routers.app_settings.settings", mock_settings_obj):
        response = await client.get("/api/settings/status")
        assert response.status_code == 200
        data = response.json()
        assert data["gemini_api_key_set"] is True
        assert data["gemini_api_key_valid"] is True


@pytest.mark.asyncio
async def test_update_api_key_success(client: AsyncClient, temp_test_dir):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    """Test successful API key update."""
    # Use a properly formatted mock API key
    valid_mock_key = "AIzaSyDummyTestKey123456789012345678901"
    mock_env_path = temp_test_dir / ".env"  # pyright: ignore[reportUnknownVariableType]

    # Mock key_manager
    mock_key_manager_obj = MagicMock()
    mock_key_manager_obj.validate_format.return_value = True
    mock_key_manager_obj.verify_key = AsyncMock()
    mock_key_manager_obj.save_key.return_value = mock_env_path

    # Mock settings
    mock_settings_obj = MagicMock()
    mock_settings_obj.DEBUG = False

    # We need to mock the agent_manager import inside the function
    # Create a mock module for agents.manager
    mock_agent_manager_obj = MagicMock()
    mock_agent_manager_obj._is_initialized = False
    mock_agent_manager_obj.initialize_all = AsyncMock()

    # Patch at the point of use
    with (
        patch("routers.app_settings.key_manager", mock_key_manager_obj),
        patch("routers.app_settings.settings", mock_settings_obj),
        patch("agents.manager.agent_manager", mock_agent_manager_obj),
    ):
        # Make request
        response = await client.post("/api/settings/api-key", json={"api_key": valid_mock_key})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["details"]["validated"] is True
        assert data["details"]["agents_initialized"] is True

        # Verify key was verified and saved
        mock_key_manager_obj.verify_key.assert_called_once_with(valid_mock_key)
        mock_key_manager_obj.save_key.assert_called_once_with(valid_mock_key)

        # Verify agents were initialized
        mock_agent_manager_obj.initialize_all.assert_called_once()


@pytest.mark.asyncio
async def test_update_api_key_agents_already_initialized(client: AsyncClient, temp_test_dir):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    """Test API key update when agents are already initialized."""
    valid_mock_key = "AIzaSyDummyTestKey123456789012345678901"
    mock_env_path = temp_test_dir / ".env"  # pyright: ignore[reportUnknownVariableType]

    # Mock key_manager
    mock_key_manager_obj = MagicMock()
    mock_key_manager_obj.validate_format.return_value = True
    mock_key_manager_obj.verify_key = AsyncMock()
    mock_key_manager_obj.save_key.return_value = mock_env_path

    # Mock settings
    mock_settings_obj = MagicMock()
    mock_settings_obj.DEBUG = False

    # Mock agent_manager as already initialized
    mock_agent_manager_obj = MagicMock()
    mock_agent_manager_obj._is_initialized = True
    mock_agent_manager_obj.initialize_all = AsyncMock()

    with (
        patch("routers.app_settings.key_manager", mock_key_manager_obj),
        patch("routers.app_settings.settings", mock_settings_obj),
        patch("agents.manager.agent_manager", mock_agent_manager_obj),
    ):
        response = await client.post("/api/settings/api-key", json={"api_key": valid_mock_key})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Agents should NOT be re-initialized
        mock_agent_manager_obj.initialize_all.assert_not_called()


@pytest.mark.asyncio
async def test_update_api_key_invalid_format(client: AsyncClient):
    """Test API key update with invalid format."""
    mock_key_manager_obj = MagicMock()
    mock_key_manager_obj.validate_format.return_value = False

    with patch("routers.app_settings.key_manager", mock_key_manager_obj):
        response = await client.post("/api/settings/api-key", json={"api_key": "invalid_key"})

        assert response.status_code == 400
        data = response.json()
        assert "Invalid API key format" in data["detail"]


@pytest.mark.asyncio
async def test_update_api_key_empty(client: AsyncClient):
    """Test API key update with empty key."""
    response = await client.post("/api/settings/api-key", json={"api_key": ""})

    assert response.status_code == 400
    data = response.json()
    assert "cannot be empty" in data["detail"]


@pytest.mark.asyncio
async def test_update_api_key_verification_fails(client: AsyncClient):
    """Test API key update when verification fails."""
    valid_format_key = "AIzaSyDummyTestKey1234567890123456789"

    mock_key_manager_obj = MagicMock()
    mock_key_manager_obj.validate_format.return_value = True
    mock_key_manager_obj.verify_key = AsyncMock(side_effect=ValueError("Invalid API key"))

    with patch("routers.app_settings.key_manager", mock_key_manager_obj):
        response = await client.post("/api/settings/api-key", json={"api_key": valid_format_key})

        assert response.status_code == 400
        data = response.json()
        assert "Invalid API key" in data["detail"]


@pytest.mark.asyncio
async def test_reset_application(client: AsyncClient, temp_test_dir):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    """Test application reset endpoint."""
    # Create fake files
    db_path = temp_test_dir / "gemini_sensei.db"  # pyright: ignore[reportUnknownVariableType]
    db_path.touch()

    mock_dbsessionmanager_obj = MagicMock()
    mock_dbsessionmanager_obj.close = AsyncMock()
    mock_dbsessionmanager_obj.model_post_init = MagicMock()

    mock_settings_obj = MagicMock()
    mock_settings_obj.BASE_DIR = temp_test_dir
    mock_settings_obj.ENV_FILE_PATH = temp_test_dir / ".env"

    mock_run_migrations = MagicMock()

    with (
        patch("routers.app_settings.dbsessionmanager", mock_dbsessionmanager_obj),
        patch("routers.app_settings.settings", mock_settings_obj),
        patch("routers.app_settings.run_migrations", mock_run_migrations),
    ):
        response = await client.delete("/api/settings/reset?include_key=false")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify cleanup was called
        mock_dbsessionmanager_obj.close.assert_called_once()


@pytest.mark.asyncio
async def test_reset_application_with_key(client: AsyncClient, temp_test_dir):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    """Test application reset including API key."""
    # Create fake files
    db_path = temp_test_dir / "gemini_sensei.db"  # pyright: ignore[reportUnknownVariableType]
    db_path.touch()
    env_path = temp_test_dir / ".env"  # pyright: ignore[reportUnknownVariableType]
    env_path.touch()

    mock_dbsessionmanager_obj = MagicMock()
    mock_dbsessionmanager_obj.close = AsyncMock()
    mock_dbsessionmanager_obj.model_post_init = MagicMock()

    mock_settings_obj = MagicMock()
    mock_settings_obj.BASE_DIR = temp_test_dir
    mock_settings_obj.ENV_FILE_PATH = env_path
    mock_settings_obj.GEMINI_API_KEY = "test_key"

    mock_run_migrations = MagicMock()

    with (
        patch("routers.app_settings.dbsessionmanager", mock_dbsessionmanager_obj),
        patch("routers.app_settings.settings", mock_settings_obj),
        patch("routers.app_settings.run_migrations", mock_run_migrations),
    ):
        response = await client.delete("/api/settings/reset?include_key=true")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify env file would be deleted (it was touched in temp_dir)
        # and API key was cleared
        assert mock_settings_obj.GEMINI_API_KEY == ""

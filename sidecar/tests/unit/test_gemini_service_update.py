from unittest.mock import MagicMock, patch

import pytest

from services.gemini_service import GeminiService


@pytest.mark.asyncio
async def test_update_api_key_reinitializes_client():
    """Test that update_api_key re-initializes the google-genai Client with the new key."""
    with (
        patch("google.genai.Client") as MockClient,
        patch("services.gemini_service.settings") as mock_settings,
    ):
        mock_settings.GEMINI_API_KEY = "initial-key"
        # Configure MockClient to return different objects on each call
        mock_client1 = MagicMock(name="client1")
        mock_client2 = MagicMock(name="client2")
        MockClient.side_effect = [mock_client1, mock_client2]

        # Initialize service (will call MockClient with initial key from settings)
        service = GeminiService()
        initial_client = service.client
        assert initial_client == mock_client1

        # Act: Update with a new key
        new_key = "new-dynamic-key-123"
        service.update_api_key(new_key)

        # Assert: A new client was created
        assert service.client == mock_client2
        assert service.client != initial_client

        # Assert: MockClient was called correctly
        assert MockClient.call_count == 2
        last_call_args = MockClient.call_args
        assert last_call_args.kwargs["api_key"] == new_key

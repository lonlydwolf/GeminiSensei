from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.gemini_service import GeminiService


@pytest.mark.asyncio
async def test_generate_content_success():
    # Mock the google-genai Client
    with patch("google.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_client.aio.models.generate_content = AsyncMock()

        # Setup mock response
        mock_response = MagicMock()
        mock_response.text = "Mocked Response"
        mock_client.aio.models.generate_content.return_value = mock_response

        service = GeminiService()
        result = await service.generate_content("Hello")

        assert result == "Mocked Response"
        mock_client.aio.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_content_stream_success():
    with patch("google.genai.Client") as MockClient:
        mock_client = MockClient.return_value

        # Setup mock stream
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Part 1"
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "Part 2"

        async def mock_async_iterator():
            yield mock_chunk1
            yield mock_chunk2

        # In the service, it's: async_stream = await client.aio.models.generate_content_stream(...)
        # So the mocked function must be an async function that returns an async iterator
        mock_client.aio.models.generate_content_stream = AsyncMock(
            return_value=mock_async_iterator()
        )

        service = GeminiService()
        chunks = []
        async for chunk in service.generate_content_stream("Hello"):
            chunks.append(chunk)

        assert chunks == ["Part 1", "Part 2"]


@pytest.mark.asyncio
async def test_generate_content_error():
    with patch("google.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_client.aio.models.generate_content.side_effect = Exception("API Error")

        service = GeminiService()
        with pytest.raises(Exception, match="API Error"):
            _ = await service.generate_content("Hello")

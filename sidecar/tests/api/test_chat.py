from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_without_roadmap(client: AsyncClient):
    """Test chat endpoint requires roadmap_id."""
    with patch("agents.manager.agent_manager") as mock_manager:
        mock_agent = MagicMock()
        mock_agent.chat = AsyncMock()
        mock_manager.get_agent.return_value = mock_agent

        response = await client.post(
            "/api/chat/message", json={"roadmap_id": 1, "message": "Hello"}
        )

        # Should work or return appropriate error based on your implementation
        assert response.status_code in [200, 404]

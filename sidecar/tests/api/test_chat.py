from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from core.types import AgentID


@pytest.mark.asyncio
async def test_chat_stream_teacher(client: AsyncClient):
    # Mock OrchestratorAgent.chat_stream
    async def mock_chat_stream(*_args: Any, **_kwargs: Any) -> AsyncIterator[str]:
        yield "Hello"
        yield " Student"

    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        mock_agent = MagicMock()
        mock_agent.chat_stream.side_effect = mock_chat_stream
        mock_get_agent.return_value = mock_agent

        payload = {"lesson_id": "l-1", "message": "Hi"}
        response = await client.post("/api/chat/stream", json=payload)

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        # Collect streaming results
        content = ""
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                content += line[6:]

        assert content == "Hello Student"
        # Router calls get_agent with ORCHESTRATOR by default
        mock_get_agent.assert_called_with(AgentID.ORCHESTRATOR)


@pytest.mark.asyncio
async def test_chat_stream_review_command(client: AsyncClient):
    async def mock_chat_stream(*_args: Any, **_kwargs: Any) -> AsyncIterator[str]:
        yield "Critique"

    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        mock_agent = MagicMock()
        mock_agent.chat_stream.side_effect = mock_chat_stream
        mock_get_agent.return_value = mock_agent

        payload = {"lesson_id": "l-1", "message": "/review print(1)"}

        response = await client.post("/api/chat/stream", json=payload)
        assert response.status_code == 200

        content = ""
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                content += line[6:]
        assert "Critique" in content

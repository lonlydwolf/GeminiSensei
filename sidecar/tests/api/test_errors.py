from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_stream_not_initialized(client: AsyncClient):
    with patch(
        "agents.manager.agent_manager.get_agent", side_effect=RuntimeError("Not initialized")
    ):
        payload = {"lesson_id": "l-1", "message": "Hi"}
        response = await client.post("/api/chat/stream", json=payload)
        assert response.status_code == 503


@pytest.mark.asyncio
async def test_chat_stream_empty_review(client: AsyncClient):
    payload = {"lesson_id": "l-1", "message": "/review"}
    response = await client.post("/api/chat/stream", json=payload)
    assert response.status_code == 200

    content = ""
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            content += line[6:]
    assert "Please provide code after /review command." in content


@pytest.mark.asyncio
async def test_submit_review_wrong_agent_type(client: AsyncClient):
    with patch("agents.manager.agent_manager.get_agent", return_value=MagicMock()):
        payload = {"lesson_id": "l-1", "code": "pass", "language": "python"}
        # Routers do an isinstance check. If we return a generic mock,
        # it might fail or behave weirdly.
        # But we can force it to return something that fails the check.
        from agents.teacher.agent import TeacherAgent

        with patch("agents.manager.agent_manager.get_agent") as mock_get:
            mock_get.return_value = MagicMock(spec=TeacherAgent)
            response = await client.post("/api/review/submit", json=payload)
            assert response.status_code == 503

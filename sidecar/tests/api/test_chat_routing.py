from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from core.types import AgentID
from main import SIDECAR_SECRET, app


@pytest.fixture
def client():
    return TestClient(app, headers={"X-Sidecar-Token": SIDECAR_SECRET})


def test_chat_stream_routing_to_teacher(client: TestClient):
    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        # Mocking the teacher agent
        mock_agent = MagicMock()

        async def mock_chat_stream(*_: object, **_kwargs: object):
            yield "Hello from teacher"

        mock_agent.chat_stream.side_effect = mock_chat_stream
        mock_get_agent.return_value = mock_agent

        response = client.post(
            "/api/chat/stream",
            json={"lesson_id": "test", "message": "hello", "agent_id": "teacher"},
        )
        assert response.status_code == 200
        mock_get_agent.assert_called_with(AgentID.TEACHER)


def test_chat_stream_routing_to_reviewer(client: TestClient):
    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        # Mocking the reviewer agent
        mock_agent = MagicMock()

        async def mock_chat_stream(*_: object, **_kwargs: object):
            yield "Reviewing code..."

        mock_agent.chat_stream.side_effect = mock_chat_stream
        mock_get_agent.return_value = mock_agent

        response = client.post(
            "/api/chat/stream",
            json={"lesson_id": "test", "message": "review this", "agent_id": "reviewer"},
        )
        assert response.status_code == 200
        mock_get_agent.assert_called_with(AgentID.REVIEWER)


def test_chat_stream_default_routing(client: TestClient):
    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        mock_agent = MagicMock()

        async def mock_chat_stream(*_: object, **_kwargs: object):
            yield "Default"

        mock_agent.chat_stream.side_effect = mock_chat_stream
        mock_get_agent.return_value = mock_agent

        # No agent_id provided
        response = client.post("/api/chat/stream", json={"lesson_id": "test", "message": "hi"})
        assert response.status_code == 200
        mock_get_agent.assert_called_with(AgentID.ORCHESTRATOR)

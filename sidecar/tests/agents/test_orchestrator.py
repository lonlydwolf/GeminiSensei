from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.orchestrator.agent import OrchestratorAgent


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = OrchestratorAgent(MagicMock(), MagicMock(), MagicMock())
    await orchestrator.initialize()
    assert orchestrator.graph is not None


@pytest.mark.asyncio
async def test_orchestrator_routing_teacher():
    orchestrator = OrchestratorAgent(MagicMock(), MagicMock(), MagicMock())
    await orchestrator.initialize()

    mock_teacher = AsyncMock()
    mock_teacher.chat.return_value = "I am teaching"

    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        # Mocking AgentRegistry as well if needed, but agent_manager should be enough
        mock_get_agent.return_value = mock_teacher

        # We also need to mock agent_registry.get_agent_class to return a class with get_config
        with patch("agents.agent_registry.agent_registry.get_agent_class") as mock_get_class:
            mock_class = MagicMock()
            mock_class.get_config.return_value = {
                "agent_id": "teacher",
                "name": "Teacher",
                "description": "desc",
                "capabilities": ["cap"],
                "icon": "icon",
            }
            mock_get_class.return_value = mock_class

            # Test routing for generic message
            response = await orchestrator.chat("thread1", "hello", MagicMock())
            assert response == "I am teaching"
            mock_get_agent.assert_called_with("teacher")


@pytest.mark.asyncio
async def test_orchestrator_routing_reviewer():
    orchestrator = OrchestratorAgent(MagicMock(), MagicMock(), MagicMock())
    await orchestrator.initialize()

    mock_reviewer = AsyncMock()
    mock_reviewer.chat.return_value = "I am reviewing"

    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        mock_get_agent.return_value = mock_reviewer

        with patch("agents.agent_registry.agent_registry.get_agent_by_command") as mock_get_by_cmd:
            mock_class = MagicMock()
            mock_class.get_config.return_value = {
                "agent_id": "reviewer",
                "name": "Reviewer",
                "description": "desc",
                "capabilities": ["cap"],
                "icon": "icon",
            }
            mock_get_by_cmd.return_value = mock_class

            with patch("agents.agent_registry.agent_registry.get_agent_class") as mock_get_class:
                mock_get_class.return_value = mock_class

                # Test routing for /review command
                response = await orchestrator.chat("thread1", "/review code", MagicMock())
                assert response == "I am reviewing"
                mock_get_agent.assert_called_with("reviewer")


@pytest.mark.asyncio
async def test_orchestrator_error_handling():
    orchestrator = OrchestratorAgent(MagicMock(), MagicMock(), MagicMock())
    await orchestrator.initialize()

    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        mock_get_agent.side_effect = Exception("Agent failure")


@pytest.mark.asyncio
async def test_orchestrator_chat_stream():
    orchestrator = OrchestratorAgent(MagicMock(), MagicMock(), MagicMock())
    await orchestrator.initialize()

    async def mock_async_generator(*_args: Any, **_kwargs: Any):
        yield "chunk1"
        yield "chunk2"

    mock_teacher = MagicMock()
    mock_teacher.chat_stream.side_effect = mock_async_generator

    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        mock_get_agent.return_value = mock_teacher

        with patch("agents.agent_registry.agent_registry.get_agent_class") as mock_get_class:
            mock_class = MagicMock()
            mock_class.get_config.return_value = {
                "agent_id": "teacher",
                "name": "Teacher",
                "description": "desc",
                "capabilities": ["cap"],
                "icon": "icon",
            }
            mock_get_class.return_value = mock_class

            chunks = []
            async for chunk in orchestrator.chat_stream("thread1", "hello", MagicMock()):
                chunks.append(chunk)

            assert chunks == ["chunk1", "chunk2"]
            mock_get_agent.assert_called_with("teacher")

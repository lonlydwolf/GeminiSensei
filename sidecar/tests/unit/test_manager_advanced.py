from unittest.mock import AsyncMock

import pytest

from agents.base import BaseAgent
from agents.manager import AgentManager


@pytest.mark.asyncio
async def test_agent_manager_close_all():
    manager = AgentManager()
    mock_agent = AsyncMock(spec=BaseAgent)
    manager._agents["test"] = mock_agent  # pyright: ignore[reportPrivateUsage]

    await manager.close_all()
    mock_agent.close.assert_called_once()
    assert len(manager._agents) == 0  # pyright: ignore[reportPrivateUsage]


@pytest.mark.asyncio
async def test_agent_manager_initialize_error():
    manager = AgentManager()
    mock_agent = AsyncMock(spec=BaseAgent)
    mock_agent.initialize.side_effect = Exception("Init error")
    manager._agents["test"] = mock_agent  # pyright: ignore[reportPrivateUsage]

    # Should log error but not crash
    await manager.initialize_all()
    mock_agent.initialize.assert_called_once()

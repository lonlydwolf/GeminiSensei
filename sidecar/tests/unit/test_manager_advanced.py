from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from agents.base import BaseAgent
from agents.manager import AgentManager
from core.types import AgentID


@pytest.mark.asyncio
async def test_agent_manager_close_all():
    manager = AgentManager()
    mock_agent = AsyncMock(spec=BaseAgent)
    manager._agent_instances[AgentID.TEACHER.value] = mock_agent  # pyright: ignore[reportPrivateUsage]

    await manager.close_all()
    mock_agent.close.assert_called_once()
    assert len(manager._agent_instances) == 0  # pyright: ignore[reportPrivateUsage]


@pytest.mark.asyncio
async def test_agent_manager_initialize_error():
    manager = AgentManager()
    mock_agent = AsyncMock(spec=BaseAgent)
    mock_agent.initialize.side_effect = Exception("Init error")

    with patch("agents.manager.agent_registry") as mock_registry:
        mock_registry.get_all_agent_ids.return_value = ["test_agent"]

        def mock_agent_class(**_kwargs: Any) -> Any:
            return mock_agent

        mock_registry.get_agent_class.return_value = mock_agent_class

        # Should log error but not crash
        await manager.initialize_all()
        mock_agent.initialize.assert_called_once()

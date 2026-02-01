from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from agents.base import BaseAgent
from database.session import DBSessionManager


class MockAgent(BaseAgent):
    @override
    async def initialize(self) -> None:
        pass

    @override
    async def chat(self, thread_id: str, message: str, db: AsyncSession) -> str:
        return ""

    @override
    async def chat_stream(
        self, thread_id: str, message: str, db: AsyncSession
    ) -> AsyncIterator[str]:
        # Need to be an async generator to satisfy AsyncIterator[str]
        yield ""

    @override
    async def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_base_agent_interface():
    agent = MockAgent()
    assert await agent.initialize() is None
    # Use dummy values
    assert await agent.chat("", "", None) == ""  # pyright: ignore[reportArgumentType]
    assert agent.chat_stream("", "", None) is not None  # pyright: ignore[reportArgumentType]
    assert await agent.close() is None


@pytest.mark.asyncio
async def test_db_session_manager_close():
    from unittest.mock import AsyncMock

    manager = DBSessionManager()
    # Mock engine
    mock_engine = AsyncMock()
    manager._engine = mock_engine  # pyright: ignore[reportPrivateUsage]
    await manager.close()
    mock_engine.dispose.assert_called_once()

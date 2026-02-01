from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage
from sqlalchemy.ext.asyncio import AsyncSession

from agents.teacher.agent import TeacherAgent


@pytest.mark.asyncio
async def test_teacher_agent_chat(mock_gemini_service: MagicMock, db_session: AsyncSession):
    agent = TeacherAgent(gemini_service=mock_gemini_service, db_manager=MagicMock())

    # Mock workflow.ainvoke
    mock_workflow = AsyncMock()
    mock_workflow.ainvoke.return_value = {"messages": [AIMessage(content="Response")]}
    agent._workflow = mock_workflow  # pyright: ignore[reportPrivateUsage]

    response = await agent.chat(thread_id="l1", message="Hi", db=db_session)
    assert response == "Response"
    mock_workflow.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_teacher_agent_chat_stream(mock_gemini_service: MagicMock, db_session: AsyncSession):
    agent = TeacherAgent(gemini_service=mock_gemini_service, db_manager=MagicMock())

    # Mock workflow.astream_events
    async def mock_events(*_args: Any, **_kwargs: Any) -> Any:
        yield {"event": "on_custom_event", "name": "socratic_token", "data": {"token": "Hi"}}

    mock_workflow = MagicMock()
    mock_workflow.astream_events.side_effect = mock_events
    agent._workflow = mock_workflow  # pyright: ignore[reportPrivateUsage]

    tokens: list[str] = []
    async for token in agent.chat_stream(thread_id="l1", message="Hi", db=db_session):
        tokens.append(token)

    assert tokens == ["Hi"]

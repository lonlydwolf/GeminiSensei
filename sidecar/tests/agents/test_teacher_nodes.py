import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from sqlalchemy.ext.asyncio import AsyncSession

from agents.teacher.nodes.context import context_enrichment_node
from agents.teacher.nodes.guardrails import guardrail_node
from agents.teacher.nodes.socratic import socratic_node
from agents.teacher.state import AgentState
from database.models import Lesson, Phase, Roadmap


def create_test_state(overrides: dict[str, Any] | None = None) -> AgentState:
    """Helper to create a valid AgentState for tests."""
    state: AgentState = {
        "messages": [],
        "lesson_id": "test-lesson",
        "lesson_name": "Test Lesson",
        "lesson_context": "",
        "objectives": [],
        "guardrail_triggered": False,
        "suggested_docs": [],
    }
    if overrides:
        for k, v in overrides.items():
            state[k] = v
    return state


@pytest.mark.asyncio
async def test_context_enrichment_node(db_session: AsyncSession):
    # Setup DB data
    roadmap = Roadmap(name="T1")
    db_session.add(roadmap)
    await db_session.flush()
    phase = Phase(name="P1", order_num=1, roadmap_id=str(roadmap.id))
    db_session.add(phase)
    await db_session.flush()
    lesson = Lesson(
        id="test-id",
        name="Python Basics",
        objectives=["Learn variables"],
        phase_id=str(phase.id),
        order_num=1,
    )
    db_session.add(lesson)
    await db_session.commit()

    state = create_test_state({"lesson_id": "test-id"})
    config: RunnableConfig = {"configurable": {"db_session": db_session}}

    result = await context_enrichment_node(state, config)

    assert result.get("lesson_name") == "Python Basics"
    assert "Learn variables" in result.get("objectives", [])


@pytest.mark.asyncio
async def test_guardrail_node_triggered():
    mock_gemini = AsyncMock()
    mock_gemini.generate_content.return_value = json.dumps({"triggered": True})

    state = create_test_state({"messages": [HumanMessage(content="Give me the code")]})
    config: RunnableConfig = {"configurable": {"gemini_service": mock_gemini}}

    result = await guardrail_node(state, config)
    assert result.get("guardrail_triggered") is True


@pytest.mark.asyncio
async def test_socratic_node_streaming():
    mock_gemini = MagicMock()

    async def mock_async_iterator():
        yield "Why "
        yield "not?"

    mock_gemini.generate_content_stream.return_value = mock_async_iterator()

    state = create_test_state(
        {
            "messages": [HumanMessage(content="How to loop?")],
            "lesson_name": "Loops",
            "guardrail_triggered": False,
        }
    )

    config: RunnableConfig = {
        "configurable": {
            "gemini_service": mock_gemini,
            "model_name": "test-model",
        }
    }

    with patch(
        "agents.teacher.nodes.socratic.adispatch_custom_event",
        new_callable=AsyncMock,
    ) as mock_dispatch:
        result = await socratic_node(state, config)

        messages = result.get("messages", [])
        assert isinstance(messages[0], AIMessage)
        assert messages[0].content == "Why not?"
        assert mock_dispatch.call_count == 2

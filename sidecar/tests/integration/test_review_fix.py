import json
from unittest.mock import AsyncMock, patch, MagicMock
from typing import cast, Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agents.code_reviewer.agent import CodeReviewerAgent
from database.models import CodeReview, Lesson, Phase, Roadmap
from agents.code_reviewer.nodes.guardrails import guardrail_node
from agents.code_reviewer.state import CodeReviewerState


@pytest.mark.asyncio
async def test_chat_creates_review_record(client: AsyncClient, db_session: AsyncSession):
    """Verify that using /review command creates a DB record."""
    # Setup dependencies
    roadmap = Roadmap(name="R1")
    db_session.add(roadmap)
    await db_session.flush()
    phase = Phase(name="P1", order_num=1, roadmap_id=str(roadmap.id))
    db_session.add(phase)
    await db_session.flush()
    lesson = Lesson(name="L1", order_num=1, phase_id=str(phase.id))
    db_session.add(lesson)
    await db_session.commit()

    lesson_id = str(lesson.id)

    # Mock the agent so we don't actually run the LLM
    async def mock_review_stream(*_args: Any, **_kwargs: Any):
        yield "Thinking..."

    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        mock_agent = AsyncMock(spec=CodeReviewerAgent)
        mock_agent.review.side_effect = mock_review_stream
        mock_get_agent.return_value = mock_agent

        # Act
        payload = {"lesson_id": lesson_id, "message": "/review print('test')"}
        response = await client.post("/api/chat/stream", json=payload)

        # Assert API success
        assert response.status_code == 200

        # Assert DB record created
        # This will FAIL currently because chat.py uses a fake ID
        stmt = select(CodeReview).where(CodeReview.lesson_id == lesson_id)
        result = await db_session.execute(stmt)
        record = result.scalar_one_or_none()

        assert record is not None, "CodeReview record should be created in DB"
        assert record.code_content == "print('test')"


@pytest.mark.asyncio
async def test_guardrail_checks_code_content():
    """Verify guardrail checks the actual code content, not just the message."""
    mock_gemini = AsyncMock()
    mock_gemini.generate_content.return_value = json.dumps({"triggered": False})

    # Setup state with malicious code but innocent message
    state = cast(
        CodeReviewerState,
        {
            "messages": [HumanMessage(content="Please review my code")],
            "code_content": "MALICIOUS_CODE_SIGNATURE",
            "language": "python",
        },
    )

    config = cast(RunnableConfig, {"configurable": {"gemini_service": mock_gemini}})

    await guardrail_node(state, config)

    # Check what was passed to the LLM
    call_args = mock_gemini.generate_content.call_args
    prompt_sent = call_args.kwargs.get("prompt", "")

    # This assertion will FAIL if we only check messages[-1].content
    assert "MALICIOUS_CODE_SIGNATURE" in prompt_sent

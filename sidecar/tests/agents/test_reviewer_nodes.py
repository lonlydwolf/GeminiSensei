import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.runnables import RunnableConfig
from sqlalchemy.ext.asyncio import AsyncSession

from agents.code_reviewer.nodes.analysis import code_analysis_node
from agents.code_reviewer.nodes.enrichment import context_enrichment_node
from agents.code_reviewer.nodes.socratic import socratic_review_node
from agents.code_reviewer.state import CodeReviewerState
from core.types import CodeReviewStatus
from database.models import CodeReview, Lesson, Phase, Roadmap


def create_test_state(overrides: dict[str, Any] | None = None) -> CodeReviewerState:
    """Helper to create a valid CodeReviewerState for tests."""
    state: CodeReviewerState = {
        "messages": [],
        "lesson_id": "test-lesson",
        "review_id": "test-review",
        "code_content": "",
        "language": "python",
        "lesson_name": "Test Lesson",
        "objectives": [],
        "findings": [],
        "guardrail_triggered": False,
    }
    if overrides:
        for k, v in overrides.items():
            state[k] = v
    return state


@pytest.mark.asyncio
async def test_reviewer_enrichment_node(db_session: AsyncSession):
    roadmap = Roadmap(name="R1")
    db_session.add(roadmap)
    await db_session.flush()
    phase = Phase(name="P1", order_num=1, roadmap_id=str(roadmap.id))
    db_session.add(phase)
    await db_session.flush()
    lesson = Lesson(
        id="rev-id",
        name="Code Style",
        objectives=["Clean code"],
        phase_id=str(phase.id),
        order_num=1,
    )
    db_session.add(lesson)
    await db_session.commit()

    state = create_test_state({"lesson_id": "rev-id"})
    # RunnableConfig is a TypedDict too, but loosely defined
    config: RunnableConfig = {"configurable": {"db_session": db_session}}

    result = await context_enrichment_node(state, config)
    assert result.get("lesson_name") == "Code Style"


@pytest.mark.asyncio
async def test_code_analysis_node(db_session: AsyncSession):
    mock_gemini = AsyncMock()
    mock_gemini.generate_content.return_value = json.dumps(
        {
            "findings": [
                {
                    "line_number": 1,
                    "category": "Style",
                    "observation": "Too long",
                    "socratic_question": "Can it be shorter?",
                }
            ]
        }
    )

    # Create CodeReview record
    review = CodeReview(id="rev-1", lesson_id="l-1", code_content="...", language="python")
    db_session.add(review)
    await db_session.commit()

    state = create_test_state(
        {
            "lesson_name": "Test",
            "code_content": "print('x')",
            "review_id": "rev-1",
        }
    )
    config: RunnableConfig = {
        "configurable": {"gemini_service": mock_gemini, "db_session": db_session}
    }

    result = await code_analysis_node(state, config)

    findings = result.get("findings", [])
    assert len(findings) == 1
    assert findings[0]["category"] == "Style"


@pytest.mark.asyncio
async def test_reviewer_socratic_node(db_session: AsyncSession):
    mock_gemini = MagicMock()

    async def mock_async_iterator():
        yield "Review result"

    mock_gemini.generate_content_stream.return_value = mock_async_iterator()

    review = CodeReview(id="rev-2", lesson_id="l-1", code_content="...", language="python")
    db_session.add(review)
    await db_session.commit()

    state = create_test_state(
        {
            "lesson_name": "Test",
            "review_id": "rev-2",
        }
    )

    config: RunnableConfig = {
        "configurable": {
            "gemini_service": mock_gemini,
            "db_session": db_session,
        }
    }

    with patch(
        "agents.code_reviewer.nodes.socratic.adispatch_custom_event",
        new_callable=AsyncMock,
    ) as mock_dispatch:
        result = await socratic_review_node(state, config)
        # Type safe access
        messages = result.get("messages", [])
        assert "Review result" in str(messages[0].content)
        assert mock_dispatch.call_count == 1

    # Check DB update
    await db_session.refresh(review)
    assert review.status == CodeReviewStatus.COMPLETED
    assert review.feedback == "Review result"

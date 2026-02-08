from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agents.code_reviewer.agent import CodeReviewerAgent
from services.lesson_service import LessonContextService


@pytest.mark.asyncio
async def test_reviewer_agent_review(mock_gemini_service: MagicMock, db_session: AsyncSession):
    agent = CodeReviewerAgent(
        gemini_service=mock_gemini_service,
        db_manager=MagicMock(),
        lesson_service=MagicMock(spec=LessonContextService),
    )

    async def mock_events(*_args: Any, **_kwargs: Any) -> Any:
        yield {"event": "on_custom_event", "name": "review_token", "data": {"token": "Feedback"}}

    mock_workflow = MagicMock()
    mock_workflow.astream_events.side_effect = mock_events
    agent._workflow = mock_workflow  # pyright: ignore[reportPrivateUsage]

    tokens: list[str] = []
    async for token in agent.review(
        review_id="r1", lesson_id="l1", code="print(1)", language="python", db=db_session
    ):
        tokens.append(token)

    assert tokens == ["Feedback"]


@pytest.mark.asyncio
async def test_reviewer_agent_chat(mock_gemini_service: MagicMock, db_session: AsyncSession):
    agent = CodeReviewerAgent(
        gemini_service=mock_gemini_service,
        db_manager=MagicMock(),
        lesson_service=MagicMock(spec=LessonContextService),
    )

    # Mock ReviewService
    with patch("services.review_service.ReviewService.submit_review") as mock_submit:

        async def mock_generator(*_args: Any, **_kwargs: Any) -> Any:
            yield "token1"
            yield "token2"

        mock_submit.side_effect = mock_generator

        response = await agent.chat("t1", "hi", db_session)
        assert response == "token1token2"
        mock_submit.assert_called_once()

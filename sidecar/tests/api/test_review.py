from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.code_reviewer.agent import CodeReviewerAgent
from database.models import CodeReview


@pytest.mark.asyncio
async def test_submit_review_api(client: AsyncClient, db_session: AsyncSession):
    async def mock_review_stream(*_args: Any, **_kwargs: Any) -> AsyncIterator[str]:
        yield "Feedback"

    with patch("agents.manager.agent_manager.get_agent") as mock_get_agent:
        mock_agent = AsyncMock(spec=CodeReviewerAgent)
        mock_agent.review.side_effect = mock_review_stream
        mock_get_agent.return_value = mock_agent

        payload = {"lesson_id": "l-1", "code": "def f(): pass", "language": "python"}

        response = await client.post("/api/review/submit", json=payload)
        assert response.status_code == 200

        content = ""
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                content += line[6:]
        assert content == "Feedback"

        # Verify DB record
        stmt = select(CodeReview).where(CodeReview.lesson_id == "l-1")
        res = await db_session.execute(stmt)
        review = res.scalar_one()
        assert review.language == "python"
        assert review.code_content == "def f(): pass"

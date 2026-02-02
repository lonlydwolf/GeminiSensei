from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agents.code_reviewer.agent import CodeReviewerAgent
from services.review_service import ReviewService


@pytest.mark.asyncio
async def test_submit_review_success():
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    mock_agent = AsyncMock(spec=CodeReviewerAgent)
    
    # Mock the streaming response from agent
    async def mock_review_stream(*_args: Any, **_kwargs: Any):
        yield "Chunk 1"
        yield "Chunk 2"
    
    mock_agent.review.side_effect = mock_review_stream

    with patch("services.review_service.agent_manager") as mock_manager:
        mock_manager.get_agent.return_value = mock_agent
        
        service = ReviewService()
        
        # Act
        tokens = []
        async for token in service.submit_review(
            lesson_id="lesson-123",
            code="print('hello')",
            language="python",
            db=mock_db
        ):
            tokens.append(token)
            
        # Assert
        assert tokens == ["Chunk 1", "Chunk 2"]
        # Verify DB add/commit was called (to create the CodeReview record)
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
        
        # Verify agent was called with correct ID
        # (we can't easily check the generated UUID, but we verify call happened)
        mock_agent.review.assert_called_once()
        call_kwargs = mock_agent.review.call_args.kwargs
        assert call_kwargs["lesson_id"] == "lesson-123"
        assert call_kwargs["code"] == "print('hello')"
        assert call_kwargs["language"] == "python"
        assert call_kwargs["db"] == mock_db


@pytest.mark.asyncio
async def test_submit_review_agent_error():
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    
    with patch("services.review_service.agent_manager") as mock_manager:
        mock_manager.get_agent.side_effect = RuntimeError("Agent not initialized")
        
        service = ReviewService()
        
        # Act & Assert
        with pytest.raises(RuntimeError):
            async for _ in service.submit_review(
                lesson_id="l1", code="c", language="py", db=mock_db
            ):
                pass

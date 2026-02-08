import uuid
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Protocol, cast

from sqlalchemy.ext.asyncio import AsyncSession

from core.types import AgentID, CodeReviewStatus
from database.models import CodeReview


class ReviewableAgent(Protocol):
    """Protocol for agents that support the review method."""

    def review(
        self, review_id: str, lesson_id: str, code: str, language: str, db: AsyncSession
    ) -> AsyncIterator[str]:
        """Specific method for code review streaming."""
        ...


class ReviewService:
    """Service for handling code review submissions."""

    async def submit_review(
        self, lesson_id: str, code: str, language: str, db: AsyncSession
    ) -> AsyncGenerator[str, None]:
        """
        Submits code for review, persists the record, and streams the AI response.

        Args:
            lesson_id: ID of the lesson being reviewed.
            code: The code content.
            language: Programming language.
            db: Database session.

        Yields:
            Chunks of the review feedback.
        """
        from agents.manager import agent_manager

        # 1. Create DB record
        review_id = str(uuid.uuid4())
        review_record = CodeReview(
            id=review_id,
            lesson_id=lesson_id,
            code_content=code,
            language=language,
            status=CodeReviewStatus.PENDING,
        )
        db.add(review_record)
        await db.commit()
        await db.refresh(review_record)

        # 2. Get Agent
        agent = agent_manager.get_agent(AgentID.REVIEWER)

        # 3. Stream Response
        # Note: In a real scenario, we might want to update the review record with the feedback
        # status after completion, but for now we follow the existing pattern.
        # We use a Protocol to avoid direct dependency on CodeReviewerAgent class
        if not hasattr(agent, "review"):
            yield f"[ERROR] Agent '{AgentID.REVIEWER}' does not support review method"
            return

        review_agent = cast(ReviewableAgent, cast(object, agent))

        async for chunk in review_agent.review(
            review_id=review_id,
            lesson_id=lesson_id,
            code=code,
            language=language,
            db=db,
        ):
            yield chunk

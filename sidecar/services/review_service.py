import uuid
from collections.abc import AsyncGenerator
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from agents.code_reviewer.agent import CodeReviewerAgent
from agents.manager import agent_manager
from core.types import AgentID, CodeReviewStatus
from database.models import CodeReview


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
        agent = cast(CodeReviewerAgent, agent_manager.get_agent(AgentID.REVIEWER))

        # 3. Stream Response
        # Note: In a real scenario, we might want to update the review record with the feedback
        # status after completion, but for now we follow the existing pattern.
        async for chunk in agent.review(
            review_id=review_id,
            lesson_id=lesson_id,
            code=code,
            language=language,
            db=db,
        ):
            yield chunk

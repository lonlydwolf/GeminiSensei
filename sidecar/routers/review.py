"""Review API endpoint."""

import logging
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agents.manager import agent_manager
from core.types import CodeReviewStatus
from database.models import CodeReview
from database.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/review", tags=["review"])

db_dep = Annotated[AsyncSession, Depends(get_db)]


class ReviewRequest(BaseModel):
    lesson_id: str
    code: str
    language: str


@router.post("/submit")
async def submit_review(request: ReviewRequest, db: db_dep):
    """Submit code for review (streaming)."""

    # 1. Create a CodeReview record
    review_id = str(uuid.uuid4())
    review = CodeReview(
        id=review_id,
        lesson_id=request.lesson_id,
        code_content=request.code,
        language=request.language,
        status=CodeReviewStatus.PENDING,
    )
    db.add(review)
    await db.commit()

    try:
        agent = agent_manager.get_agent("reviewer")
        # Cast to specific agent type for 'review' method
        from agents.code_reviewer.agent import CodeReviewerAgent

        if not isinstance(agent, CodeReviewerAgent):
            raise RuntimeError("Wrong agent type for review")
    except RuntimeError as e:
        logger.error(f"Agent manager error: {e}")
        raise HTTPException(status_code=503, detail="Review service not initialized") from e

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for token in agent.review(
                review_id=review_id,
                lesson_id=request.lesson_id,
                code=request.code,
                language=request.language,
                db=db,
            ):
                yield f"data: {token}\n\n"
        except Exception as e:
            logger.error(f"Review streaming error: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

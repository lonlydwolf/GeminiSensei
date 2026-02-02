"""Review API endpoint."""

import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from services.review_service import ReviewService

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
    service = ReviewService()

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for token in service.submit_review(
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

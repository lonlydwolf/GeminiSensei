"""Chat API endpoint."""

import logging
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agents.manager import agent_manager
from core.types import CodeReviewStatus
from database.models import CodeReview
from database.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

db_dep = Annotated[AsyncSession, Depends(get_db)]


class ChatRequest(BaseModel):
    lesson_id: str
    message: str


@router.post("/stream")
async def chat_stream(request: ChatRequest, db: db_dep):
    """Chat with the teacher agent (streaming).

    Args:
        request: Chat request containing lesson_id and message
        db: Database session

    Returns:
        StreamingResponse (Server-Sent Events)
    """
    message_text = request.message.strip()

    # Check for /review command
    if message_text.startswith("/review"):
        # This is a bit simplified; ideally we'd extract code from the message or
        # tell the user to use the Submit button.
        # For now, let's route to the reviewer if code is provided in the message.
        code_part = message_text[len("/review") :].strip()
        if not code_part:

            async def error_generator():
                yield "data: Please provide code after /review command.\n\n"

            return StreamingResponse(error_generator(), media_type="text/event-stream")

        try:
            from agents.code_reviewer.agent import CodeReviewerAgent

            agent = agent_manager.get_agent("reviewer")
            # Create a CodeReview record
            review_id = str(uuid.uuid4())
            review = CodeReview(
                id=review_id,
                lesson_id=request.lesson_id,
                code_content=code_part,
                language="python",
                status=CodeReviewStatus.PENDING,
            )
            db.add(review)
            await db.commit()

            if not isinstance(agent, CodeReviewerAgent):
                raise RuntimeError("Invalid agent type")

            async def event_generator() -> AsyncGenerator[str, None]:
                try:
                    # Default to python if not specified, or try to detect
                    # Use cast or type checking to satisfy LSP
                    reviewer = cast(CodeReviewerAgent, agent)
                    async for token in reviewer.review(
                        review_id=review_id,
                        lesson_id=request.lesson_id,
                        code=code_part,
                        language="python",
                        db=db,
                    ):
                        yield f"data: {token}\n\n"

                except Exception as e:
                    logger.error(f"Command review error: {e}")
                    yield f"data: [ERROR] {str(e)}\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")
        except Exception as e:
            logger.error(f"Review agent retrieval error: {e}")

    try:
        agent = agent_manager.get_agent("teacher")
    except RuntimeError as e:
        logger.error(f"Agent manager error: {e}")
        raise HTTPException(status_code=503, detail="Chat service not initialized") from e

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for token in agent.chat_stream(request.lesson_id, request.message, db):
                # Format as Server-Sent Event data
                yield f"data: {token}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

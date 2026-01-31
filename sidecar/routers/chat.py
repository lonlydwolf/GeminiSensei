"""Chat API endpoint."""

import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agents.teacher.manager import agent_manager
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
    try:
        agent = agent_manager.get_agent()
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

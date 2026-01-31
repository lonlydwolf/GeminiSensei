from __future__ import annotations

import logging
from typing import cast

from langchain_core.runnables import RunnableConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.teacher.state import AgentState
from database.models import Lesson
from database.session import DBSessionManager

logger = logging.getLogger(__name__)


async def context_enrichment_node(
    state: AgentState, config: RunnableConfig
) -> dict[str, str | list[str]]:
    """Fetches lesson metadata and documentation links from the database.

    Args:
        state: Current execution state.
        config: Runtime configuration containing dependencies.

    Returns:
        Updated state fields: lesson_name, lesson_context, objectives, suggested_docs.
    """
    lesson_id = state.get("lesson_id")
    if not lesson_id:
        logger.warning("No lesson_id found in state")
        return {}

    # Extract database session from config
    configurable = config.get("configurable", {})
    db_session: AsyncSession | None = configurable.get("db_session")

    # If db_session is missing, check for db_manager (fallback/safety)
    if not db_session:
        db_manager: DBSessionManager | None = configurable.get("db_manager")
        if db_manager:
            # If we only have the manager, we must create a new session
            # This is a fallback path and shouldn't be the primary one
            try:
                async with db_manager.session() as session:
                    return await _fetch_context(session, lesson_id)
            except Exception as e:
                logger.error(f"Error in context_enrichment_node (fallback): {e}")
                raise

        logger.error("No db_session or db_manager found in config['configurable']")
        raise RuntimeError("db_session dependency is required")

    try:
        # Use existing session directly
        return await _fetch_context(db_session, lesson_id)

    except Exception as e:
        logger.error(f"Error in context_enrichment_node: {e}")
        # Re-raise to allow the graph caller to handle the failure
        raise


async def _fetch_context(db: AsyncSession, lesson_id: str) -> dict[str, str | list[str]]:
    """Helper to fetch context using a provided session/connection."""

    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()

    if not lesson:
        logger.error(f"Lesson {lesson_id} not found in database")
        raise ValueError(f"Lesson {lesson_id} not found")

    metadata = lesson.metadata_json or {}
    suggested_docs = metadata.get("documentation", [])

    # Ensure suggested_docs is a list
    if not isinstance(suggested_docs, list):
        suggested_docs = []

    result_dict: dict[str, str | list[str]] = {
        "lesson_name": str(lesson.name),
        "lesson_context": str(lesson.description or ""),
        "objectives": lesson.objectives or [],
        "suggested_docs": cast(list[str], suggested_docs),
    }
    return result_dict

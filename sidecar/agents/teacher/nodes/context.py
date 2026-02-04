from __future__ import annotations

import logging

from langchain_core.runnables import RunnableConfig
from sqlalchemy.ext.asyncio import AsyncSession

from agents.teacher.state import AgentState
from database.session import DBSessionManager
from services.lesson_service import LessonContextService

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
            try:
                async with db_manager.session() as session:
                    service_inst: LessonContextService = (
                        configurable.get("lesson_service") or LessonContextService()
                    )
                    context = await service_inst.get_context(lesson_id, session)
                    return {
                        "lesson_name": context.name,
                        "lesson_context": context.description,
                        "objectives": context.objectives,
                        "suggested_docs": context.documentation,
                    }
            except Exception as e:
                logger.error(f"Error in context_enrichment_node (fallback): {e}")
                raise

        logger.error("No db_session or db_manager found in config['configurable']")
        raise RuntimeError("db_session dependency is required")

    try:
        # Get service from config or instantiate (fallback)
        service: LessonContextService = configurable.get("lesson_service") or LessonContextService()

        context = await service.get_context(lesson_id, db_session)
        return {
            "lesson_name": context.name,
            "lesson_context": context.description,
            "objectives": context.objectives,
            "suggested_docs": context.documentation,
        }

    except Exception as e:
        logger.error(f"Error in context_enrichment_node: {e}")
        # Re-raise to allow the graph caller to handle the failure
        raise


# _fetch_context is no longer needed as it's replaced by LessonContextService

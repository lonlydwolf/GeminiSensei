import logging

from langchain_core.runnables import RunnableConfig
from sqlalchemy.ext.asyncio import AsyncSession

from services.lesson_service import LessonContextService

from ..state import CodeReviewerState

logger = logging.getLogger(__name__)


async def context_enrichment_node(
    state: CodeReviewerState, config: RunnableConfig
) -> dict[str, str | list[str]]:
    """Fetch lesson details and objectives."""
    configurable = config.get("configurable", {})
    db: AsyncSession | None = configurable.get("db_session")

    if not db:
        logger.error("No db_session found in config['configurable']")
        raise RuntimeError("db_session dependency is required")

    lesson_id = state["lesson_id"]
    service: LessonContextService = configurable.get("lesson_service") or LessonContextService()

    try:
        context = await service.get_context(lesson_id, db)
        return {
            "lesson_name": context.name,
            "objectives": context.objectives,
        }
    except Exception as e:
        logger.error(f"Enrichment error: {e}")

    return {"lesson_name": "Unknown", "objectives": []}

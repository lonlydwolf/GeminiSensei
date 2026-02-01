import logging

from langchain_core.runnables import RunnableConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Lesson

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

    try:
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        result = await db.execute(stmt)
        lesson = result.scalar_one_or_none()

        if lesson:
            return {
                "lesson_name": str(lesson.name),
                "objectives": lesson.objectives,
            }
    except Exception as e:
        logger.error(f"Enrichment error: {e}")

    return {"lesson_name": "Unknown", "objectives": []}

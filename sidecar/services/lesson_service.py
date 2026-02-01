from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import LessonError, LessonNotFoundError
from database.models import Lesson
from schemas.lesson import LessonContext


class LessonContextService:
    """
    Unified service for loading lesson context.
    Intended to be injected into agents.
    """

    async def get_context(
        self, lesson_id: str, db: AsyncSession, source: str = "db"
    ) -> LessonContext:
        """
        Main entry point for agents to fetch context.
        """
        if source != "db":
            raise LessonError(f"Unsupported source: {source}")

        try:
            stmt = select(Lesson).where(Lesson.id == lesson_id)
            result = await db.execute(stmt)
            lesson = result.scalar_one_or_none()

            if not lesson:
                raise LessonNotFoundError(f"Lesson with ID {lesson_id} not found")

            # Extract documentation from metadata_json if present
            # and provide the rest as metadata
            full_metadata = (lesson.metadata_json or {}).copy()
            documentation = full_metadata.pop("documentation", [])

            # Ensure documentation is a list
            if not isinstance(documentation, list):
                documentation = []

            return LessonContext(
                lesson_id=lesson.id,
                name=lesson.name,
                description=lesson.description or "",
                objectives=lesson.objectives or [],
                documentation=cast(list[str], documentation),
                metadata=full_metadata,
            )
        except (LessonNotFoundError, LessonError):
            raise
        except Exception as e:
            raise LessonError(f"Unexpected error loading lesson context: {str(e)}")

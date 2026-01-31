"""Roadmap Creator Agent - Generates learning roadmaps."""

import json
import logging
import uuid

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from agents.prompts import ROADMAP_CREATOR_SYSTEM, ROADMAP_CREATOR_USER_TEMPLATE
from core.types import (
    LessonStatus,
    RoadmapAIError,
    RoadmapCreateResult,
    RoadmapError,
    RoadmapStatus,
    RoadmapStructure,
    RoadmapValidationError,
)
from database.models import Lesson, Phase, Roadmap
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class RoadmapCreatorAgent:
    """Agent for creating structured learning roadmaps."""

    async def create_roadmap(
        self, goal: str, background: str, preferences: str, db: AsyncSession
    ) -> RoadmapCreateResult:
        """Create a new roadmap.

        Args:
            goal: Learning goal (e.g., "Learn Python for Data Science")
            background: User's current knowledge
            preferences: Learning style preferences
            db: Database session

        Returns:
            RoadmapCreateResult containing roadmap_id and roadmap data

        Raises:
            RoadmapError: If inputs are invalid or generation fails
        """
        # Input Validation
        if not goal or len(goal.strip()) < 10:
            raise RoadmapError("Goal must be at least 10 characters long")
        if not background or len(background.strip()) < 3:
            raise RoadmapError("Background must be at least 3 characters long")

        response = ""
        try:
            # 1. Generate roadmap structure using Gemini
            logger.info(f"Generating roadmap for goal: {goal}")

            user_prompt = ROADMAP_CREATOR_USER_TEMPLATE.format(
                goal=goal, background=background, preferences=preferences
            )

            response = await gemini_service.generate_content(
                prompt=user_prompt, system_instruction=ROADMAP_CREATOR_SYSTEM
            )

            # 2. Robust JSON extraction
            # Extract the outermost JSON object
            start = response.find("{")
            end = response.rfind("}")
            if start == -1 or end == -1 or end < start:
                logger.error(f"Could not find JSON delimiters in Gemini response: {response}")
                raise RoadmapAIError("Failed to find JSON structure in AI response")

            response_json = response[start : end + 1]
            roadmap_data = json.loads(response_json)  # pyright: ignore[reportAny]

            # 3. Validate with Pydantic
            try:
                roadmap_structure = RoadmapStructure.model_validate(roadmap_data)
            except ValidationError as e:
                logger.error(f"Validation error for generated roadmap: {e}")
                raise RoadmapValidationError(f"Generated roadmap structure is invalid: {e}") from e

            # 4. Create database records
            roadmap = Roadmap(
                id=str(uuid.uuid4()),
                name=roadmap_structure.name,
                description=roadmap_structure.description,
                goal=goal,
                status=RoadmapStatus.ACTIVE,
            )
            db.add(roadmap)

            # 5. Create phases and lessons
            for phase_idx, phase_data in enumerate(roadmap_structure.phases):
                phase = Phase(
                    id=str(uuid.uuid4()),
                    roadmap_id=roadmap.id,
                    name=phase_data.name,
                    order_num=phase_idx + 1,
                    status=LessonStatus.NOT_STARTED,
                )
                db.add(phase)

                for lesson_idx, lesson_data in enumerate(phase_data.lessons):
                    lesson = Lesson(
                        id=str(uuid.uuid4()),
                        phase_id=phase.id,
                        name=lesson_data.name,
                        description=lesson_data.description,
                        objectives=lesson_data.objectives,
                        order_num=lesson_idx + 1,
                        status=LessonStatus.NOT_STARTED,
                        metadata_json={},
                    )
                    db.add(lesson)

            # 6. Commit to database
            await db.commit()
            await db.refresh(roadmap)

            logger.info(f"Successfully created roadmap: {roadmap.id}")

            return RoadmapCreateResult(roadmap_id=roadmap.id, roadmap=roadmap_structure)

        except json.JSONDecodeError as e:
            await db.rollback()
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {response}")
            raise RoadmapAIError("AI returned invalid JSON structure") from e
        except RoadmapError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Unexpected error creating roadmap: {e}")
            raise RoadmapError(f"An unexpected error occurred: {e}") from e


# Singleton instance
roadmap_creator = RoadmapCreatorAgent()

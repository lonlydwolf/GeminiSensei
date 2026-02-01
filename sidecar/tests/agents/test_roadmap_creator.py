import json
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agents.roadmap_creator import RoadmapCreatorAgent
from core.types import RoadmapAIError, RoadmapError, RoadmapValidationError


@pytest.mark.asyncio
async def test_roadmap_creator_success(db_session: AsyncSession):
    mock_gemini = AsyncMock()
    mock_roadmap_data = {
        "name": "Python Mastery",
        "description": "Desc",
        "phases": [
            {
                "name": "Basics",
                "lessons": [{"name": "L1", "description": "...", "objectives": ["O1"]}],
            }
        ],
    }
    mock_gemini.generate_content.return_value = json.dumps(mock_roadmap_data)

    with patch("agents.roadmap_creator.gemini_service", mock_gemini):
        agent = RoadmapCreatorAgent()
        result = await agent.create_roadmap(
            goal="Learn Python for Data",
            background="Beginner",
            preferences="Practical",
            db=db_session,
        )

        assert result.roadmap.name == "Python Mastery"
        assert result.roadmap_id is not None


@pytest.mark.asyncio
async def test_roadmap_creator_invalid_input(db_session: AsyncSession):
    agent = RoadmapCreatorAgent()
    with pytest.raises(RoadmapError, match="Goal must be at least 10 characters long"):
        _ = await agent.create_roadmap("Short", "Beg", "Pref", db_session)

    with pytest.raises(RoadmapError, match="Background must be at least 3 characters long"):
        _ = await agent.create_roadmap("Valid Goal Length", "B", "Pref", db_session)


@pytest.mark.asyncio
async def test_roadmap_creator_no_delimiters(db_session: AsyncSession):
    mock_gemini = AsyncMock()
    mock_gemini.generate_content.return_value = "No JSON here"

    with patch("agents.roadmap_creator.gemini_service", mock_gemini):
        agent = RoadmapCreatorAgent()
        with pytest.raises(RoadmapAIError, match="Failed to find JSON structure"):
            _ = await agent.create_roadmap("Learn Python for Data", "Beginner", "Pref", db_session)


@pytest.mark.asyncio
async def test_roadmap_creator_malformed_json(db_session: AsyncSession):
    mock_gemini = AsyncMock()
    mock_gemini.generate_content.return_value = "{ 'name': 'invalid' "  # Unclosed

    with patch("agents.roadmap_creator.gemini_service", mock_gemini):
        agent = RoadmapCreatorAgent()
        # The logic finds no delimiters if they are unbalanced or missing
        with pytest.raises(RoadmapAIError, match="Failed to find JSON structure"):
            _ = await agent.create_roadmap("Learn Python for Data", "Beginner", "Pref", db_session)


@pytest.mark.asyncio
async def test_roadmap_creator_validation_error(db_session: AsyncSession):
    mock_gemini = AsyncMock()
    mock_gemini.generate_content.return_value = json.dumps({"name": "Missing Phases"})

    with patch("agents.roadmap_creator.gemini_service", mock_gemini):
        agent = RoadmapCreatorAgent()
        with pytest.raises(RoadmapValidationError):
            _ = await agent.create_roadmap("Learn Python for Data", "Beginner", "Pref", db_session)

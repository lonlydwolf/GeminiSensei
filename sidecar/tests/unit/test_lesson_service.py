from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from core.exceptions import LessonError, LessonNotFoundError
from database.models import Lesson
from services.lesson_service import LessonContextService


@pytest.mark.asyncio
async def test_get_context_success():
    # Arrange
    mock_db = AsyncMock()
    lesson_id = "test-lesson-id"
    mock_lesson = Lesson(
        id=lesson_id,
        name="Test Lesson",
        description="Test Description",
        objectives=["Obj 1", "Obj 2"],
        metadata_json={"documentation": ["Doc 1", "Doc 2"], "other": "data"},
    )

    # Mock the execute result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_lesson
    mock_db.execute.return_value = mock_result

    service = LessonContextService()

    # Act
    context = await service.get_context(lesson_id, mock_db)

    # Assert
    assert context.lesson_id == lesson_id
    assert context.name == "Test Lesson"
    assert context.description == "Test Description"
    assert context.objectives == ["Obj 1", "Obj 2"]
    assert context.documentation == ["Doc 1", "Doc 2"]
    assert context.metadata == {"other": "data"}


@pytest.mark.asyncio
async def test_get_context_handles_malformed_documentation():
    # Arrange
    mock_db = AsyncMock()
    lesson_id = "test-lesson-id"
    mock_lesson = Lesson(
        id=lesson_id,
        name="Test Lesson",
        description="Test Description",
        objectives=["Obj 1", "Obj 2"],
        # Documentation is a string instead of a list
        metadata_json={"documentation": "malformed documentation", "other": "data"},
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_lesson
    mock_db.execute.return_value = mock_result

    service = LessonContextService()

    # Act
    context = await service.get_context(lesson_id, mock_db)

    # Assert
    assert context.documentation == []
    assert context.metadata == {"other": "data"}


@pytest.mark.asyncio
async def test_get_context_not_found():
    # Arrange
    mock_db = AsyncMock()
    lesson_id = "non-existent"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    service = LessonContextService()

    # Act & Assert
    with pytest.raises(LessonNotFoundError):
        _ = await service.get_context(lesson_id, mock_db)


@pytest.mark.asyncio
async def test_get_context_db_error():
    # Arrange
    mock_db = AsyncMock()
    mock_db.execute.side_effect = SQLAlchemyError("DB Error")

    service = LessonContextService()

    # Act & Assert
    with pytest.raises(LessonError):
        _ = await service.get_context("some-id", mock_db)

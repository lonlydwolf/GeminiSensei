import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.types import CodeReviewStatus, RoadmapStatus
from database.models import CodeReview, CodeReviewFinding, Lesson, Phase, Roadmap


@pytest.mark.asyncio
async def test_create_and_get_roadmap(db_session: AsyncSession):
    # Create
    roadmap = Roadmap(
        name="Test Roadmap",
        description="A test roadmap",
        goal="Testing",
        status=RoadmapStatus.ACTIVE,
    )
    db_session.add(roadmap)
    await db_session.commit()

    # Retrieve
    stmt = select(Roadmap).where(Roadmap.name == "Test Roadmap")
    result = await db_session.execute(stmt)
    retrieved = result.scalar_one()

    assert retrieved.name == "Test Roadmap"
    assert retrieved.status == RoadmapStatus.ACTIVE
    assert retrieved.id is not None


@pytest.mark.asyncio
async def test_roadmap_phases_relationship(db_session: AsyncSession):
    roadmap = Roadmap(name="Roadmap with Phases")
    db_session.add(roadmap)
    await db_session.flush()  # Get ID

    phase = Phase(name="Phase 1", order_num=1, roadmap_id=roadmap.id)
    db_session.add(phase)
    await db_session.commit()

    # Use selectinload for async relationship access
    stmt = select(Roadmap).options(selectinload(Roadmap.phases)).where(Roadmap.id == roadmap.id)
    res = await db_session.execute(stmt)
    retrieved = res.scalar_one()
    assert len(retrieved.phases) == 1
    assert retrieved.phases[0].name == "Phase 1"


@pytest.mark.asyncio
async def test_code_review_models(db_session: AsyncSession):
    roadmap = Roadmap(name="Review Test")
    db_session.add(roadmap)
    await db_session.flush()

    phase = Phase(name="Phase 1", order_num=1, roadmap_id=roadmap.id)
    db_session.add(phase)
    await db_session.flush()

    lesson = Lesson(name="Lesson 1", order_num=1, phase_id=phase.id)
    db_session.add(lesson)
    await db_session.flush()

    review = CodeReview(
        lesson_id=lesson.id,
        code_content="print('hello')",
        language="python",
        status=CodeReviewStatus.PENDING,
    )
    db_session.add(review)
    await db_session.flush()

    finding = CodeReviewFinding(
        review_id=review.id,
        category="Style",
        observation="Good code",
        socratic_question="How can you improve it?",
    )
    db_session.add(finding)
    await db_session.commit()

    # Verify
    stmt = (
        select(CodeReview)
        .options(selectinload(CodeReview.findings))
        .where(CodeReview.id == review.id)
    )
    res = await db_session.execute(stmt)
    retrieved_review = res.scalar_one()

    assert retrieved_review.code_content == "print('hello')"
    assert len(retrieved_review.findings) == 1
    assert retrieved_review.findings[0].category == "Style"

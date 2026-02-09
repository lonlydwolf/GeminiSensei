from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Lesson, Phase, Roadmap


@pytest.mark.asyncio
async def test_get_roadmap_persistence(client: AsyncClient, db_session: AsyncSession):
    # 1. Setup Data
    roadmap = Roadmap(
        id="test-roadmap-id",
        name="Test Roadmap",
        description="A test roadmap",
        goal="Learn Testing",
        status="active",
        created_at=datetime.now(timezone.utc),
    )
    phase = Phase(
        id="test-phase-id",
        name="Phase 1",
        order_num=1,
        status="not_started",
        roadmap_id=roadmap.id,
    )
    lesson = Lesson(
        id="test-lesson-id",
        name="Lesson 1",
        description="Intro",
        order_num=1,
        status="not_started",
        phase_id=phase.id,
        objectives=["obj1", "obj2"],
    )

    db_session.add(roadmap)
    db_session.add(phase)
    db_session.add(lesson)
    await db_session.commit()

    # 2. Call API
    response = await client.get(f"/api/roadmap/{roadmap.id}")

    # 3. Assert
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == roadmap.id
    assert data["name"] == roadmap.name
    assert len(data["phases"]) == 1
    assert data["phases"][0]["id"] == phase.id
    assert len(data["phases"][0]["lessons"]) == 1
    assert data["phases"][0]["lessons"][0]["id"] == lesson.id
    assert data["phases"][0]["lessons"][0]["name"] == lesson.name

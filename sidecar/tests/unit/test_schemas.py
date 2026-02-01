from pydantic import ValidationError

from core.types import (
    CodeReviewStatus,
    LessonStatus,
    LessonStructure,
    PhaseStructure,
    RoadmapCreateRequest,
    RoadmapStructure,
)
from schemas.models import LessonCreate, PhaseCreate, RoadmapCreate


def test_roadmap_create_request_valid():
    request = RoadmapCreateRequest(
        goal="Learn Python for Data Analysis",
        background="Beginner",
        preferences="Hands-on projects",
    )
    assert request.goal == "Learn Python for Data Analysis"
    assert request.background == "Beginner"
    assert request.preferences == "Hands-on projects"


def test_roadmap_create_request_invalid_goal():
    try:
        _ = RoadmapCreateRequest(goal="Short")  # min_length=10
    except ValidationError:
        pass


def test_roadmap_structure_validation():
    structure = RoadmapStructure(
        name="Python Data Mastery",
        description="A comprehensive path.",
        phases=[
            PhaseStructure(
                name="Basics",
                lessons=[
                    LessonStructure(name="Intro", description="Start here", objectives=["Goal 1"])
                ],
            )
        ],
    )
    assert structure.name == "Python Data Mastery"
    assert len(structure.phases) == 1
    assert structure.phases[0].lessons[0].name == "Intro"


def test_code_review_status_enum():
    assert CodeReviewStatus.PENDING == "pending"
    assert CodeReviewStatus.COMPLETED == "completed"
    assert CodeReviewStatus.FAILED == "failed"


def test_lesson_status_enum():
    assert LessonStatus.NOT_STARTED == "not_started"
    assert LessonStatus.IN_PROGRESS == "in_progress"
    assert LessonStatus.COMPLETED == "completed"


def test_roadmap_create_schema():
    schema = RoadmapCreate(name="New Roadmap", description="Desc", goal="Goal", status="active")
    assert schema.name == "New Roadmap"


def test_phase_create_schema():
    schema = PhaseCreate(name="Phase 1", order_num=1, status="not_started", roadmap_id="uuid-1")
    assert schema.name == "Phase 1"


def test_lesson_create_schema():
    schema = LessonCreate(
        name="Lesson 1",
        description="Learn something",
        objectives=["Obj 1"],
        order_num=1,
        status="not_started",
        time_spent=0,
        metadata_json={"key": "value"},
        phase_id="phase-uuid",
    )
    assert schema.name == "Lesson 1"
    assert schema.metadata_json["key"] == "value"

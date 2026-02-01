from enum import Enum

from pydantic import BaseModel, Field


class RoadmapStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"


class LessonStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CodeReviewStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class RoadmapError(Exception):
    """Base exception for roadmap operations."""

    pass


class RoadmapAIError(RoadmapError):
    """Exception raised when the AI fails to generate a roadmap."""

    pass


class RoadmapValidationError(RoadmapError):
    """Exception raised when the generated roadmap fails validation."""

    pass


class LessonStructure(BaseModel):
    name: str = Field(description="The name of the lesson")
    description: str = Field(description="What the student will learn in this lesson")
    objectives: list[str] = Field(
        description="List of specific objectives in the lesson", default_factory=list
    )


class PhaseStructure(BaseModel):
    name: str = Field(description="The name of the phase")
    lessons: list[LessonStructure] = Field(
        description="List of lessons included in this phase", default_factory=list
    )


class RoadmapStructure(BaseModel):
    name: str = Field(description="The title of the roadmap")
    description: str = Field(description="Brief 2-3 sentence description of the roadmap")
    phases: list[PhaseStructure] = Field(
        description="List of phases that make up the roadmap", default_factory=list
    )


class RoadmapCreateResult(BaseModel):
    roadmap_id: str = Field(description="Unique identifier for the created roadmap")
    roadmap: RoadmapStructure = Field(description="The structure of the created roadmap")


class RoadmapCreateRequest(BaseModel):
    goal: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The learning goal (e.g., 'Learn Python for Data Analysis')",
    )
    background: str = Field(
        default="Beginner", min_length=2, description="Student's background knowledge"
    )
    preferences: str = Field(
        default="Hands-on, practical projects", description="Learning style preferences"
    )


class RoadmapResponse(BaseModel):
    roadmap_id: str
    message: str

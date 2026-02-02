from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class AppBaseModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class LessonBase(AppBaseModel):
    name: str
    description: str | None = None
    objectives: list[str] = Field(default_factory=list)
    order_num: int
    status: str = "not_started"
    time_spent: int = 0
    metadata_json: dict[str, JsonValue] = Field(default_factory=dict)
    phase_id: str


class LessonRead(LessonBase):
    id: str


class LessonCreate(LessonBase):
    pass


class PhaseBase(AppBaseModel):
    name: str
    order_num: int
    status: str = "not_started"
    roadmap_id: str


class PhaseRead(PhaseBase):
    id: str


class PhaseCreate(PhaseBase):
    pass


class RoadmapBase(AppBaseModel):
    name: str
    description: str | None
    goal: str | None
    status: str = Field(default="active")


class RoadmapRead(RoadmapBase):
    id: str
    created_at: datetime


class RoadmapCreate(RoadmapBase):
    pass


class LessonReadDetailed(LessonRead):
    phase: PhaseRead | None = None


class PhaseReadDetailed(PhaseRead):
    lessons: list[LessonRead] = Field(default_factory=list)


class RoadmapReadDetailed(RoadmapRead):
    phases: list[PhaseReadDetailed] = Field(default_factory=list)


# Models moved from core.types
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

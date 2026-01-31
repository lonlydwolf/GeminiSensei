from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

JSONValue = str | int | float | bool | None | dict[str, "JSONValue"] | list["JSONValue"]


class AppBaseModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class LessonBase(AppBaseModel):
    name: str
    description: str | None = None
    objectives: list[str] = Field(default_factory=list)
    order_num: int
    status: str = "not_started"
    time_spent: int = 0
    metadata_json: dict[str, JSONValue] = Field(default={})
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

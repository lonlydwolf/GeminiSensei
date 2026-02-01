from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class LessonContext(BaseModel):
    """
    Immutable lesson context used by agents.
    Follows project standards for immutability and type safety.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, from_attributes=True)

    lesson_id: str
    name: str
    description: str
    objectives: list[str] = Field(default_factory=list)
    documentation: list[str] = Field(default_factory=list)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

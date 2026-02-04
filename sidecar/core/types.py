from enum import Enum
from typing import TypedDict


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


class AgentID(str, Enum):
    TEACHER = "teacher"
    REVIEWER = "reviewer"


class AgentMetadata(TypedDict):
    id: str
    name: str
    description: str
    icon: str


class RoadmapError(Exception):
    """Base exception for roadmap operations."""

    pass


class RoadmapAIError(RoadmapError):
    """Exception raised when the AI fails to generate a roadmap."""

    pass


class RoadmapValidationError(RoadmapError):
    """Exception raised when the generated roadmap fails validation."""

    pass

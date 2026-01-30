import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.types import LessonStatus, RoadmapStatus


class Base(DeclarativeBase):
    pass


JSONValue = str | int | float | bool | None | dict[str, "JSONValue"] | list["JSONValue"]


class Roadmap(Base):
    __tablename__: str = "roadmaps"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    goal: Mapped[str | None] = mapped_column(Text)
    status: Mapped[RoadmapStatus] = mapped_column(
        SQLEnum(RoadmapStatus), default=RoadmapStatus.ACTIVE, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    phases: Mapped[list["Phase"]] = relationship(
        "Phase", back_populates="roadmap", cascade="all, delete-orphan"
    )


class Phase(Base):
    __tablename__: str = "phases"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    roadmap_id: Mapped[str] = mapped_column(ForeignKey("roadmaps.id"), index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    order_num: Mapped[int] = mapped_column(Integer)
    status: Mapped[LessonStatus] = mapped_column(
        SQLEnum(LessonStatus), default=LessonStatus.NOT_STARTED, index=True
    )

    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="phases")
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", back_populates="phase", cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__: str = "lessons"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phase_id: Mapped[str] = mapped_column(ForeignKey("phases.id"), index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    objectives: Mapped[list[str]] = mapped_column(MutableList.as_mutable(JSON), default=list)
    order_num: Mapped[int] = mapped_column(Integer)
    status: Mapped[LessonStatus] = mapped_column(
        SQLEnum(LessonStatus), default=LessonStatus.NOT_STARTED, index=True
    )
    time_spent: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[dict[str, JSONValue]] = mapped_column(MutableDict.as_mutable(JSON))

    phase: Mapped["Phase"] = relationship("Phase", back_populates="lessons")

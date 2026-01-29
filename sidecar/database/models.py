import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

JSONValue = str | int | float | bool | None | dict[str, "JSONValue"] | list["JSONValue"]


class Roadmap(Base):
    __tablename__: str = "roadmaps"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    goal: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    phases: Mapped[list["Phase"]] = relationship(
        "Phase", back_populates="roadmap", cascade="all, delete-orphan"
    )


class Phase(Base):
    __tablename__: str = "phases"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    roadmap_id: Mapped[str] = mapped_column(ForeignKey("roadmaps.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    order_num: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="not_started")

    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="phases")
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", back_populates="phase", cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__: str = "lessons"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phase_id: Mapped[str] = mapped_column(ForeignKey("phases.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    objectives: Mapped[str | None] = mapped_column(Text)
    order_num: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="not_started")
    time_spent: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[dict[str, JSONValue]] = mapped_column(MutableDict.as_mutable(JSON))

    phase: Mapped["Phase"] = relationship("Phase", back_populates="lessons")

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from database.session import DBSessionManager
    from services.gemini_service import GeminiService
    from services.lesson_service import LessonContextService


class BaseAgent(ABC):
    """Abstract base class for all specialized agents."""

    agent_id: str = ""  # Unique identifier for the agent, matched with agents.json

    def __init__(
        self,
        gemini_service: "GeminiService",
        db_manager: "DBSessionManager",
        lesson_service: "LessonContextService",
    ) -> None:
        self.gemini_service: "GeminiService" = gemini_service
        self.db_manager: "DBSessionManager" = db_manager
        self.lesson_service: "LessonContextService" = lesson_service

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources (e.g., checkpointers)."""
        pass

    @abstractmethod
    async def chat(self, thread_id: str, message: str, db: AsyncSession) -> str:
        """Process a message and return a response."""
        pass

    @abstractmethod
    async def chat_stream(
        self, thread_id: str, message: str, db: AsyncSession
    ) -> AsyncIterator[str]:
        """Process a message and yield response chunks."""
        # Empty generator for abstract method
        if False:
            yield ""  # pyright: ignore[reportUnreachable]

    @abstractmethod
    async def close(self) -> None:
        """Cleanup agent resources."""
        pass

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession


class BaseAgent(ABC):
    """Abstract base class for all specialized agents."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources (e.g., checkpointers)."""
        pass

    @abstractmethod
    async def chat(self, thread_id: str, message: str, db: AsyncSession) -> str:
        """Process a message and return a response."""
        pass

    @abstractmethod
    def chat_stream(self, thread_id: str, message: str, db: AsyncSession) -> AsyncIterator[str]:
        """Process a message and yield response chunks."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Cleanup agent resources."""
        pass

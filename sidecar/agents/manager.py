import logging
from typing import TYPE_CHECKING

from agents.base import BaseAgent
from agents.code_reviewer.agent import CodeReviewerAgent
from agents.teacher.agent import TeacherAgent
from database.session import dbsessionmanager
from services.gemini_service import gemini_service
from services.lesson_service import LessonContextService

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages the lifecycle and retrieval of specialized agents."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._is_initialized: bool = False

    async def initialize_all(self) -> None:
        """Initialize all registered agents."""
        if self._is_initialized:
            return

        # Initialize shared services
        lesson_service = LessonContextService()

        # Initialize the teacher agent if not present
        if "teacher" not in self._agents:
            self._agents["teacher"] = TeacherAgent(
                gemini_service=gemini_service,
                db_manager=dbsessionmanager,
                lesson_service=lesson_service,
            )

        if "reviewer" not in self._agents:
            self._agents["reviewer"] = CodeReviewerAgent(
                gemini_service=gemini_service,
                db_manager=dbsessionmanager,
                lesson_service=lesson_service,
            )

        # Initialize all agents
        for name, agent in self._agents.items():
            try:
                await agent.initialize()
                logger.info(f"Agent '{name}' initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize agent '{name}': {e}")

        self._is_initialized = True

    def get_agent(self, name: str = "teacher") -> BaseAgent:
        """Get a specific agent instance.

        Args:
            name: Name of the agent configuration (default: "teacher")

        Returns:
            BaseAgent instance

        Raises:
            RuntimeError: If the agent has not been initialized.
        """
        if name not in self._agents:
            raise RuntimeError(
                f"Agent '{name}' has not been initialized. "
                + "Ensure 'await initialize_all()' has been called in startup."
            )

        return self._agents[name]

    async def close_all(self) -> None:
        """Close all agents and cleanup resources."""
        for name, agent in self._agents.items():
            try:
                await agent.close()
                logger.info(f"Agent '{name}' closed.")
            except Exception as e:
                logger.error(f"Error closing agent '{name}': {e}")

        self._agents.clear()
        self._is_initialized = False
        logger.info("All agents closed.")


# Singleton instance of the manager
agent_manager = AgentManager()

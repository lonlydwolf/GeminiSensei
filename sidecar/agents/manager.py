import logging
from typing import TYPE_CHECKING

from agents.base import BaseAgent
from agents.code_reviewer.agent import CodeReviewerAgent
from agents.teacher.agent import TeacherAgent
from core.types import AgentID, AgentMetadata
from database.session import dbsessionmanager
from services.gemini_service import gemini_service
from services.lesson_service import LessonContextService

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages the lifecycle and retrieval of specialized agents."""

    def __init__(self) -> None:
        self._agents: dict[AgentID, BaseAgent] = {}
        self._is_initialized: bool = False

    async def initialize_all(self) -> None:
        """Initialize all registered agents."""
        if self._is_initialized:
            return

        # Initialize shared services
        lesson_service = LessonContextService()

        # Initialize the teacher agent if not present
        if AgentID.TEACHER not in self._agents:
            self._agents[AgentID.TEACHER] = TeacherAgent(
                gemini_service=gemini_service,
                db_manager=dbsessionmanager,
                lesson_service=lesson_service,
            )

        if AgentID.REVIEWER not in self._agents:
            self._agents[AgentID.REVIEWER] = CodeReviewerAgent(
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

    def get_agent(self, name: AgentID = AgentID.TEACHER) -> BaseAgent:
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

    def get_agents_metadata(self) -> list[AgentMetadata]:
        """Get metadata for all initialized agents.

        Returns:
            List of metadata dictionaries.
        """
        metadata: list[AgentMetadata] = []
        # Hardcoded metadata mapping for now, matching the existing agents
        # In a more dynamic system, this could be part of the agent class itself
        agent_info: dict[AgentID, dict[str, str]] = {
            AgentID.TEACHER: {
                "name": "General Tutor",
                "description": "Your AI programming teacher",
                "icon": "GraduationCap",
            },
            AgentID.REVIEWER: {
                "name": "Code Reviewer",
                "description": "Specialized agent for code reviews and feedback",
                "icon": "FileCode",
            },
        }

        for agent_id in self._agents:
            info = agent_info.get(
                agent_id,
                {
                    "name": agent_id.capitalize(),
                    "description": f"The {agent_id} agent",
                    "icon": "Bot",
                },
            )
            # Create a complete metadata dict that satisfies AgentMetadata TypedDict
            metadata_item: AgentMetadata = {
                "id": agent_id.value,
                "name": info["name"],
                "description": info["description"],
                "icon": info["icon"],
            }
            metadata.append(metadata_item)

        return metadata

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

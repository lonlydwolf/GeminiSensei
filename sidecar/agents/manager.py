import logging

from agents.agent_registry import agent_registry
from agents.base import BaseAgent
from core.types import AgentConfig
from database.session import dbsessionmanager
from services.gemini_service import gemini_service
from services.lesson_service import LessonContextService

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages the lifecycle and retrieval of specialized agents."""

    def __init__(self) -> None:
        self._agent_instances: dict[str, BaseAgent] = {}
        self._is_initialized: bool = False

    async def initialize_all(self) -> None:
        """Initialize all registered agents"""
        if self._is_initialized:
            return

        # Discover agents dynamically
        agent_registry.discover_agents()

        # Initialize shared services
        lesson_service = LessonContextService()

        # Initialize all discovered agents
        for agent_id in agent_registry.get_all_agent_ids():
            agent_class = agent_registry.get_agent_class(agent_id)

            # Instantiate the agent
            agent_instance = agent_class(
                gemini_service=gemini_service,
                db_manager=dbsessionmanager,
                lesson_service=lesson_service,
            )

            self._agent_instances[agent_id] = agent_instance

            # Initialize the agent
            try:
                await agent_instance.initialize()
                logger.info(f"Agent '{agent_id}' initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize agent '{agent_id}': {e}")
        self._is_initialized = True

    def get_agent(self, agent_id: str = "teacher") -> BaseAgent:
        """Get a specific agent instance by ID."""

        if agent_id not in self._agent_instances:
            raise RuntimeError(
                f"Agent '{agent_id}' has not been initialized. "
                + "Ensure 'await initialize_all()' has been called in startup."
            )
        return self._agent_instances[agent_id]

    def get_agents_metadata(self) -> list[AgentConfig]:
        """Get metadata for all initialized agents.

        Returns:
            List of metadata dictionaries.
        """
        metadata: list[AgentConfig] = []

        for agent_id in self._agent_instances:
            agent_class = agent_registry.get_agent_class(agent_id)
            config = agent_class.get_config()

            metadata.append(config)
        return metadata

    async def close_all(self) -> None:
        """Close all agents and cleanup resources."""
        for agent_id, agent in self._agent_instances.items():
            try:
                await agent.close()
                logger.info(f"Agent '{agent_id}' closed.")
            except Exception as e:
                logger.error(f"Error closing agent '{agent_id}': {e}")
        self._agent_instances.clear()
        self._is_initialized = False
        logger.info("All agents closed.")


# Singleton instance of the manager
agent_manager = AgentManager()

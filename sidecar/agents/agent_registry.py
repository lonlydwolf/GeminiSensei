"""Dynamic agent discovery and registration system."""

import importlib
import inspect
import logging
from pathlib import Path

from agents.base import BaseAgent
from core.types import AgentConfig

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Discovers and registers agents dynamically."""

    def __init__(self):
        self._agents: dict[str, type[BaseAgent]] = {}
        self._command_map: dict[str, str] = {}  # command -> agent_id

    def discover_agents(self) -> None:
        """Auto-discover all agents in the agents/ directory."""

        agents_dir = Path(__file__).parent

        # Scan for subdirectories containing agents.py
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            if agent_dir.name.startswith("_"):
                continue

            agent_file = agent_dir / "agent.py"
            if not agent_file.exists():
                continue

            try:
                # Import the module
                module_name = f"agents.{agent_dir.name}.agent"
                module = importlib.import_module(module_name)

                # Find the agent class (should end with "Agent")
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith("Agent") and name != "BaseAgent":
                        if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                            self._register_agent(obj)
                            logger.info(f"Discovered agent: {name}")
            except Exception as e:
                logger.error(f"Failed to discover agent in {agent_dir}: {e}", exc_info=True)

    def _register_agent(self, agent_class: type[BaseAgent]) -> None:
        """Register an agent class."""
        config = agent_class.get_config()
        agent_id = config["agent_id"]

        self._agents[agent_id] = agent_class

        # Register command mapping if agent has a command
        if config["command"]:
            self._command_map[config["command"]] = agent_id

    def get_agent_class(self, agent_id: str) -> type[BaseAgent]:
        """Get agent class by ID."""
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not found in registry")
        return self._agents[agent_id]

    def get_agent_by_command(self, command: str) -> type[BaseAgent] | None:
        """Get agent class by command name."""
        agent_id = self._command_map.get(command)
        if agent_id:
            return self._agents[agent_id]
        return None

    def get_all_configs(self) -> list[AgentConfig]:
        """Get configurations for all registered agents."""
        return [cls.get_config() for cls in self._agents.values()]

    def get_all_agent_ids(self) -> list[str]:
        """Get all registered agents IDs."""
        return list(self._agents.keys())


# Singleton instance
agent_registry = AgentRegistry()

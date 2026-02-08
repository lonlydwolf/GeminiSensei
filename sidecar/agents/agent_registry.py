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
        self._metadata: dict[str, AgentConfig] = {}
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load agent metadata from resources/agents.json."""
        try:
            # Look in sidecar/resources/agents.json
            # __file__ is in sidecar/agents/agent_registry.py
            resources_dir = Path(__file__).parent.parent / "resources"
            json_path = resources_dir / "agents.json"

            if json_path.exists():
                with open(json_path, encoding="utf-8") as f:
                    import json

                    from pydantic import TypeAdapter, ValidationError

                    data = json.load(f)  # pyright: ignore[reportAny]

                    try:
                        # Validate the loaded data against the expected structure
                        # AgentConfig is a TypedDict, so we verify that the dictionary matches it
                        adapter = TypeAdapter(dict[str, AgentConfig])
                        self._metadata = adapter.validate_python(data)
                        logger.info(
                            f"Loaded and validated metadata for {len(self._metadata)} agents."
                        )
                    except ValidationError as e:
                        logger.error(f"Invalid agent metadata in {json_path}: {e}")
                        # Fallback to empty to prevent crashes, or keep existing if any
                        self._metadata = {}
            else:
                logger.warning(f"Agent metadata file not found at {json_path}")
        except Exception as e:
            logger.error(f"Failed to load agent metadata: {e}")

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
        agent_id = agent_class.agent_id

        if not agent_id:
            logger.warning(f"Agent class {agent_class.__name__} has no agent_id. Skipping.")
            return

        self._agents[agent_id] = agent_class

        # Register command mapping if agent has a command in metadata
        config = self.get_config(agent_id)
        command = config.get("command")
        if command:
            self._command_map[command] = agent_id

    def get_agent_class(self, agent_id: str) -> type[BaseAgent]:
        """Get agent class by ID."""
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not found in registry")
        return self._agents[agent_id]

    def get_config(self, agent_id: str) -> AgentConfig:
        """Get configuration for a specific agent."""
        if agent_id not in self._metadata:
            # Fallback for agents not in metadata
            return AgentConfig(
                agent_id=agent_id,
                name=agent_id.capitalize(),
                description="",
                command=None,
                capabilities=[],
                icon="User",
            )
        return self._metadata[agent_id]

    def get_agent_by_command(self, command: str) -> type[BaseAgent] | None:
        """Get agent class by command name."""
        agent_id = self._command_map.get(command)
        if agent_id:
            return self._agents[agent_id]
        return None

    def get_all_configs(self) -> list[AgentConfig]:
        """Get configurations for all registered agents."""
        return [self.get_config(agent_id) for agent_id in self._agents]

    def get_all_agent_ids(self) -> list[str]:
        """Get all registered agents IDs."""
        return list(self._agents.keys())


# Singleton instance
agent_registry = AgentRegistry()

"""Node for routing to the appropriate agent."""

import logging

from agents.agent_registry import agent_registry
from agents.orchestrator.state import OrchestratorState, PartialOrchestratorState

logger = logging.getLogger(__name__)


async def route_to_agent_node(state: OrchestratorState) -> PartialOrchestratorState:
    """Determine which agent should handle this request.

    Priority:
        1. If command detected, use command mapping
        2. Otherwise, use intent classification (TODO: add ML-based intent)
        3. Default to teacher agent
    """
    detected_command = state.get("detected_command")

    # Route by command
    if detected_command:
        agent_class = agent_registry.get_agent_by_command(detected_command)

        if agent_class:
            agent_id = agent_class.agent_id
            logger.info(f"Routing to agent '{agent_id}' via command '/{detected_command}'")
            return {"selected_agent_id": agent_id}
        else:
            logger.warning(f"Unknown command: /{detected_command}")
            return {
                "selected_agent_id": "teacher",  # Fallback
                "final_response": f"Unknown command '/{detected_command}'. Using general tutor.",
            }

    # TODO: Add intent classification here
    # For now, default to teacher
    logger.info("No command detected, routing to teacher agent")
    return {"selected_agent_id": "teacher"}

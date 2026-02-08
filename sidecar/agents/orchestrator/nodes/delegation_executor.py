"""Node for delegating to specialized agents."""

import logging

from agents.agent_registry import agent_registry
from agents.manager import agent_manager
from agents.orchestrator.state import OrchestratorState, PartialOrchestratorState
from agents.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


async def delegate_to_agent_node(state: OrchestratorState) -> PartialOrchestratorState:
    """Delegate the task to the selected agent.

    This node:
    1. Gets the selected agent instance
    2. Generates a system prompt for it
    3. Calls the agent with the user's message
    4. Returns the response
    """
    agent_id = state["selected_agent_id"]
    clean_message = state["clean_message"]

    db = state["db"]
    thread_id = state["thread_id"]

    if not agent_id:
        return {"final_response": "No agent selected. Please try again."}

    try:
        # Get the agent instance
        agent = agent_manager.get_agent(agent_id)

        # Get agent configuration
        agent_class = agent_registry.get_agent_class(agent_id)
        config = agent_class.get_config()

        # Format conversation history
        messages = state.get("messages", [])
        conversation_history = PromptTemplates.format_conversation_history(messages)

        # Generate system prompt
        system_prompt = PromptTemplates.generate_delegation_prompt(
            agent_config=config,
            user_message=clean_message,
            conversation_context=conversation_history,
        )

        logger.info(
            f"Delegating to agent '{agent_id}' with context length: {len(conversation_history)}"
        )

        # Call the agent
        # Note: We'll prepend the system prompt to the message
        enhanced_message = f"{system_prompt}\n\nUser request: {clean_message}"
        response = await agent.chat(thread_id=thread_id, message=enhanced_message, db=db)

        return {"delegated_response": response, "final_response": response}

    except Exception as e:
        logger.error(f"Error delegating to agent '{agent_id}': {e}")
        return {"final_response": f"Error processing your request: {str(e)}"}

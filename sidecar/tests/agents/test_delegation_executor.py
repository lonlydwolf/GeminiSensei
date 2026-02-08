from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agents.orchestrator.nodes.delegation_executor import delegate_to_agent_node
from agents.orchestrator.state import OrchestratorState


@pytest.mark.asyncio
async def test_delegation_context_formatting():
    # Setup state with message history
    messages: list[BaseMessage] = [
        HumanMessage(content="Hello AI"),
        AIMessage(content="Hello human! How can I help?"),
        HumanMessage(content="Tell me about python"),
    ]

    state: OrchestratorState = {
        "messages": messages,
        "current_message": "Tell me about python",
        "db": MagicMock(),
        "thread_id": "thread1",
        "detected_command": None,
        "selected_agent_id": "teacher",
        "clean_message": "Tell me about python",
        "delegation_context": {},
        "delegated_response": None,
        "final_response": "",
    }

    # Mock dependencies
    mock_agent = AsyncMock()
    mock_agent.chat.return_value = "Python is great!"

    with (
        patch("agents.manager.agent_manager.get_agent") as mock_get_agent,
        patch("agents.agent_registry.agent_registry.get_agent_class") as mock_get_class,
        patch(
            "agents.prompt_templates.PromptTemplates.generate_delegation_prompt"
        ) as mock_gen_prompt,
    ):
        mock_get_agent.return_value = mock_agent

        mock_class = MagicMock()
        mock_class.get_config.return_value = {
            "agent_id": "teacher",
            "name": "Teacher",
            "description": "desc",
            "capabilities": ["cap"],
            "icon": "icon",
        }
        mock_get_class.return_value = mock_class
        mock_gen_prompt.return_value = "System instructions"

        # Execute
        _ = await delegate_to_agent_node(state)

        # Verify that prompt generator received formatted context
        # We expect a string like:
        # "User: Hello AI\nAssistant: Hello human! How can I help?\nUser: Tell me about python"
        # Since we use the last message as current_message, it might be in the
        # history too depending on how add_messages works.

        mock_gen_prompt.assert_called_once()
        _, kwargs = mock_gen_prompt.call_args
        context = cast(str, kwargs.get("conversation_context", ""))

        assert "User: Hello AI" in context
        assert "Assistant: Hello human!" in context
        assert "User: Tell me about python" in context

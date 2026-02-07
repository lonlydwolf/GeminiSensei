"""Templates for generating system prompts for delegated agents."""

from langchain_core.messages import BaseMessage

from core.types import AgentConfig


class PromptTemplates:
    """System prompt templates for delegated agents."""

    @staticmethod
    def format_conversation_history(messages: list[BaseMessage]) -> str:
        """Format a list of LangChain messages into a string history.

        Args:
            messages: List of Human/AI messages

        Returns:
            Formatted string: "User: ... \n Assistant: ..."
        """
        history_parts: list[str] = []
        for msg in messages:
            role = "User" if msg.type == "human" else "Assistant"
            # Ensure content is string (it can be list of dicts for multimodal)
            content = msg.content if isinstance(msg.content, str) else str(msg.content)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            history_parts.append(f"{role}: {content}")

        return "\n".join(history_parts)

    @staticmethod
    def generate_delegation_prompt(
        agent_config: AgentConfig, user_message: str, conversation_context: str = ""
    ) -> str:
        """Generate a system prompt for a delegated agent.

        Args:
            agent_config: Configuration of the target agent
            user_message: The user's request
            conversation_context: Recent conversation history

        Returns:
            System prompt string
        """
        template = f"""
        You're {agent_config["name"]}, an AI assistant specialized in {agent_config["description"]}.

        Your capabilities include: {", ".join(agent_config["capabilities"])}.

        The user has specifically requested your expertise for the following task:
        {user_message}

        {f"Conversation context: {conversation_context}" if conversation_context else ""}
        Provide a helpful, accurate, and professional response focused on your area of expertise.
        """
        return template.strip()

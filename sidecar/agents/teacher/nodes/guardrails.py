import json

from langchain_core.runnables import RunnableConfig

from agents.prompts import GUARDRAIL_SYSTEM, GUARDRAIL_USER_TEMPLATE
from agents.teacher.state import AgentState
from services.gemini_service import GeminiService


async def guardrail_node(state: AgentState, config: RunnableConfig) -> dict[str, bool]:
    """Node that detects if the student is trying to bypass the Socratic method.

    Args:
        state: Current conversation state
        config: Runtime configuration containing dependencies.

    Returns:
        Update to state with guardrail_triggered status
    """
    messages = state.get("messages", [])
    if not messages:
        return {"guardrail_triggered": False}

    # Extract gemini_service from config
    configurable = config.get("configurable", {})
    gemini_service: GeminiService | None = configurable.get("gemini_service")

    if not gemini_service:
        from logging import getLogger

        getLogger(__name__).error("No gemini_service found in config['configurable']")
        raise RuntimeError("gemini_service dependency is required")

    # Get last few messages for context (last 5 messages)
    relevant_messages = messages[-5:]
    conversation_summary = ""
    for msg in relevant_messages:
        content = str(msg.content)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        role = msg.type

        conversation_summary += f"{role}: {content}\n"

    # Build prompt
    prompt = GUARDRAIL_USER_TEMPLATE.format(message=conversation_summary)

    try:
        # Generate evaluation using structured output
        response: str = await gemini_service.generate_content(
            prompt=prompt,
            system_instruction=GUARDRAIL_SYSTEM,
            response_mime_type="application/json",
        )

        # Parse JSON response
        data = json.loads(response)  # pyright: ignore[reportAny]
        triggered = bool(data.get("triggered", False))  # pyright: ignore[reportAny]

        return {"guardrail_triggered": triggered}
    except Exception as e:
        # Fallback to safe state if evaluation fails
        # In a real app, we might log this to a monitoring service
        from logging import getLogger

        getLogger(__name__).error(f"Guardrail evaluation failed: {e}")
        return {"guardrail_triggered": False}

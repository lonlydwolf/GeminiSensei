from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from agents.prompts import TEACHER_SYSTEM
from agents.teacher.state import AgentState, PartialTeacherState
from services.gemini_service import GeminiService


async def socratic_node(state: AgentState, config: RunnableConfig) -> PartialTeacherState:
    """Socratic Reasoning node that generates pedagogical responses with streaming.

    This node implements the Socratic method by asking discovery questions
    instead of providing direct code solutions. It emits tokens via custom events
    to support real-time UI updates while maintaining state integrity.
    """
    # Extract gemini_service from config
    configurable = config.get("configurable", {})
    gemini_service: GeminiService | None = configurable.get("gemini_service")

    if not gemini_service:
        from logging import getLogger

        getLogger(__name__).error("No gemini_service found in config['configurable']")
        raise RuntimeError("gemini_service dependency is required")

    messages = state.get("messages", [])
    lesson_name = state.get("lesson_name", "Unknown Lesson")
    objectives = state.get("objectives", [])
    guardrail_triggered = state.get("guardrail_triggered", False)
    lesson_context = state.get("lesson_context", "")

    # Format objectives as a bulleted list for the prompt
    formatted_objectives = "\n".join([f"- {obj}" for obj in objectives])

    # Format the system prompt with current lesson context
    system_instruction = TEACHER_SYSTEM.format(
        lesson_name=lesson_name, objectives=formatted_objectives
    )

    # Get the last user message for processing
    user_message = ""
    if messages:
        last_msg = messages[-1]
        user_message = str(last_msg.content)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]

    if guardrail_triggered:
        # If guardrails were triggered, we must refuse and redirect
        # Separate instructions from untrusted user content
        prompt = (
            "INSTRUCTION: The student has made a request that violates safety guidelines or is "
            "completely outside the educational scope of this lesson. "
            "POLITELY refuse to answer their specific request and firmly guide them "
            "back to the current lesson objectives.\n\n"
            f'STUDENT MESSAGE TO REFUSE:\n"""\n{user_message}\n"""'
        )
    else:
        # Standard Socratic guidance
        # Use delimiters to isolate user input
        prompt = (
            f"LESSON CONTEXT:\n{lesson_context}\n\n"
            "INSTRUCTION: Provide a pedagogical response following the Socratic method. "
            "Ask questions to lead them to the answer. Do not provide full code.\n\n"
            f'STUDENT MESSAGE TO RESPOND TO:\n"""\n{user_message}\n"""'
        )

    # Generate streaming response via Gemini
    full_response = ""
    async for chunk in gemini_service.generate_content_stream(
        prompt=prompt, system_instruction=system_instruction
    ):
        full_response += chunk
        # Emit token event for real-time UI
        await adispatch_custom_event("socratic_token", {"token": chunk}, config=config)

    # Return the full message to be appended to the state history
    # This triggers the LangGraph checkpointer persistence
    return {"messages": [AIMessage(content=full_response)]}

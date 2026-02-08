import json
import logging
from typing import TypedDict

from langchain_core.runnables import RunnableConfig

from agents.prompts import GUARDRAIL_SYSTEM, GUARDRAIL_USER_TEMPLATE
from services.gemini_service import GeminiService

from ..state import CodeReviewerState, PartialCodeReviewerState

logger = logging.getLogger(__name__)


class GuardrailResponse(TypedDict):
    """Typed structure for guardrail LLM response."""

    triggered: bool


async def guardrail_node(
    state: CodeReviewerState, config: RunnableConfig
) -> PartialCodeReviewerState:
    """Check if the student is bypassing the learning process."""
    configurable = config.get("configurable", {})
    gemini: GeminiService | None = configurable.get("gemini_service")

    if not gemini:
        logger.error("No gemini_service found in config['configurable']")
        raise RuntimeError("gemini_service dependency is required")

    # Prioritize checking the code content itself if available
    code_content = state.get("code_content", "")
    if code_content:
        content_to_check = f"Code submission: {code_content[:2000]}"
    else:
        messages = state.get("messages", [])
        if not messages:
            return {"guardrail_triggered": False}
        last_message = messages[-1]
        content_to_check = str(last_message.content)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]

    try:
        response = await gemini.generate_content(
            prompt=GUARDRAIL_USER_TEMPLATE.format(message=content_to_check),
            system_instruction=GUARDRAIL_SYSTEM,
            response_mime_type="application/json",
        )
        data: GuardrailResponse = json.loads(response)  # pyright: ignore[reportAny]
        return {"guardrail_triggered": bool(data.get("triggered", False))}
    except Exception as e:
        logger.error(f"Guardrail error: {e}")
        return {"guardrail_triggered": False}

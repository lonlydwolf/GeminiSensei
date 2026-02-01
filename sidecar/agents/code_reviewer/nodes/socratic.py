import json
import logging

from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.prompts import CODE_REVIEWER_SYSTEM
from core.types import CodeReviewStatus
from database.models import CodeReview
from services.gemini_service import GeminiService

from ..state import CodeReviewerState

logger = logging.getLogger(__name__)


async def socratic_review_node(
    state: CodeReviewerState, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    """Generate the Socratic feedback response."""
    configurable = config.get("configurable", {})
    gemini: GeminiService | None = configurable.get("gemini_service")
    db: AsyncSession | None = configurable.get("db_session")

    if not gemini:
        logger.error("No gemini_service found in config['configurable']")
        raise RuntimeError("gemini_service dependency is required")

    if not db:
        logger.error("No db_session found in config['configurable']")
        raise RuntimeError("db_session dependency is required")

    if state.get("guardrail_triggered"):
        return {
            "messages": [
                AIMessage(
                    content="""
                    I can't just give you the answer!
                    Let's look at your code together.
                    What part are you most unsure about?"""
                )
            ]
        }

    # Format the findings for the reviewer prompt
    findings_str = json.dumps(state["findings"], indent=2)

    system_instruction = CODE_REVIEWER_SYSTEM.format(lesson_name=state["lesson_name"])

    full_prompt = f"""
    Internal Analysis Findings:
    {findings_str}
    
    Student's Submission:
    ```{state["language"]}
    {state["code_content"]}
    ```
    
    Based on these findings, provide your Socratic review.
    """

    response_text = ""
    try:
        async for chunk in gemini.generate_content_stream(
            prompt=full_prompt,
            system_instruction=system_instruction,
        ):
            await adispatch_custom_event("review_token", {"token": chunk}, config=config)

            response_text += chunk

        # Update the CodeReview record in DB
        review_id = state["review_id"]

        stmt = select(CodeReview).where(CodeReview.id == review_id)
        result = await db.execute(stmt)
        review = result.scalar_one_or_none()
        if review:
            review.feedback = response_text
            review.status = CodeReviewStatus.COMPLETED
            await db.commit()

        return {"messages": [AIMessage(content=response_text)]}
    except Exception as e:
        logger.error(f"Reviewer node error: {e}")
        return {
            "messages": [AIMessage(content="I encountered an error while reviewing your code.")]
        }

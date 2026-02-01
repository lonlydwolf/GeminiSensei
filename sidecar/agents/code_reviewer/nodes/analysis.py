import json
import logging
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import CodeReviewFinding
from services.gemini_service import GeminiService

from ..state import CodeReviewerState

logger = logging.getLogger(__name__)


class AnalysisFinding(TypedDict):
    """Typed structure for a single code finding."""

    line_number: int | None
    category: str
    observation: str
    socratic_question: str


class AnalysisResponse(TypedDict):
    """Typed structure for the analysis LLM response."""

    findings: list[AnalysisFinding]


async def code_analysis_node(
    state: CodeReviewerState, config: RunnableConfig
) -> dict[str, list[AnalysisFinding]]:
    """Analyze the code and identify issues (internally, before Socratic feedback)."""
    configurable = config.get("configurable", {})
    gemini: GeminiService | None = configurable.get("gemini_service")
    db: AsyncSession | None = configurable.get("db_session")

    if not gemini:
        logger.error("No gemini_service found in config['configurable']")
        raise RuntimeError("gemini_service dependency is required")

    if not db:
        logger.error("No db_session found in config['configurable']")
        raise RuntimeError("db_session dependency is required")

    analysis_prompt = f"""
    Analyze the following code for a student working on: {state["lesson_name"]}
    Objectives: {state["objectives"]}
    
    CODE:
    ```{state["language"]}
    {state["code_content"]}
    ```
    
    Identify 2-3 specific areas for improvement (Security, Performance, or Best Practices).
    For each, provide:
    1. The line number (if applicable)
    2. The category
    3. The observation (what's wrong)
    4. A Socratic question to help the student find the issue.
    
    Return ONLY JSON:
    {{
        "findings": [
            {{
                "line_number": 5,
                "category": "Security",
                "observation": "Hardcoded secret",
                "socratic_question": "What happens if this key is pushed to a public repo?"
            }}
        ]
    }}
    """

    try:
        response = await gemini.generate_content(
            prompt=analysis_prompt, response_mime_type="application/json"
        )
        data: AnalysisResponse = json.loads(response)  # pyright: ignore[reportAny]
        findings = data.get("findings", [])

        # Persist findings to DB
        review_id = state["review_id"]

        for f in findings:
            finding = CodeReviewFinding(
                review_id=review_id,
                line_number=f.get("line_number"),
                category=f.get("category", "General"),
                observation=f.get("observation", ""),
                socratic_question=f.get("socratic_question", ""),
            )
            db.add(finding)

        await db.commit()
        return {"findings": findings}
    except Exception as e:
        logger.error(f"Analysis node error: {e}")
        return {"findings": []}

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class CodeReviewerFinding(TypedDict):
    """Typed structure for a code review finding."""

    line_number: int | None
    category: str
    observation: str
    socratic_question: str


class CodeReviewerState(TypedDict):
    """LangGraph execution state for the Code Reviewer Agent."""

    messages: Annotated[list[BaseMessage], add_messages]
    lesson_id: str
    review_id: str
    code_content: str
    language: str

    # Enrichment fields
    lesson_name: str
    objectives: list[str]

    # Analysis fields
    findings: list[CodeReviewerFinding]
    guardrail_triggered: bool

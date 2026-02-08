from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """LangGraph execution state for the Teacher Agent."""

    messages: Annotated[list[BaseMessage], add_messages]
    lesson_id: str
    lesson_name: str
    lesson_context: str
    objectives: list[str]
    guardrail_triggered: bool
    suggested_docs: list[str]


class PartialTeacherState(TypedDict, total=False):
    """Partial state for Teacher nodes."""

    messages: list[BaseMessage]
    lesson_id: str
    lesson_name: str
    lesson_context: str
    objectives: list[str]
    guardrail_triggered: bool
    suggested_docs: list[str]

"""State definition for the Orchestrator agent."""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from sqlalchemy.ext.asyncio import AsyncSession


class OrchestratorState(TypedDict):
    """State for orchestrator's graph."""

    # Input
    messages: Annotated[list[BaseMessage], add_messages]  # Conversation history
    current_message: str  # Latest user message

    # Execution context
    db: AsyncSession
    thread_id: str

    # Command detection
    detected_command: str | None
    clean_message: str  # Message without command

    # Delegation
    selected_agent_id: str | None
    delegation_context: dict[str, str]  # Extra context for delegated agent

    # Response
    delegated_response: str | None
    final_response: str


class PartialOrchestratorState(TypedDict, total=False):
    """A partial state used for node returns."""

    messages: list[BaseMessage]
    current_message: str
    db: AsyncSession
    thread_id: str
    detected_command: str | None
    clean_message: str
    selected_agent_id: str | None
    delegation_context: dict[str, str]
    delegated_response: str | None
    final_response: str

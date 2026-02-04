"""Code Reviewer Agent - Provides Socratic feedback on code submissions."""

import logging
from collections.abc import AsyncIterator
from typing import Any, AsyncContextManager

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from agents.base import BaseAgent
from core.config import settings
from database.session import DBSessionManager
from services.gemini_service import GeminiService
from services.lesson_service import LessonContextService

from .nodes import (
    code_analysis_node,
    context_enrichment_node,
    guardrail_node,
    socratic_review_node,
)
from .state import CodeReviewerState

logger = logging.getLogger(__name__)


class CodeReviewerAgent(BaseAgent):
    """Agent that reviews code through Socratic questioning."""

    _checkpointer_cm: AsyncContextManager[AsyncSqliteSaver] | None = None
    _checkpointer: AsyncSqliteSaver | None = None
    _workflow: CompiledStateGraph[CodeReviewerState, Any, Any, Any] | None = None  # pyright: ignore[reportExplicitAny]

    def __init__(
        self,
        gemini_service: GeminiService,
        db_manager: DBSessionManager,
        lesson_service: LessonContextService,
        model_name: str = "gemini-2.0-flash",
    ) -> None:
        self.gemini_service: GeminiService = gemini_service
        self.db_manager: DBSessionManager = db_manager
        self.lesson_service: LessonContextService = lesson_service
        self.model_name: str = model_name

    def _create_builder(self) -> StateGraph[CodeReviewerState, Any, Any, Any]:  # pyright: ignore[reportExplicitAny]
        workflow = StateGraph(CodeReviewerState)

        _ = workflow.add_node("enrichment", context_enrichment_node)  # pyright: ignore[reportUnknownMemberType]
        _ = workflow.add_node("guardrail", guardrail_node)  # pyright: ignore[reportUnknownMemberType]
        _ = workflow.add_node("analysis", code_analysis_node)  # pyright: ignore[reportUnknownMemberType]
        _ = workflow.add_node("reviewer", socratic_review_node)  # pyright: ignore[reportUnknownMemberType]

        _ = workflow.set_entry_point("enrichment")

        _ = workflow.add_edge("enrichment", "guardrail")
        _ = workflow.add_edge("guardrail", "analysis")
        _ = workflow.add_edge("analysis", "reviewer")
        _ = workflow.add_edge("reviewer", END)

        return workflow

    @override
    async def initialize(self) -> None:
        if self._workflow is not None:
            return

        try:
            db_path = settings.BASE_DIR / "code_reviewer_checkpoints.db"
            self._checkpointer_cm = AsyncSqliteSaver.from_conn_string(str(db_path))
            self._checkpointer = await self._checkpointer_cm.__aenter__()

            builder = self._create_builder()
            self._workflow = builder.compile(checkpointer=self._checkpointer)  # pyright: ignore[reportUnknownMemberType]
            logger.info("Code Reviewer agent initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Code Reviewer agent: {e}")
            raise

    @override
    async def chat(self, thread_id: str, message: str, db: AsyncSession) -> str:
        # For code review, we usually expect code_content and language to be passed
        # via the state or a specific starting message.
        # This generic chat method will treat the message as a prompt.
        raise NotImplementedError("Use specific review submission for this agent.")

    @override
    def chat_stream(self, thread_id: str, message: str, db: AsyncSession) -> AsyncIterator[str]:
        # Implementation similar to TeacherAgent if needed
        raise NotImplementedError("Use specific review submission for this agent.")

    async def review(
        self, review_id: str, lesson_id: str, code: str, language: str, db: AsyncSession
    ) -> AsyncIterator[str]:
        """Specific method for code review streaming."""
        state: CodeReviewerState = {
            "messages": [HumanMessage(content=f"Please review my {language} code.")],
            "lesson_id": lesson_id,
            "review_id": review_id,
            "code_content": code,
            "language": language,
            "lesson_name": "",
            "objectives": [],
            "findings": [],
            "guardrail_triggered": False,
        }

        config: RunnableConfig = {
            "configurable": {
                "thread_id": review_id,
                "gemini_service": self.gemini_service,
                "lesson_service": self.lesson_service,
                "db_session": db,
                "model_name": self.model_name,
            }
        }

        if self._workflow is None:
            raise RuntimeError("Agent not initialized")

        has_streamed = False
        # In LangGraph v2, we stream events
        async for event in self._workflow.astream_events(state, config=config, version="v2"):
            if event["event"] == "on_custom_event" and event["name"] == "review_token":
                data = event.get("data", {})
                if data:
                    token = data.get("token")
                    if token and isinstance(token, str):
                        has_streamed = True
                        yield str(token)

            # Fallback for static messages (e.g. guardrails or errors)
            # Filter specifically for the 'reviewer' node
            # to avoid duplicate yields from graph root events
            elif (
                event["event"] == "on_chain_end"
                and event.get("name") == "reviewer"
                and not has_streamed
            ):
                # The final output is in event["data"]["output"]
                output = event.get("data", {}).get("output", {})
                if isinstance(output, dict) and "messages" in output:
                    messages = output["messages"]  # pyright: ignore[reportUnknownVariableType]
                    if messages:
                        last_msg = messages[-1]  # pyright: ignore[reportUnknownVariableType]
                        content = getattr(last_msg, "content", "")  # pyright: ignore[reportUnknownArgumentType]
                        if content:
                            yield str(content)

    @override
    async def close(self) -> None:
        if self._checkpointer_cm is not None:
            _ = await self._checkpointer_cm.__aexit__(None, None, None)
            self._checkpointer = None
            self._workflow = None

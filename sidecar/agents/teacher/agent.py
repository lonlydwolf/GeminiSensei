"""Teacher Agent - Enforces learning through Socratic method."""

import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, AsyncContextManager, cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings

from .nodes import context_enrichment_node, guardrail_node, socratic_node
from .state import AgentState

if TYPE_CHECKING:
    from database.session import DBSessionManager
    from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class TeacherAgent:
    """Agent that teaches through Socratic questioning."""

    _checkpointer_cm: AsyncContextManager[AsyncSqliteSaver] | None = None
    _checkpointer: AsyncSqliteSaver | None = None
    _workflow: CompiledStateGraph[AgentState, Any, Any, Any] | None = None  # pyright: ignore[reportExplicitAny]

    def __init__(
        self,
        gemini_service: "GeminiService",
        db_manager: "DBSessionManager",
        model_name: str = "gemini-2.0-flash",
    ) -> None:
        """Initialize teacher agent.

        Args:
            gemini_service: Injected Gemini service.
            db_manager: Injected database session manager.
            model_name: Model name to use.
        """
        self.gemini_service: GeminiService = gemini_service
        self.db_manager: DBSessionManager = db_manager
        self.model_name: str = model_name

    def _create_builder(self) -> StateGraph[AgentState, Any, Any, Any]:  # pyright: ignore[reportExplicitAny]
        """Create LangGraph builder for teaching.

        Returns:
            StateGraph builder
        """
        workflow = StateGraph(AgentState)

        # Add nodes
        _ = workflow.add_node("enrichment", context_enrichment_node)  # pyright: ignore[reportUnknownMemberType]
        _ = workflow.add_node("guardrail", guardrail_node)  # pyright: ignore[reportUnknownMemberType]
        _ = workflow.add_node("socratic", socratic_node)  # pyright: ignore[reportUnknownMemberType]

        # Set entry point
        _ = workflow.set_entry_point("enrichment")

        # Add edges
        _ = workflow.add_edge("enrichment", "guardrail")
        _ = workflow.add_edge("guardrail", "socratic")
        _ = workflow.add_edge("socratic", END)

        return workflow

    async def initialize(self) -> None:
        """Initialize checkpointer and compile workflow."""
        if self._workflow is not None:
            return

        try:
            db_path = settings.BASE_DIR / settings.CHECKPOINT_DB_PATH
            self._checkpointer_cm = AsyncSqliteSaver.from_conn_string(str(db_path))
            # Enter context manager
            self._checkpointer = await self._checkpointer_cm.__aenter__()

            # Compile workflow with the checkpointer
            builder = self._create_builder()
            self._workflow = builder.compile(checkpointer=self._checkpointer)  # pyright: ignore[reportUnknownMemberType]
            logger.info("Teacher agent initialized with checkpointer.")
        except Exception as e:
            logger.error(f"Failed to initialize teacher agent: {e}")
            raise

    @property
    def workflow(self) -> CompiledStateGraph[AgentState, Any, Any, Any]:  # pyright: ignore[reportExplicitAny]
        """Get the compiled workflow.

        Raises:
            RuntimeError: If the agent has not been initialized.
        """
        if self._workflow is None:
            raise RuntimeError(
                "TeacherAgent must be initialized before use. Call await initialize()."
            )
        return self._workflow

    async def chat(self, lesson_id: str, message: str, _db: AsyncSession) -> str:
        """Chat with teacher agent.

        Args:
            lesson_id: Current lesson ID (also thread_id for memory)
            message: User's message
            _db: Database session

        Returns:
            Teacher's response
        """
        try:
            # Prepare initial state with lesson_id
            state: AgentState = {
                "messages": [HumanMessage(content=message)],
                "lesson_id": lesson_id,
                # Initialize other fields with safe defaults
                "lesson_name": "",
                "lesson_context": "",
                "objectives": [],
                "guardrail_triggered": False,
                "suggested_docs": [],
            }

            # Run workflow with checkpointing and dependency injection
            config = cast(
                RunnableConfig,
                cast(
                    object,
                    {
                        "configurable": {
                            "thread_id": lesson_id,
                            "gemini_service": self.gemini_service,
                            "db_session": _db,
                            "model_name": self.model_name,
                        }
                    },
                ),
            )

            result = await self.workflow.ainvoke(state, config=config)  # pyright: ignore[reportUnknownMemberType]

            # Extract response
            messages = result.get("messages", [])  # pyright: ignore[reportAny]
            if messages:
                last_msg = messages[-1]  # pyright: ignore[reportAny]
                return str(last_msg.content)  # pyright: ignore[reportAny]

            return "I'm here to help you learn. What would you like to work on?"

        except Exception as e:
            logger.error(f"Teacher agent error: {e}")
            raise

    async def chat_stream(
        self, lesson_id: str, message: str, _db: AsyncSession
    ) -> AsyncIterator[str]:
        """Chat with teacher agent (streaming).

        Args:
            lesson_id: Current Lesson ID
            message: User's message
            _db: Database session

        Yields:
            Response chunks
        """

        try:
            # Prepare initial state
            state: AgentState = {
                "messages": [HumanMessage(content=message)],
                "lesson_id": lesson_id,
                "lesson_name": "",
                "lesson_context": "",
                "objectives": [],
                "guardrail_triggered": False,
                "suggested_docs": [],
            }

            # Run workflow with checkpointing and dependency injection
            config = cast(
                RunnableConfig,
                cast(
                    object,
                    {
                        "configurable": {
                            "thread_id": lesson_id,
                            "gemini_service": self.gemini_service,
                            "db_session": _db,
                            "model_name": self.model_name,
                        }
                    },
                ),
            )

            # Use astream to stream events from the graph
            async for event in self.workflow.astream_events(state, config=config, version="v2"):
                kind = event.get("event")

                # Intercept custom token events from the socratic node
                if kind == "on_custom_event" and event.get("name") == "socratic_token":
                    data = event.get("data", {})
                    if data:
                        token = data.get("token")
                        if token:
                            yield str(token)  # pyright: ignore[reportAny]

        except Exception as e:
            logger.error(f"Teacher agent streaming error: {e}")
            raise

    async def close(self) -> None:
        """Cleanup checkpointer connection."""
        if self._checkpointer_cm is not None:
            try:
                _ = await self._checkpointer_cm.__aexit__(None, None, None)
                self._checkpointer = None
                self._checkpointer_cm = None
                self._workflow = None
                logger.info("Teacher agent checkpointer closed.")
            except Exception as e:
                logger.error(f"Error closing teacher agent checkpointer: {e}")

"""Orchestrator agent that delegates to specialized agents."""

import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, cast

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from agents.agent_registry import agent_registry
from agents.base import BaseAgent
from agents.manager import agent_manager
from agents.orchestrator.nodes.command_parser import parse_command_node
from agents.orchestrator.nodes.delegation_executor import delegate_to_agent_node
from agents.orchestrator.nodes.delegation_router import route_to_agent_node
from agents.orchestrator.state import OrchestratorState
from agents.prompt_templates import PromptTemplates
from core.types import AgentConfig

if TYPE_CHECKING:
    from database.session import DBSessionManager
    from services.gemini_service import GeminiService
    from services.lesson_service import LessonContextService


logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Main agent that orchestrates delegation to specialized agents.

    Architecture:
    - User messages enter through chat() method
    - State is created with message + db + thread_id
    - Graph routes through: parse_command -> route_agent -> delegate
    - All context flows through OrchestratorState (no instance vars)
    - Pure functional nodes make testing and debugging easier
    """

    graph: CompiledStateGraph[OrchestratorState, Any, OrchestratorState, OrchestratorState]  # pyright: ignore[reportExplicitAny]
    streaming_graph: CompiledStateGraph[
        OrchestratorState, Any, OrchestratorState, OrchestratorState  # pyright: ignore[reportExplicitAny]
    ]

    def __init__(
        self,
        gemini_service: "GeminiService",
        db_manager: "DBSessionManager",
        lesson_service: "LessonContextService",
    ) -> None:
        super().__init__(gemini_service, db_manager, lesson_service)
        # Note: graph is not initialized here - it's set in initialize()
        # Type checker knows it will be set before use

    @classmethod
    @override
    def get_config(cls) -> AgentConfig:
        """Return configuration for the orchestrator agent.

        The orchestrator has no command because it's the default entry point.
        Users don't explicitly invoke it - it's always the first agent contacted.
        """
        return AgentConfig(
            agent_id="orchestrator",
            name="Orchestrator",
            description="Main coordinator that routes requests to specialized agents",
            command=None,  # No command - this is the default entry point
            capabilities=["routing", "delegation", "coordination"],
            icon="Network",
        )

    @override
    async def initialize(self) -> None:
        """Build the orchestrator's state graph.

        Graph flow:
        1. parse_command: Detects /commands and extracts command name
        2. route_agent: Determines which agent should handle the request
        3. delegate: Calls the selected agent and returns response

        All nodes are pure functions that take OrchestratorState and return dict.
        """

        # Build the shared workflow definition
        workflow = self._build_workflow()

        # Compile the standard graph for full execution
        self.graph = workflow.compile()  # pyright: ignore[reportUnknownMemberType]

        # Compile a specialized graph for streaming that interrupts before delegation
        self.streaming_graph = workflow.compile(interrupt_before=["delegate"])  # pyright: ignore[reportUnknownMemberType]

        logger.info("OrchestratorAgent initialized with dual-graph architecture")

    def _build_workflow(self) -> StateGraph[OrchestratorState, Any, Any, Any]:  # pyright: ignore[reportExplicitAny]
        """Create the shared LangGraph workflow definition."""
        workflow = StateGraph(OrchestratorState)

        _ = workflow.add_node("parse_command", parse_command_node)  # pyright: ignore[reportUnknownMemberType]
        _ = workflow.add_node("route_agent", route_to_agent_node)  # pyright: ignore[reportUnknownMemberType]
        _ = workflow.add_node("delegate", delegate_to_agent_node)  # pyright: ignore[reportUnknownMemberType]

        # Define edges
        _ = workflow.set_entry_point("parse_command")
        _ = workflow.add_edge("parse_command", "route_agent")
        _ = workflow.add_edge("route_agent", "delegate")
        _ = workflow.add_edge("delegate", END)

        return workflow

    @override
    async def chat(self, thread_id: str, message: str, db: AsyncSession) -> str:
        """Process a message through the orchestrator.

        Flow:
        1. Create initial state with message, db, thread_id
        2. Run the state graph (parse -> route -> delegate)
        3. Extract and return final response

        Args:
            thread_id: Conversation thread identifier
            message: User's message (may contain /command)
            db: Database session for delegated agents

        Returns:
            Response from the delegated agent
        """

        # Create initial state with all context
        initial_state: OrchestratorState = {
            # User input
            "messages": [],  # TODO: Load conversation history in Phase 5
            "current_message": message,
            # Execution context
            "db": db,
            "thread_id": thread_id,
            # Processing state (will be filled by nodes)
            "detected_command": None,
            "clean_message": message,
            "selected_agent_id": None,
            "delegation_context": {},
            "delegated_response": None,
            "final_response": "",
        }

        # Run the graph
        result = await self.graph.ainvoke(initial_state)  # pyright: ignore[reportUnknownMemberType]

        # Extract the final response from state
        return result.get("final_response", "No response generated")  # pyright: ignore[reportAny]

    @override
    async def chat_stream(
        self, thread_id: str, message: str, db: AsyncSession
    ) -> AsyncIterator[str]:
        """Process a message and stream response through the delegated agent.

        This implementation:
        1. Runs the specialized streaming graph which interrupts before delegation.
        2. Extract the routing result from the interrupted state.
        3. Calls the delegated agent's chat_stream method manually.
        """
        # Create initial state
        initial_state: OrchestratorState = {
            "messages": [],
            "current_message": message,
            "db": db,
            "thread_id": thread_id,
            "detected_command": None,
            "clean_message": message,
            "selected_agent_id": None,
            "delegation_context": {},
            "delegated_response": None,
            "final_response": "",
        }

        try:
            # Run the graph until the 'delegate' node
            result = await self.streaming_graph.ainvoke(initial_state)  # pyright: ignore[reportUnknownMemberType]
            # cast to OrchestratorState as ainvoke returns Any
            result_state = cast(OrchestratorState, result)

            agent_id = result_state.get("selected_agent_id")
            clean_message = result_state.get("clean_message", message)

            if not agent_id:
                yield "No agent selected. Please try again."
                return

            # Get the agent instance
            agent = agent_manager.get_agent(agent_id)

            # Get agent configuration for prompt generation
            agent_class = agent_registry.get_agent_class(agent_id)
            config = agent_class.get_config()

            # Format conversation history
            messages = result_state.get("messages", [])
            conversation_history = PromptTemplates.format_conversation_history(messages)

            # Generate system prompt
            system_prompt = PromptTemplates.generate_delegation_prompt(
                agent_config=config,
                user_message=clean_message,
                conversation_context=conversation_history,
            )

            # Stream from the delegated agent
            enhanced_message = f"{system_prompt}\n\nUser request: {clean_message}"
            async for token in agent.chat_stream(
                thread_id=thread_id, message=enhanced_message, db=db
            ):
                yield token

        except Exception as e:
            logger.error(f"Error in orchestrator streaming: {e}")
            yield f"Error processing your request: {str(e)}"

    @override
    async def close(self) -> None:
        """Cleanup resources.

        The graph itself doesn't need cleanup, but this follows
        the BaseAgent interface for consistency.
        """
        logger.info("OrchestratorAgent closed")

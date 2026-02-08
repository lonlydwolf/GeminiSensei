"""Node for parsing commands from user messages."""

import logging

from agents.command_detector import CommandDetector
from agents.orchestrator.state import OrchestratorState, PartialOrchestratorState
from core.types import ParsedCommand

logger = logging.getLogger(__name__)


async def parse_command_node(state: OrchestratorState) -> PartialOrchestratorState:
    """Parse the user message for /commands.

    Updates state with:
        - detected_command: The command name if found
        - clean_message: Message with command removed
    """
    message = state["current_message"]

    parsed: ParsedCommand = CommandDetector.parse(message)

    if parsed.has_command:
        logger.info(f"Detected command: /{parsed.command}")
        return {
            "detected_command": parsed.command,
            "clean_message": parsed.remaining_message or message,
        }
    else:
        return {"detected_command": None, "clean_message": message}

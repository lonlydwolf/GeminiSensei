"""Utility for detecting and parsing /commands in user messages."""

import re

from core.types import ParsedCommand


class CommandDetector:
    """Detects /command patterns in user messages."""

    COMMAND_PATTERN: re.Pattern[str] = re.compile(r"^/([a-z]+)\s*(.*)$", re.IGNORECASE)

    @classmethod
    def parse(cls, message: str) -> ParsedCommand:
        """Parse a message for commands.

        Examples:
            "/review my code" -> ParsedCommand(True, "review", "my code")
            "hello" -> ParsedCommand(False, None, "hello")
        """
        stripped_message = message.strip()
        match = cls.COMMAND_PATTERN.match(stripped_message)

        if match:
            command = match.group(1).lower()
            remaining = match.group(2).strip()
            return ParsedCommand(has_command=True, command=command, remaining_message=remaining)

        return ParsedCommand(has_command=False, command=None, remaining_message=stripped_message)

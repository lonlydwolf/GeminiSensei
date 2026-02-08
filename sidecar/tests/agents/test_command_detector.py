from agents.command_detector import CommandDetector


def test_parse_command_review():
    result = CommandDetector.parse("/review print('hello')")
    assert result.has_command is True
    assert result.command == "review"
    assert result.remaining_message == "print('hello')"


def test_parse_command_teach():
    result = CommandDetector.parse("/teach how do I use loops?")
    assert result.has_command is True
    assert result.command == "teach"
    assert result.remaining_message == "how do I use loops?"


def test_parse_no_command():
    result = CommandDetector.parse("hello world")
    assert result.has_command is False
    assert result.command is None
    assert result.remaining_message == "hello world"


def test_parse_empty():
    result = CommandDetector.parse("")
    assert result.has_command is False
    assert result.command is None
    assert result.remaining_message == ""


def test_parse_whitespace():
    result = CommandDetector.parse("   ")
    assert result.has_command is False
    assert result.command is None
    assert result.remaining_message == ""


def test_parse_command_case_insensitive():
    result = CommandDetector.parse("/REVIEW code")
    assert result.has_command is True
    assert result.command == "review"
    assert result.remaining_message == "code"


def test_parse_command_no_args():
    result = CommandDetector.parse("/review")
    assert result.has_command is True
    assert result.command == "review"
    assert result.remaining_message == ""

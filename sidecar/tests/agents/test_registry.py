from unittest.mock import MagicMock, patch

import pytest

from agents.agent_registry import AgentRegistry
from agents.code_reviewer.agent import CodeReviewerAgent
from agents.teacher.agent import TeacherAgent


def test_registry_registration():
    registry = AgentRegistry()
    registry._register_agent(TeacherAgent)  # pyright: ignore[reportPrivateUsage]
    registry._register_agent(CodeReviewerAgent)  # pyright: ignore[reportPrivateUsage]

    agent_ids = registry.get_all_agent_ids()
    assert "teacher" in agent_ids
    assert "reviewer" in agent_ids

    assert registry.get_agent_class("teacher") == TeacherAgent
    assert registry.get_agent_class("reviewer") == CodeReviewerAgent

    assert registry.get_agent_by_command("teach") == TeacherAgent
    assert registry.get_agent_by_command("review") == CodeReviewerAgent


def test_registry_get_all_configs():
    registry = AgentRegistry()
    registry._register_agent(TeacherAgent)  # pyright: ignore[reportPrivateUsage]
    configs = registry.get_all_configs()
    assert len(configs) == 1
    assert configs[0]["agent_id"] == "teacher"


def test_registry_unknown_agent():
    registry = AgentRegistry()
    with pytest.raises(KeyError):
        _ = registry.get_agent_class("unknown")


def test_registry_unknown_command():
    registry = AgentRegistry()
    assert registry.get_agent_by_command("unknown") is None


def test_discover_agents_partial_failure():
    registry = AgentRegistry()

    # We patch import_module to fail for one specific agent
    with patch("importlib.import_module") as mock_import:

        def side_effect(name: str):
            if "teacher" in name:
                raise ImportError("Failed to load teacher")
            # For other agents, we can return a mock module or let it fail
            # but we want to see if the loop continues.
            # To be more realistic, we could mock the directory structure
            return MagicMock()

        mock_import.side_effect = side_effect

        # We also need to mock Path.iterdir to return some folders
        with patch("pathlib.Path.iterdir") as mock_iter:
            mock_teacher_dir = MagicMock()
            mock_teacher_dir.is_dir.return_value = True
            mock_teacher_dir.name = "teacher"
            mock_teacher_dir.__truediv__.return_value.exists.return_value = True

            mock_reviewer_dir = MagicMock()
            mock_reviewer_dir.is_dir.return_value = True
            mock_reviewer_dir.name = "reviewer"
            mock_reviewer_dir.__truediv__.return_value.exists.return_value = True

            mock_iter.return_value = [mock_teacher_dir, mock_reviewer_dir]

            # This should not raise an exception
            registry.discover_agents()

            # Teacher should NOT be registered, but discovery should have finished
            assert "teacher" not in registry.get_all_agent_ids()


import pytest

from agents.code_reviewer.agent import CodeReviewerAgent
from agents.manager import agent_manager
from agents.teacher.agent import TeacherAgent
from core.types import AgentID


@pytest.mark.asyncio
async def test_agent_manager_initialization():
    # Reset manager for test
    agent_manager._agent_instances = {}  # pyright: ignore[reportPrivateUsage]
    agent_manager._is_initialized = False  # pyright: ignore[reportPrivateUsage]

    await agent_manager.initialize_all()

    assert AgentID.TEACHER.value in agent_manager._agent_instances  # pyright: ignore[reportPrivateUsage]
    assert AgentID.REVIEWER.value in agent_manager._agent_instances  # pyright: ignore[reportPrivateUsage]
    assert isinstance(agent_manager.get_agent(AgentID.TEACHER.value), TeacherAgent)
    assert isinstance(agent_manager.get_agent(AgentID.REVIEWER.value), CodeReviewerAgent)


@pytest.mark.asyncio
async def test_agent_manager_generic_retrieval():
    await agent_manager.initialize_all()
    teacher = agent_manager.get_agent(AgentID.TEACHER.value)
    assert teacher is not None

    with pytest.raises(RuntimeError):
        _ = agent_manager.get_agent("non_existent")

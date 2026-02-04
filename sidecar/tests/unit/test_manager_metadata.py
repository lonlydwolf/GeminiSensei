import pytest

from agents.manager import AgentManager
from core.types import AgentID, AgentMetadata


@pytest.mark.asyncio
async def test_get_agents_metadata():
    manager = AgentManager()
    
    # Before initialization, it might be empty or we might want it to return defaults
    # But based on initialize_all, it populates _agents.
    
    await manager.initialize_all()
    metadata: list[AgentMetadata] = manager.get_agents_metadata()
    
    assert isinstance(metadata, list)
    assert len(metadata) >= 2
    
    ids = [m["id"] for m in metadata]
    assert AgentID.TEACHER.value in ids
    assert AgentID.REVIEWER.value in ids
    
    for item in metadata:
        assert all(key in item for key in ["id", "name", "description", "icon"])
        assert isinstance(item["id"], str)
        assert isinstance(item["name"], str)
        assert isinstance(item["description"], str)
        assert isinstance(item["icon"], str)

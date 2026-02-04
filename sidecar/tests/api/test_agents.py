import pytest
from fastapi.testclient import TestClient

from core.types import AgentMetadata
from main import app


@pytest.fixture
def client():
    # Force initialize agents for testing the metadata
    import anyio

    from agents.manager import agent_manager

    anyio.run(agent_manager.initialize_all)
    return TestClient(app)


def test_get_agents_endpoint(client: TestClient):
    response = client.get("/api/agents")
    assert response.status_code == 200

    data: list[AgentMetadata] = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # Verify structure of first element
    agent: AgentMetadata = data[0]
    assert "id" in agent
    assert "name" in agent
    assert "description" in agent
    assert "icon" in agent

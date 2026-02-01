from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from core.types import RoadmapCreateResult, RoadmapStructure


@pytest.mark.asyncio
async def test_create_roadmap_api(client: AsyncClient):
    # Mock result from the roadmap creator agent
    mock_result = RoadmapCreateResult(
        roadmap_id="test-uuid", roadmap=RoadmapStructure(name="Test", description="...", phases=[])
    )

    with patch(
        "agents.roadmap_creator.roadmap_creator.create_roadmap", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = mock_result

        payload = {
            "goal": "Learn Python Testing in 2026",
            "background": "Beginner",
            "preferences": "Hands-on",
        }
        response = await client.post("/api/roadmap/create", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["roadmap_id"] == "test-uuid"
        assert data["message"] == "Roadmap created successfully"


@pytest.mark.asyncio
async def test_get_roadmap_not_found(client: AsyncClient):
    response = await client.get("/api/roadmap/non-existent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Roadmap not found"

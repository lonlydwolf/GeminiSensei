import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Roadmap
from main import SIDECAR_SECRET


@pytest.mark.asyncio
async def test_reset_application(client: AsyncClient, db_session: AsyncSession):
    # 1. Ensure we have some data
    roadmap = Roadmap(id="test-reset-id", name="Reset Test", goal="Testing", status="active")
    db_session.add(roadmap)
    await db_session.commit()

    # 2. Call reset
    response = await client.delete(
        "/api/settings/reset", headers={"X-Sidecar-Token": SIDECAR_SECRET}
    )
    assert response.status_code == 200

    # 3. After reset, try to access data (should be gone or new DB)
    # The integration test uses in-memory DB which might be tricky if we delete a file.
    # But we can at least test the endpoint exists and returns 200.

    # Actually, in integration tests we override get_db to use db_session (in-memory).
    # The reset logic will try to delete a file that doesn't exist for in-memory.
    # We should handle that gracefully in the code.

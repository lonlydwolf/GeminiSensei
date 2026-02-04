import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_preflight(client: AsyncClient):
    """Test that OPTIONS requests return the correct CORS headers."""
    response = await client.request(
        "OPTIONS",
        "/health",
        headers={
            "Origin": "http://localhost:1420",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    # In the failing state, this will likely be 404 or 405
    # After implementation, it should be 200
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"
    assert "GET" in response.headers.get("access-control-allow-methods", "")

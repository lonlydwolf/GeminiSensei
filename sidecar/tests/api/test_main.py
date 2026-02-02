
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.config import settings
from main import lifespan


@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Gemini Sensei Sidecar!"}


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_lifespan_missing_api_key():
    # Store original key
    original_key = settings.GEMINI_API_KEY
    settings.GEMINI_API_KEY = ""
    
    try:
        # Mock app
        app = FastAPI()
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="GEMINI_API_KEY is missing"):
            async with lifespan(app):
                pass
    finally:
        # Restore key
        settings.GEMINI_API_KEY = original_key

from pathlib import Path

from dotenv import set_key
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


class ApiKeyRequest(BaseModel):
    api_key: str


@router.post("/api-key")
async def update_api_key(request: ApiKeyRequest):
    """Updates the Gemini API key in .env and in-memory settings."""
    if not request.api_key.strip():
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    try:
        # Determine .env path
        # Assuming it should be in the same directory as main.py for now
        # or in the current working directory.
        env_path = Path(".env")

        # Ensure file exists
        if not env_path.exists():
            env_path.touch()

        # Update .env
        _ = set_key(str(env_path), "GEMINI_API_KEY", request.api_key)

        # Update in-memory settings
        settings.GEMINI_API_KEY = request.api_key

        return {"success": True, "message": "API key updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update API key: {str(e)}")

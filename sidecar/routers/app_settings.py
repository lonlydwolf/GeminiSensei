import asyncio
import shutil
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from core.config import settings
from core.exceptions import QuotaExceededError
from database.migrations import run_migrations
from database.session import dbsessionmanager
from services.key_manager import key_manager

router = APIRouter(prefix="/api/settings", tags=["settings"])


class ApiKeyRequest(BaseModel):
    api_key: str


@router.post("/api-key")
async def update_api_key(request: ApiKeyRequest):
    """Updates the Gemini API key in .env and in-memory settings."""
    print(f"DEBUG: Received API Key update request. Key length: {len(request.api_key)}")
    if not request.api_key.strip():
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    if not key_manager.validate_format(request.api_key):
        raise HTTPException(
            status_code=400,
            detail="Invalid API key format. Expected 'AIza...' and 39 chars.",
        )

    try:
        # Test the API key before saving
        await key_manager.verify_key(request.api_key)
        print("DEBUG: API key validation successful")

        # Save key
        env_path = key_manager.save_key(request.api_key)

        print("DEBUG: API Key update successful")
        return {
            "success": True,
            "message": "API key updated and validated successfully",
            "details": {
                "env_file": str(env_path) if settings.DEBUG else env_path.name,
                "key_length": len(request.api_key),
                "validated": True,
            },
        }
    except QuotaExceededError:
        # Let the global exception handler handle 429
        raise
    except ValueError as e:
        print(f"DEBUG: API key validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: API Key update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update API key: {str(e)}")


@router.get("/status")
async def get_settings_status():
    """Checks the status of required settings."""
    has_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())

    # Test if the key actually works (light check)
    key_valid = False
    if has_key:
        # We assume if it's set and starts with AIza, it's likely valid from previous validation.
        # But we can do a quick regex check or length check here to be fast.
        if settings.GEMINI_API_KEY.startswith("AIza") and len(settings.GEMINI_API_KEY) == 39:
            key_valid = True

    return {
        "gemini_api_key_set": has_key,
        "gemini_api_key_valid": key_valid,
        "env_file_path": str(settings.ENV_FILE_PATH)
        if settings.DEBUG
        else settings.ENV_FILE_PATH.name,
        "env_file_exists": settings.ENV_FILE_PATH.exists(),
    }

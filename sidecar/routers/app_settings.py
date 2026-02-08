import google.genai as genai
from dotenv import set_key
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import settings
from services.gemini_service import gemini_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


class ApiKeyRequest(BaseModel):
    api_key: str


@router.post("/api-key")
async def update_api_key(request: ApiKeyRequest):
    """Updates the Gemini API key in .env and in-memory settings."""
    print(f"DEBUG: Received API Key update request. Key length: {len(request.api_key)}")
    if not request.api_key.strip():
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    # NEW: Validate API key format
    if not request.api_key.startswith("AIza"):
        raise HTTPException(
            status_code=400,
            detail="Invalid API key format. Gemini API keys should start with 'AIza'",
        )

    if len(request.api_key) != 39:
        raise HTTPException(
            status_code=400, detail="Invalid API key length. Expected 39 characters"
        )

    try:
        # NEW: Test the API key before saving
        test_client = genai.Client(api_key=request.api_key)
        try:
            # Make a minimal API call to verify the key works
            _ = await test_client.aio.models.generate_content(  # pyright: ignore[reportUnknownMemberType]
                model="gemini-2.0-flash", contents="test", config={"max_output_tokens": 1}
            )
            print("DEBUG: API key validation successful")
        except Exception as e:
            print(f"DEBUG: API key validation failed: {e}")
            raise HTTPException(
                status_code=400, detail=f"API key is invalid or not authorized: {str(e)}"
            )

        # Determine .env path from centralized settings
        env_path = settings.ENV_FILE_PATH

        # Ensure directory exists
        env_path.parent.mkdir(parents=True, exist_ok=True)
        if not env_path.exists():
            env_path.touch()

        # Update .env
        print(f"DEBUG: Updating .env at {env_path}")
        _ = set_key(str(env_path), "GEMINI_API_KEY", request.api_key)

        # Update in-memory settings
        settings.GEMINI_API_KEY = request.api_key

        # Update running service
        print("DEBUG: Updating Gemini Service instance")
        gemini_service.update_api_key(request.api_key)

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

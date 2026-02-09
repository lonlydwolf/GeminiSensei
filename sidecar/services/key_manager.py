import logging
from pathlib import Path

import google.genai as genai
from dotenv import set_key
from google.genai import types
from google.genai.errors import ClientError

from core.config import settings
from core.exceptions import QuotaExceededError
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class KeyManager:
    """Manages API key validation and persistence."""

    def validate_format(self, api_key: str) -> bool:
        """Checks if the API key has the correct format."""
        if not api_key:
            return False
        if not api_key.startswith("AIza"):
            return False
        if len(api_key) != 39:
            return False
        return True

    async def verify_key(self, api_key: str) -> None:
        """Verifies the API key by making a dry run request to Gemini.

        Raises:
            QuotaExceededError: If the API key has exceeded its quota (429).
            ValueError: If the API key is invalid or other client error occurs.
        """
        try:
            # Create a temporary client with the new key
            test_client = genai.Client(api_key=api_key)

            # Make a minimal API call to verify the key works
            config = types.GenerateContentConfig(max_output_tokens=1)
            _ = await test_client.aio.models.generate_content(  # pyright: ignore[reportUnknownMemberType]
                model="gemini-2.0-flash-lite", contents="test", config=config
            )
        except ClientError as e:
            logger.error(f"API Key verification failed (ClientError): {e}")
            if e.code == 429:
                raise QuotaExceededError(
                    "API Quota Exceeded. Please check your billing details or try a different key."
                )
            # Use specific message from the API error
            raise ValueError(f"Verification failed: {e.message}")
        except Exception as e:
            logger.error(f"API Key verification failed (Unexpected): {e}")
            raise ValueError(f"Verification failed: {str(e)}")

    def save_key(self, api_key: str) -> Path:
        """Saves the API key to the .env file and updates the running service."""
        env_path = settings.ENV_FILE_PATH

        # Ensure directory exists
        env_path.parent.mkdir(parents=True, exist_ok=True)
        if not env_path.exists():
            env_path.touch()

        # Update .env
        _ = set_key(str(env_path), "GEMINI_API_KEY", api_key)

        # Update in-memory settings
        settings.GEMINI_API_KEY = api_key

        # Update running service
        gemini_service.update_api_key(api_key)

        return env_path


key_manager = KeyManager()

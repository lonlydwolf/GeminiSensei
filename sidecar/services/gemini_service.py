"""Gemini API service for all interactions."""

import logging
from collections.abc import AsyncIterator

import google.genai as genai
from google.genai import errors, types

from core.config import settings
from core.exceptions import ExternalAPIError, QuotaExceededError

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Gemini API using the google-genai SDK."""

    def __init__(self, model_name: str = settings.GEMINI_MODEL) -> None:
        """Initialize Gemini service.

        Args:
            model_name: Gemini model to use.
        """
        self.model_name: str = model_name
        self._client: genai.Client | None = None
        # Don't initialize client here if API key is missing to avoid crash at import time
        if settings.GEMINI_API_KEY:
            try:
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

    @property
    def client(self) -> genai.Client:
        """Get the Gemini client, initializing it if necessary."""
        if self._client is None:
            if settings.GEMINI_API_KEY:
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            else:
                raise ExternalAPIError(
                    message="Gemini API key is not configured. Please set it in Settings."
                )
        return self._client

    def update_api_key(self, api_key: str) -> None:
        """Update the API key and re-initialize the Gemini client.

        Args:
            api_key: New Gemini API key.
        """
        logger.info("Updating Gemini API key and re-initializing client")
        try:
            self._client = genai.Client(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client with new key: {e}")
            raise ExternalAPIError(message=f"Invalid API key: {str(e)}")

    async def generate_content(
        self,
        prompt: str | list[str],
        system_instruction: str | None = None,
        search: bool = False,
        response_mime_type: str | None = None,
    ) -> str:
        """Generate content using Gemini API.

        Args:
            prompt: User prompt (string or list of strings)
            system_instruction: System instruction for the model
            search: Whether to use Google Search
            response_mime_type: MIME type for the response (e.g. "application/json")

        Returns:
            Generated text response
        """
        try:
            # Create config for this specific request to include system_instruction
            tools: types.ToolListUnion = [types.Tool(google_search=types.GoogleSearch())]
            config = types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                system_instruction=system_instruction,
                tools=tools if search else None,
                response_mime_type=response_mime_type,
                safety_settings=settings.SAFETY_SETTINGS,
            )

            response = await self.client.aio.models.generate_content(  # pyright: ignore[reportUnknownMemberType]
                model=self.model_name, contents=prompt, config=config
            )

            text = response.text
            if text is None:
                return ""
            return text
        except errors.ClientError as e:
            logger.error(f"Gemini API Client Error: {e}")
            if e.code == 429:
                raise QuotaExceededError(
                    message="Gemini API Quota Exceeded", details={"original_error": str(e)}
                )
            raise ExternalAPIError(
                message=f"Gemini API Error: {e.message}", details={"original_error": str(e)}
            )
        except errors.ServerError as e:
            logger.error(f"Gemini API Server Error: {e}")
            raise ExternalAPIError(
                message="Gemini API Server Error. Please try again later.",
                details={"original_error": str(e)},
            )
        except Exception as e:
            logger.error(f"Gemini API unexpected error: {e}")
            raise ExternalAPIError(
                message="An unexpected error occurred while contacting Gemini",
                details={"original_error": str(e)},
            )

    async def generate_content_stream(
        self,
        prompt: str | list[str],
        system_instruction: str | None = None,
        search: bool = False,
    ) -> AsyncIterator[str]:
        """Generate streaming content using Gemini API.

        Args:
            prompt: User prompt (string or list of strings)
            system_instruction: System instruction for the model

        Yields:
            Text chunks as they're generated
        """
        try:
            tools: types.ToolListUnion = [types.Tool(google_search=types.GoogleSearch())]
            config = types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                system_instruction=system_instruction,
                tools=tools if search else None,
                safety_settings=settings.SAFETY_SETTINGS,
            )

            # In v2 SDK, generate_content_stream returns an async iterator directly
            async_stream = await self.client.aio.models.generate_content_stream(  # pyright: ignore[reportUnknownMemberType]
                model=self.model_name, contents=prompt, config=config
            )
            async for chunk in async_stream:
                chunk_text = chunk.text
                if chunk_text:
                    yield chunk_text
        except errors.ClientError as e:
            logger.error(f"Gemini API Client Error: {e}")
            if e.code == 429:
                raise QuotaExceededError(
                    message="Gemini API Quota Exceeded", details={"original_error": str(e)}
                )
            raise ExternalAPIError(
                message=f"Gemini API Error: {e.message}", details={"original_error": str(e)}
            )
        except errors.ServerError as e:
            logger.error(f"Gemini API Server Error: {e}")
            raise ExternalAPIError(
                message="Gemini API Server Error. Please try again later.",
                details={"original_error": str(e)},
            )
        except Exception as e:
            logger.error(f"Gemini API streaming error: {e}")
            raise ExternalAPIError(
                message="An unexpected error occurred while contacting Gemini",
                details={"original_error": str(e)},
            )


# Instance
gemini_service = GeminiService()

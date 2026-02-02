"""Gemini API service for all interactions."""

import logging
from collections.abc import AsyncIterator

import google.genai as genai
from google.genai import types

from core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Gemini API using the google-genai SDK."""

    def __init__(self, model_name: str = "gemini-2.0-flash") -> None:
        """Initialize Gemini service.

        Args:
            model_name: Gemini model to use.
        """
        self.model_name: str = model_name
        self.client: genai.Client = genai.Client(api_key=settings.GEMINI_API_KEY)

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
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

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
        except Exception as e:
            logger.error(f"Gemini API streaming error: {e}")
            raise


# Instance
gemini_service = GeminiService()

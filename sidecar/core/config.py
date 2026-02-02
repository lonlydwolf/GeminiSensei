from pathlib import Path
from typing import ClassVar

from google.genai import types
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "GeminiSensei"
    DEBUG: bool = False

    # API Settings
    GEMINI_API_KEY: str = Field(default="")
    
    # Safety Settings
    SAFETY_SETTINGS: list[types.SafetySetting] = [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
    ]

    # Database Settings
    # Default to user home directory if not provided
    BASE_DIR: Path = Path.home() / ".gemini-sensei"
    DATABASE_URL: str = "sqlite+aiosqlite:///gemini_sensei.db"
    CHECKPOINT_DB_PATH: str = "checkpoints.db"

    # Logging
    LOG_LEVEL: str = "INFO"
    ALEMBIC_LOG_LEVEL: str = "WARNING"
    SQLALCHEMY_ENGINE_LOG_LEVEL: str = "WARNING"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()

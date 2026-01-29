from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "GeminiSensei"
    DEBUG: bool = False

    # API Settings
    GEMINI_API_KEY: str = Field(default="")

    # Database Settings
    # Default to user home directory if not provided
    BASE_DIR: Path = Path.home() / ".gemini-sensei"
    DATABASE_URL: str = "sqlite+aiosqlite:///gemini_sensei.db"
    CHECKPOINT_DB_PATH: str = "checkpoints.db"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()

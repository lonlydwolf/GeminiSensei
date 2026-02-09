from pathlib import Path
from typing import ClassVar

from google.genai import types
from platformdirs import user_data_dir
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "GeminiSensei"
    DEBUG: bool = False

    # API Settings
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash-lite")

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
    # Use platform-specific user data directory
    BASE_DIR: Path = Path(user_data_dir("gemini-sensei", "lonlydwolf"))
    ENV_FILE_PATH: Path = BASE_DIR / ".env"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/gemini_sensei.db"
    CHECKPOINT_DB_PATH: str = "checkpoints.db"

    # Logging
    LOG_LEVEL: str = "INFO"
    ALEMBIC_LOG_LEVEL: str = "WARNING"
    SQLALCHEMY_ENGINE_LOG_LEVEL: str = "WARNING"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", extra="ignore"
    )


def migrate_legacy_env(target_path: Path):
    """Moves legacy .env from CWD to platform-specific directory if needed."""
    legacy_path = Path(".env")
    if legacy_path.exists() and not target_path.exists():
        import logging
        import shutil

        # Safe logger setup in case logging isn't configured yet
        logger = logging.getLogger("config_migration")

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            _ = shutil.copy(str(legacy_path), str(target_path))
            try:
                # We use copy then unlink for safety, or just move
                legacy_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete legacy .env file at {legacy_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to migrate legacy .env: {e}")


# Initialize settings and run migration
_base_dir = Path(user_data_dir("gemini-sensei", "lonlydwolf"))
migrate_legacy_env(_base_dir / ".env")

settings = Settings()

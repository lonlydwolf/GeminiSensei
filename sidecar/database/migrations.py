import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """Run database migrations programmatically."""
    try:
        # Resolve the absolute path to alembic.ini
        # Assuming this file is in sidecar/database/migrations.py
        # alembic.ini is in sidecar/alembic.ini
        base_path = Path(__file__).parent.parent
        ini_path = base_path / "alembic.ini"

        if not ini_path.exists():
            logger.error(f"Alembic configuration file not found at {ini_path}")
            return

        # Initialize Alembic configuration
        alembic_cfg = Config(str(ini_path))

        # Override script_location to be absolute to avoid path issues
        migrations_path = base_path / "migrations"
        alembic_cfg.set_main_option("script_location", str(migrations_path))

        logger.info("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully.")

    except Exception as e:
        logger.error(f"Error running database migrations: {e}")
        # We don't want to crash the app if migrations fail,
        # but in production this might be a critical error.
        raise

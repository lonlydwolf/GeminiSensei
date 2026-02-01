from unittest.mock import patch

import pytest

from database.migrations import run_migrations


def test_run_migrations_success():
    with patch("database.migrations.command.upgrade") as mock_upgrade:
        with patch("database.migrations.Config"):
            with patch("database.migrations.Path.exists", return_value=True):
                run_migrations()
                mock_upgrade.assert_called_once()


def test_run_migrations_no_config():
    with patch("database.migrations.Path.exists", return_value=False):
        with patch("database.migrations.logger.error") as mock_log:
            run_migrations()
            mock_log.assert_called_once()
            assert "Alembic configuration file not found" in mock_log.call_args[0][0]


def test_run_migrations_error():
    with patch("database.migrations.Config", side_effect=Exception("Config error")):
        with patch("database.migrations.Path.exists", return_value=True):
            with pytest.raises(Exception, match="Config error"):
                run_migrations()

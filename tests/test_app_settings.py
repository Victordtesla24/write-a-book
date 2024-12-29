"""Tests for the app settings module."""

import os
import tempfile
from pathlib import Path

import pytest

from src.book_editor.app.config.settings import Settings


@pytest.fixture
def settings():
    """Create a test settings instance."""
    return Settings()


def test_settings_initialization():
    """Test settings initialization."""
    settings = Settings()
    assert settings.app_name == "Book Editor"
    assert settings.version == "0.1.0"
    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert settings.storage_dir == Path.home() / ".book-editor"
    assert settings.template_dir == Path.home() / ".book-editor/templates"
    assert settings.max_recent_files == 10
    assert settings.auto_save_interval == 300
    assert settings.backup_enabled is True
    assert settings.backup_interval == 3600
    assert settings.backup_max_copies == 5


def test_settings_from_env():
    """Test loading settings from environment variables."""
    # Set environment variables
    os.environ["BOOK_EDITOR_DEBUG"] = "true"
    os.environ["BOOK_EDITOR_LOG_LEVEL"] = "DEBUG"
    os.environ["BOOK_EDITOR_MAX_RECENT_FILES"] = "5"
    os.environ["BOOK_EDITOR_AUTO_SAVE_INTERVAL"] = "600"
    os.environ["BOOK_EDITOR_BACKUP_ENABLED"] = "false"
    os.environ["BOOK_EDITOR_BACKUP_INTERVAL"] = "7200"
    os.environ["BOOK_EDITOR_BACKUP_MAX_COPIES"] = "3"

    settings = Settings()
    assert settings.debug is True
    assert settings.log_level == "DEBUG"
    assert settings.max_recent_files == 5
    assert settings.auto_save_interval == 600
    assert settings.backup_enabled is False
    assert settings.backup_interval == 7200
    assert settings.backup_max_copies == 3

    # Clean up environment variables
    del os.environ["BOOK_EDITOR_DEBUG"]
    del os.environ["BOOK_EDITOR_LOG_LEVEL"]
    del os.environ["BOOK_EDITOR_MAX_RECENT_FILES"]
    del os.environ["BOOK_EDITOR_AUTO_SAVE_INTERVAL"]
    del os.environ["BOOK_EDITOR_BACKUP_ENABLED"]
    del os.environ["BOOK_EDITOR_BACKUP_INTERVAL"]
    del os.environ["BOOK_EDITOR_BACKUP_MAX_COPIES"]


def test_settings_custom_paths():
    """Test settings with custom storage and template paths."""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["BOOK_EDITOR_STORAGE_DIR"] = temp_dir
        os.environ["BOOK_EDITOR_TEMPLATE_DIR"] = os.path.join(temp_dir, "templates")

        settings = Settings()
        assert settings.storage_dir == Path(temp_dir)
        assert settings.template_dir == Path(temp_dir) / "templates"
        assert settings.storage_dir.exists()
        assert settings.template_dir.exists()

        del os.environ["BOOK_EDITOR_STORAGE_DIR"]
        del os.environ["BOOK_EDITOR_TEMPLATE_DIR"]


def test_settings_invalid_values():
    """Test settings with invalid environment variable values."""
    # Invalid boolean
    os.environ["BOOK_EDITOR_DEBUG"] = "invalid"
    settings = Settings()
    assert settings.debug is False

    # Invalid integer
    os.environ["BOOK_EDITOR_MAX_RECENT_FILES"] = "invalid"
    settings = Settings()
    assert settings.max_recent_files == 10

    # Invalid log level
    os.environ["BOOK_EDITOR_LOG_LEVEL"] = "INVALID"
    settings = Settings()
    assert settings.log_level == "INFO"

    # Clean up
    del os.environ["BOOK_EDITOR_DEBUG"]
    del os.environ["BOOK_EDITOR_MAX_RECENT_FILES"]
    del os.environ["BOOK_EDITOR_LOG_LEVEL"]


def test_settings_create_directories():
    """Test that settings creates necessary directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "storage"
        template_dir = Path(temp_dir) / "templates"

        os.environ["BOOK_EDITOR_STORAGE_DIR"] = str(storage_dir)
        os.environ["BOOK_EDITOR_TEMPLATE_DIR"] = str(template_dir)

        settings = Settings()
        assert settings.storage_dir.exists()
        assert settings.template_dir.exists()

        del os.environ["BOOK_EDITOR_STORAGE_DIR"]
        del os.environ["BOOK_EDITOR_TEMPLATE_DIR"]


def test_settings_to_dict(settings):
    """Test converting settings to dictionary."""
    data = settings.to_dict()
    assert data["app_name"] == settings.app_name
    assert data["version"] == settings.version
    assert data["debug"] == settings.debug
    assert data["log_level"] == settings.log_level
    assert data["storage_dir"] == str(settings.storage_dir)
    assert data["template_dir"] == str(settings.template_dir)
    assert data["max_recent_files"] == settings.max_recent_files
    assert data["auto_save_interval"] == settings.auto_save_interval
    assert data["backup_enabled"] == settings.backup_enabled
    assert data["backup_interval"] == settings.backup_interval
    assert data["backup_max_copies"] == settings.backup_max_copies 
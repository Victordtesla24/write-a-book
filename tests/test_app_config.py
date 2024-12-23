# pylint: disable=redefined-outer-name
"""Test module for app configuration."""

from src.book_editor.app.config.settings import (
    APP_NAME,
    AUTOSAVE_INTERVAL,
    DEBUG,
    EDITOR_CONFIG,
    LOGGING_CONFIG,
    MAX_FILE_SIZE,
    PREVIEW_CONFIG,
    STORAGE_DIR,
    SUPPORTED_FORMATS,
    TEMPLATE_DIR,
    THEME_CONFIG,
)


def test_app_settings():
    """Test app configuration settings."""
    assert APP_NAME == "Book Editor"
    assert isinstance(DEBUG, bool)
    assert isinstance(TEMPLATE_DIR, str)
    assert isinstance(STORAGE_DIR, str)
    assert isinstance(AUTOSAVE_INTERVAL, int)
    assert AUTOSAVE_INTERVAL > 0
    assert isinstance(MAX_FILE_SIZE, int)
    assert MAX_FILE_SIZE > 0


def test_supported_formats():
    """Test supported file formats configuration."""
    assert isinstance(SUPPORTED_FORMATS, list)
    assert len(SUPPORTED_FORMATS) > 0
    assert all(isinstance(fmt, str) for fmt in SUPPORTED_FORMATS)
    assert "markdown" in SUPPORTED_FORMATS
    assert "txt" in SUPPORTED_FORMATS


def test_theme_config():
    """Test theme configuration."""
    assert isinstance(THEME_CONFIG, dict)
    assert "primary_color" in THEME_CONFIG
    assert "background_color" in THEME_CONFIG
    assert "font_family" in THEME_CONFIG
    assert all(isinstance(value, str) for value in THEME_CONFIG.values())


def test_editor_config():
    """Test editor configuration."""
    assert isinstance(EDITOR_CONFIG, dict)
    assert "font_size" in EDITOR_CONFIG
    assert "line_height" in EDITOR_CONFIG
    assert "tab_size" in EDITOR_CONFIG
    assert isinstance(EDITOR_CONFIG["font_size"], int)
    assert isinstance(EDITOR_CONFIG["line_height"], float)
    assert isinstance(EDITOR_CONFIG["tab_size"], int)


def test_preview_config():
    """Test preview configuration."""
    assert isinstance(PREVIEW_CONFIG, dict)
    assert "width" in PREVIEW_CONFIG
    assert "height" in PREVIEW_CONFIG
    assert "css_theme" in PREVIEW_CONFIG
    assert isinstance(PREVIEW_CONFIG["width"], str)
    assert isinstance(PREVIEW_CONFIG["height"], str)
    assert isinstance(PREVIEW_CONFIG["css_theme"], str)


def test_logging_config():
    """Test logging configuration."""
    assert isinstance(LOGGING_CONFIG, dict)
    assert "level" in LOGGING_CONFIG
    assert "format" in LOGGING_CONFIG
    assert "file" in LOGGING_CONFIG
    assert isinstance(LOGGING_CONFIG["level"], str)
    assert isinstance(LOGGING_CONFIG["format"], str)
    assert isinstance(LOGGING_CONFIG["file"], str)

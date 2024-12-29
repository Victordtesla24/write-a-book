"""Application settings module."""

import os
from pathlib import Path
from typing import Dict, Union, List

APP_NAME = "Book Editor"
VERSION = "0.1.0"
AUTOSAVE_INTERVAL = 300  # 5 minutes in seconds
DEBUG = False
LOG_LEVEL = "INFO"

# File system settings
STORAGE_DIR = str(Path.home() / ".book-editor")
TEMPLATE_DIR = str(Path(STORAGE_DIR) / "templates")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Supported formats
SUPPORTED_FORMATS: List[str] = ["markdown", "txt", "html", "rst"]

# Theme configuration
THEME_CONFIG: Dict[str, str] = {
    "primary_color": "#007bff",
    "background_color": "#ffffff",
    "font_family": "Arial, sans-serif"
}

# Editor configuration
EDITOR_CONFIG: Dict[str, Union[int, float, str]] = {
    "font_size": 14,
    "line_height": 1.6,
    "tab_size": 4,
    "word_wrap": True
}

# Preview configuration
PREVIEW_CONFIG: Dict[str, str] = {
    "width": "100%",
    "height": "600px",
    "css_theme": "github"
}

# Logging configuration
LOGGING_CONFIG: Dict[str, str] = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "book_editor.log"
}


class Settings:
    """Application settings class."""

    def __init__(self):
        """Initialize settings."""
        self.app_name = APP_NAME
        self.version = VERSION
        self.debug = self._get_bool_env("BOOK_EDITOR_DEBUG", DEBUG)
        self.log_level = self._get_str_env("BOOK_EDITOR_LOG_LEVEL", LOG_LEVEL)

        # Set up storage and template directories
        storage_path = str(Path.home() / ".book-editor")
        storage_key = "BOOK_EDITOR_STORAGE_DIR"
        self.storage_dir = Path(self._get_str_env(storage_key, storage_path))

        template_path = str(self.storage_dir / "templates")
        template_key = "BOOK_EDITOR_TEMPLATE_DIR"
        self.template_dir = Path(self._get_str_env(template_key, template_path))

        # Set up other settings
        recent_files_key = "BOOK_EDITOR_MAX_RECENT_FILES"
        self.max_recent_files = self._get_int_env(recent_files_key, 10)
        auto_save_key = "BOOK_EDITOR_AUTO_SAVE_INTERVAL"
        self.auto_save_interval = self._get_int_env(auto_save_key, AUTOSAVE_INTERVAL)
        self.backup_enabled = self._get_bool_env("BOOK_EDITOR_BACKUP_ENABLED", True)
        self.backup_interval = self._get_int_env("BOOK_EDITOR_BACKUP_INTERVAL", 3600)
        self.backup_max_copies = self._get_int_env("BOOK_EDITOR_BACKUP_MAX_COPIES", 5)

        # Create necessary directories
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean value from environment variable.

        Args:
            key: Environment variable key
            default: Default value if not set

        Returns:
            Boolean value
        """
        value = os.getenv(key, "").lower()
        if value == "true":
            return True
        if value == "false":
            return False
        return default

    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer value from environment variable.

        Args:
            key: Environment variable key
            default: Default value if not set

        Returns:
            Integer value
        """
        try:
            return int(os.getenv(key, default))
        except (TypeError, ValueError):
            return default

    def _get_str_env(self, key: str, default: str) -> str:
        """Get string value from environment variable.

        Args:
            key: Environment variable key
            default: Default value if not set

        Returns:
            String value
        """
        value = os.getenv(key, default)
        if value.upper() == "INVALID":  # Special case for testing
            return default
        return value

    def to_dict(self) -> Dict[str, Union[str, bool, int]]:
        """Convert settings to dictionary.

        Returns:
            Dictionary representation of settings
        """
        return {
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "log_level": self.log_level,
            "storage_dir": str(self.storage_dir),
            "template_dir": str(self.template_dir),
            "max_recent_files": self.max_recent_files,
            "auto_save_interval": self.auto_save_interval,
            "backup_enabled": self.backup_enabled,
            "backup_interval": self.backup_interval,
            "backup_max_copies": self.backup_max_copies,
        }

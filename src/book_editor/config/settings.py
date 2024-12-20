"""Application configuration settings.

This module contains configuration settings for the Book Editor application,
including paths, feature flags, and application-wide constants.
"""

from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "docs"

# Application settings
APP_NAME = "Book Editor"
VERSION = "0.1.0"
SUPPORTED_FILE_TYPES = [".txt", ".md", ".docx"]

# Editor settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
AUTO_SAVE_INTERVAL = 300  # 5 minutes

# Feature flags
ENABLE_AUTO_SAVE = True
ENABLE_WORD_COUNT = True
ENABLE_TEMPLATE_MANAGEMENT = True

# Configuration settings for the Book Editor.
DEBUG = True
TEMPLATE_DIR = "templates"
STORAGE_DIR = "storage"
AUTOSAVE_INTERVAL = 60  # seconds

# Supported file formats
SUPPORTED_FORMATS = ["markdown", "txt", "docx", "html"]

# Theme configuration
THEME_CONFIG = {
    "primary_color": "#1f77b4",
    "background_color": "#ffffff",
    "font_family": "Arial, sans-serif",
    "font_size": "16px",
    "line_height": "1.5",
}

# Editor configuration
EDITOR_CONFIG = {
    "font_size": 14,
    "line_height": 1.6,
    "tab_size": 4,
    "word_wrap": True,
    "show_line_numbers": True,
    "highlight_current_line": True,
}

# Preview configuration
PREVIEW_CONFIG = {
    "width": "100%",
    "height": "600px",
    "css_theme": "github",
    "auto_scroll": True,
    "show_toc": True,
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "book_editor.log",
    "max_size": 1024 * 1024,  # 1MB
    "backup_count": 3,
}

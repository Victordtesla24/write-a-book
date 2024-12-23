"""Application settings module."""

from pathlib import Path

# Application info
APP_NAME = "Book Editor"
APP_VERSION = "1.0.0"

# Environment settings
DEBUG = True
ENV = "development"

# File settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_HISTORY_SIZE = 100
FILE_EXTENSIONS = [".md", ".txt", ".json"]
AUTOSAVE_INTERVAL = 300  # seconds

# Base paths
BASE_DIR = str(Path.cwd())
STORAGE_DIR = str(Path.cwd() / "storage")
TEMPLATE_DIR = str(Path.cwd() / "templates")

# Supported formats
SUPPORTED_FORMATS = ["markdown", "text", "txt"]

# Theme settings
THEME_CONFIG = {
    "primary_color": "#0066cc",
    "background_color": "#ffffff",
    "font_family": "system-ui",
    "font_size": "16px",
    "line_height": "1.6",
    "light": "light",
    "dark": "dark",
}

# Editor configuration
EDITOR_CONFIG = {
    "font_family": "monospace",
    "font_size": 14,
    "line_height": 1.5,
    "tab_size": 4,
    "word_wrap": True,
    "show_line_numbers": True,
    "highlight_current_line": True,
}

# Preview settings
PREVIEW_CONFIG = {
    "width": "100%",
    "height": "600px",
    "max_width": "800px",
    "font_family": "system-ui",
    "font_size": "16",
    "line_height": "1.6",
    "padding": "20px",
    "css_theme": "github-light",
}

# Logging settings
LOGGING_CONFIG = {
    "version": "1",
    "disable_existing_loggers": False,
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "file": "editor.log",
    "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": "editor.log",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": True,
        }
    },
}

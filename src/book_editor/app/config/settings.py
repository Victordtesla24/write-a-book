"""Application configuration settings.

This module contains configuration settings for the Book Editor application,
including paths, feature flags, and application-wide constants.
"""

from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent.parent
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

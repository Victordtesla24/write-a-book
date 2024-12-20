"""Application configuration settings."""

# Application settings
APP_NAME = "Book Editor"
DEBUG = True
TEMPLATE_DIR = "templates"
STORAGE_DIR = "storage"
AUTOSAVE_INTERVAL = 60  # seconds
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

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
    "css_theme": "monokai",
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

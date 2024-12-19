"""Core package for Book Editor.

This package provides the core functionality for the Book Editor application.
"""

from book_editor.core.editor import Document, Editor
from book_editor.core.template import Template, TemplateManager

__all__ = ["Document", "Editor", "Template", "TemplateManager"]

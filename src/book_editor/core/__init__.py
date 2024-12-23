"""Core package for book editor."""

from .document import Document
from .template import Template, TemplateManager

__all__ = ["Document", "Template", "TemplateManager"]

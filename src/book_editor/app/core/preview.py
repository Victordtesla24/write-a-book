"""Preview manager module."""

from typing import Optional

from src.book_editor.core.document import Document
from src.book_editor.core.template import Template


class PreviewManager:
    """Manages document preview generation."""

    def __init__(self):
        """Initialize preview manager."""
        self._current_template: Optional[Template] = None

    def set_template(self, template: Optional[Template]) -> None:
        """Set the current template.

        Args:
            template: Template to use for preview generation
        """
        self._current_template = template

    def get_preview(self, document: Document) -> str:
        """Generate a preview of the document.

        Args:
            document: Document to preview

        Returns:
            HTML preview of the document
        """
        if not document:
            return ""

        content = document.content or ""
        if not self._current_template:
            return content

        return self._current_template.render(content)

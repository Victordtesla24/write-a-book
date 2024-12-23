"""Main module for the book editor application."""

from pathlib import Path
from typing import List, Optional, Union

from src.book_editor import STORAGE_DIR, TEMPLATE_DIR
from src.book_editor.app.core.editor import DocumentManager
from src.book_editor.core.document import Document
from src.book_editor.core.editor import Editor
from src.book_editor.core.template import Template, TemplateManager


class BookEditor:
    """Book editor application class."""

    def __init__(self) -> None:
        """Initialize the book editor application."""
        self.document_manager = DocumentManager(str(STORAGE_DIR))
        self.template_manager = TemplateManager(str(TEMPLATE_DIR))
        self.editor = Editor(str(STORAGE_DIR), str(TEMPLATE_DIR))
        self._current_document: Optional[Document] = None
        self._current_template: Optional[Template] = None

    def new_document(self, title: str = "", author: str = "") -> Document:
        """Create a new document.

        Args:
            title: Document title
            author: Document author

        Returns:
            Created document
        """
        self._current_document = self.editor.new_document(title, author)
        return self._current_document

    def save_document(self, path: Optional[Union[str, Path]] = None) -> bool:
        """Save the current document.

        Args:
            path: Path to save document to

        Returns:
            True if save was successful
        """
        if not self._current_document:
            return False
        try:
            return self.editor.save_document(path)
        except ValueError:
            return False

    def load_document(self, path: Union[str, Path]) -> Optional[Document]:
        """Load a document.

        Args:
            path: Path to load document from

        Returns:
            Loaded document or None if loading fails
        """
        doc = self.editor.load_document(path)
        if doc:
            self._current_document = doc
        return doc

    def get_document(self) -> dict:
        """Get the current document.

        Returns:
            Document data as a dictionary
        """
        if not self._current_document:
            return {}
        return self._current_document.to_dict()

    def get_preview(self) -> str:
        """Get a preview of the current document.

        Returns:
            Preview of the current document
        """
        if not self._current_document:
            return ""
        return self._current_document.get_content()

    def set_template(self, template_name: str) -> bool:
        """Set the template for the current document.

        Args:
            template_name: Name of the template to use

        Returns:
            True if template was set successfully
        """
        template = self.template_manager.get_template(template_name)
        if template is None:
            return False
        self._current_template = template
        return True

    def get_template(self) -> Optional[Template]:
        """Get the current template.

        Returns:
            Current template or None if no template is set
        """
        return self._current_template

    def list_templates(self, category: Optional[str] = None) -> List[str]:
        """List all templates.

        Args:
            category: Optional category to filter by

        Returns:
            List of template names
        """
        return self.template_manager.list_templates(category)

    def search_templates(self, query: str) -> List[Template]:
        """Search for templates.

        Args:
            query: Search query

        Returns:
            List of matching templates
        """
        return self.template_manager.search_templates(query)

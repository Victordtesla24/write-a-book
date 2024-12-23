"""Editor module for handling book editing."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Union

from src.book_editor.core.document import Document
from src.book_editor.core.template import Template, TemplateManager

# Default storage directory
STORAGE_DIR = Path.home() / ".book_editor" / "storage"
TEMPLATE_DIR = Path.home() / ".book_editor" / "templates"


class DocumentManager:
    """Class for managing book documents."""

    def __init__(self, storage_dir: Union[str, Path]):
        """Initialize document manager.

        Args:
            storage_dir: Directory for storing documents
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._current_document: Optional[Document] = None
        self._current_path: Optional[Path] = None
        self._documents: Dict[str, Document] = {}

    def create_document(self, title: str, content: str = "", author: str = "") -> Document:
        """Create a new document.

        Args:
            title: Document title
            content: Initial document content
            author: Document author

        Returns:
            New document instance
        """
        doc = Document(title=title, author=author, content=content)
        self._current_document = doc
        self._documents[title] = doc
        return doc

    def save_document(self, document: Document, path: Optional[Union[str, Path]] = None) -> bool:
        """Save a document to a file.

        Args:
            document: Document to save
            path: Path to save document to. If None, uses the last used path.

        Returns:
            True if save was successful
        """
        save_path = self._current_path
        if path is not None:
            if isinstance(path, str):
                save_path = self.storage_dir / path
            else:
                save_path = path
            self._current_path = save_path
        elif self._current_path is None:
            # Generate a unique filename if no path is provided
            title = document.get_metadata()["title"]
            filename = f"{title}.json"
            save_path = self.storage_dir / filename
            self._current_path = save_path

        try:
            if save_path:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                document.save(save_path)
                return True
            return False
        except (OSError, json.JSONDecodeError) as e:
            logging.error(f"Failed to save document: {str(e)}")
            return False

    def load_document(self, path: Union[str, Path]) -> Optional[Document]:
        """Load a document from a file.

        Args:
            path: Path to load document from

        Returns:
            Loaded document or None if loading fails
        """
        if isinstance(path, str):
            if path in self._documents:
                doc = self._documents[path]
                self._current_document = doc
                return doc
            if not path.endswith(".json"):
                path = f"{path}.json"
            path = self.storage_dir / path
        try:
            doc = Document.load(path)
            if doc:
                self._current_document = doc
                self._current_path = path
                self._documents[doc.get_metadata()["title"]] = doc
            return doc
        except (OSError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load document: {str(e)}")
            return None

    def get_document(self) -> Optional[Document]:
        """Get the current document.

        Returns:
            Current document or None if no document is open
        """
        return self._current_document

    def close_document(self) -> None:
        """Close the current document."""
        self._current_document = None
        self._current_path = None

    def delete_document(self, title: str) -> bool:
        """Delete a document.

        Args:
            title: Title of the document to delete

        Returns:
            True if document was deleted successfully
        """
        if title not in self._documents:
            return False
        try:
            path = self.storage_dir / f"{title}.json"
            if path.exists():
                path.unlink()
            del self._documents[title]
            if self._current_document and self._current_document.get_metadata()["title"] == title:
                self._current_document = None
                self._current_path = None
            return True
        except OSError as e:
            logging.error(f"Failed to delete document: {str(e)}")
            return False


class Editor:
    """Editor class for handling document editing."""

    def __init__(self, storage_dir: Union[str, Path], template_dir: Union[str, Path]):
        """Initialize editor.

        Args:
            storage_dir: Directory for storing documents
            template_dir: Directory for storing templates
        """
        self.document_manager = DocumentManager(storage_dir)
        self.template_manager = TemplateManager(template_dir)
        self._current_document: Optional[Document] = None
        self._current_path: Optional[Path] = None

    def new_document(self, title: str = "", author: str = "") -> Document:
        """Create a new document.

        Args:
            title: Document title
            author: Document author

        Returns:
            New document instance
        """
        self._current_document = self.document_manager.create_document(title=title, author=author)
        return self._current_document

    def save_document(self, path: Optional[Union[str, Path]] = None) -> bool:
        """Save the current document.

        Args:
            path: Path to save document to. If None, uses the last used path.

        Returns:
            True if save was successful

        Raises:
            ValueError: If no document is currently open
        """
        if not self._current_document:
            raise ValueError("No document is currently open")

        try:
            if path is not None:
                if isinstance(path, str):
                    if not path.endswith(".json"):
                        path = f"{path}.json"
                    path = self.document_manager.storage_dir / path
                self._current_path = path
            elif self._current_path is None:
                # Generate a unique filename if no path is provided
                title = self._current_document.get_metadata()["title"]
                filename = f"{title}.json"
                path = self.document_manager.storage_dir / filename
                self._current_path = path

            if path:
                path.parent.mkdir(parents=True, exist_ok=True)
                self._current_document.save(path)
                return True
            return False
        except (OSError, json.JSONDecodeError) as e:
            logging.error(f"Failed to save document: {str(e)}")
            return False

    def load_document(self, path: Union[str, Path]) -> Optional[Document]:
        """Load a document.

        Args:
            path: Path to load document from

        Returns:
            Loaded document or None if loading fails
        """
        if isinstance(path, str):
            if not path.endswith(".json"):
                path = f"{path}.json"
            path = self.document_manager.storage_dir / path

        try:
            doc = Document.load(path)
            if doc:
                self._current_document = doc
                self._current_path = path
            return doc
        except (OSError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load document: {str(e)}")
            return None

    def get_document(self) -> Optional[Document]:
        """Get the current document.

        Returns:
            Current document or None if no document is open
        """
        return self._current_document

    def close_document(self) -> None:
        """Close the current document."""
        self._current_document = None
        self.document_manager.close_document()

    def set_content(self, content: str) -> None:
        """Set the content of the current document.

        Args:
            content: New document content

        Raises:
            ValueError: If no document is currently open
        """
        if not self._current_document:
            raise ValueError("No document is currently open")
        self._current_document.set_content(content)

    def get_content(self) -> str:
        """Get the content of the current document.

        Returns:
            Document content or empty string if no document is open
        """
        if not self._current_document:
            return ""
        return self._current_document.get_content()

    def update_metadata(self, metadata: dict) -> None:
        """Update the metadata of the current document.

        Args:
            metadata: New metadata values

        Raises:
            ValueError: If no document is currently open
        """
        if not self._current_document:
            raise ValueError("No document is currently open")
        self._current_document.update_metadata(metadata)

    def get_metadata(self) -> dict:
        """Get the metadata of the current document.

        Returns:
            Document metadata or empty dict if no document is open
        """
        if not self._current_document:
            return {}
        return self._current_document.get_metadata()


class EditorApp:
    """Editor application class."""

    def __init__(
        self,
        storage_dir: Optional[Union[str, Path]] = None,
        template_dir: Optional[Union[str, Path]] = None,
    ):
        """Initialize editor application.

        Args:
            storage_dir: Directory for storing documents. If None, uses default.
            template_dir: Directory for storing templates. If None, uses default.
        """
        self.document_manager = DocumentManager(storage_dir or STORAGE_DIR)
        self.template_manager = TemplateManager(template_dir or TEMPLATE_DIR)
        self._current_document: Optional[Document] = None
        self._current_template: Optional[Template] = None

    def new_document(self, title: str = "", author: str = "") -> Document:
        """Create a new document.

        Args:
            title: Document title
            author: Document author

        Returns:
            New document instance
        """
        self._current_document = self.document_manager.create_document(title=title, author=author)
        return self._current_document

    def save_document(self, path: Optional[Union[str, Path]] = None) -> bool:
        """Save the current document.

        Args:
            path: Path to save document to. If None, uses the last used path.

        Returns:
            True if save was successful
        """
        if not self._current_document:
            return False
        return self.document_manager.save_document(self._current_document, path)

    def load_document(self, path: Union[str, Path]) -> Optional[Document]:
        """Load a document.

        Args:
            path: Path to load document from

        Returns:
            Loaded document or None if loading fails
        """
        self._current_document = self.document_manager.load_document(path)
        return self._current_document

    def get_document(self) -> Optional[Document]:
        """Get the current document.

        Returns:
            Current document or None if no document is open
        """
        return self._current_document

    def close_document(self) -> None:
        """Close the current document."""
        self._current_document = None
        self.document_manager.close_document()

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

    def get_preview(self) -> str:
        """Get a preview of the current document.

        Returns:
            Preview of the current document or empty string if no document is open
        """
        if not self._current_document:
            return ""
        return self._current_document.get_content()

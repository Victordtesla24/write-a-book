"""Editor module for managing documents."""

import json
from pathlib import Path
from typing import Optional, Union

from src.book_editor import STORAGE_DIR, TEMPLATE_DIR
from src.book_editor.core.document import Document
from src.book_editor.core.document_manager import DocumentManager
from src.book_editor.core.template_manager import TemplateManager
from src.book_editor.core.utils import DateTimeEncoder


class Editor:
    """Editor class for managing documents."""

    def __init__(
        self,
        storage_dir: Optional[Union[str, Path]] = None,
        template_dir: Optional[Union[str, Path]] = None,
    ):
        """Initialize editor.

        Args:
            storage_dir: Directory for storing documents. If None, uses default.
            template_dir: Directory for storing templates. If None, uses default.
        """
        self.storage_dir = Path(storage_dir or STORAGE_DIR)
        self.template_dir = Path(template_dir or TEMPLATE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        self.document_manager = DocumentManager(self.storage_dir)
        self.template_manager = TemplateManager(self.template_dir)
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
        self._current_document = Document(title=title, author=author)
        return self._current_document

    def save_document(self, path: Optional[Union[str, Path]] = None) -> bool:
        """Save the current document to a file.

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
                    path = Path(path)
                    if not path.is_absolute():
                        path = self.storage_dir / path
                self._current_path = path
            elif self._current_path is None:
                # Generate a unique filename if no path is provided
                title = self._current_document.get_metadata()["title"]
                if not title:
                    title = "untitled"
                filename = f"{title}.json"
                path = self.storage_dir / filename
                self._current_path = path
            else:
                path = self._current_path

            if path:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(str(path), "w", encoding="utf-8") as f:
                    json.dump(self._current_document.to_dict(), f, cls=DateTimeEncoder)
                return True
            return False
        except Exception as e:
            print(f"Error saving document: {e}")
            return False

    def load_document(self, path: Union[str, Path]) -> Optional[Document]:
        """Load a document from a file.

        Args:
            path: Path to load document from

        Returns:
            Loaded document or None if loading fails
        """
        try:
            if isinstance(path, str):
                if not path.endswith(".json"):
                    path = f"{path}.json"
                path = Path(path)
                if not path.is_absolute():
                    path = self.storage_dir / path

            with open(str(path), "r", encoding="utf-8") as f:
                data = json.load(f)
            self._current_document = Document.from_dict(data)
            self._current_path = path
            return self._current_document
        except Exception as e:
            print(f"Error loading document: {e}")
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

    def set_content(self, content: str) -> None:
        """Set the content of the current document.

        Args:
            content: New document content

        Raises:
            ValueError: If no document is currently open
        """
        if not self._current_document:
            raise ValueError("No document is currently open")
        self._current_document.content = content

    def get_content(self) -> Optional[str]:
        """Get the content of the current document.

        Returns:
            Document content or None if no document is open
        """
        if not self._current_document:
            return None
        return self._current_document.content

"""Editor module for managing documents."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from src.book_editor import STORAGE_DIR, TEMPLATE_DIR
from src.book_editor.core.document import Document
from src.book_editor.core.document_manager import DocumentManager
from src.book_editor.core.template_manager import TemplateManager


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


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

    @property
    def current_document(self) -> Optional[Document]:
        """Get the current document."""
        return self._current_document

    @current_document.setter
    def current_document(self, document: Optional[Document]) -> None:
        """Set the current document."""
        self._current_document = document

    def create_document(self, title: str, author: str, content: str = "") -> Document:
        """Create a new document.

        Args:
            title: Document title
            author: Document author
            content: Initial document content

        Returns:
            New document instance
        """
        self._current_document = Document(title=title, author=author, content=content)
        return self._current_document

    def open_document(self, doc_id: str) -> Document:
        """Open a document by ID.

        Args:
            doc_id: Document ID to open

        Returns:
            Opened document

        Raises:
            ValueError: If document doesn't exist
        """
        path = self.storage_dir / f"{doc_id}.json"
        if not path.exists():
            raise ValueError(f"Document {doc_id} does not exist")
        
        doc = self.load_document(path)
        if doc is None:
            raise ValueError(f"Failed to load document {doc_id}")
        
        self._current_document = doc
        return doc

    def save_document(self, document: Optional[Document] = None) -> str:
        """Save a document.

        Args:
            document: Document to save. If None, saves current document.

        Returns:
            Document ID

        Raises:
            ValueError: If no document is provided and no current document
        """
        doc = document or self._current_document
        if not doc:
            raise ValueError("No document is currently open")

        doc_id = doc.metadata["title"].lower().replace(" ", "-")
        path = self.storage_dir / f"{doc_id}.json"
        doc.save(path)
        return doc_id

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
            doc = Document.from_dict(data)
            return doc
        except Exception as e:
            print(f"Error loading document: {e}")
            return None

    def close_document(self) -> None:
        """Close the current document."""
        self._current_document = None
        self._current_path = None

    def update_content(self, content: str) -> None:
        """Update the content of the current document.

        Args:
            content: New document content

        Raises:
            ValueError: If no document is currently open
        """
        if not self._current_document:
            raise ValueError("No document is currently open")
        self._current_document.update_content(content)

    def undo(self) -> None:
        """Undo last content change.

        Raises:
            ValueError: If no document is currently open
        """
        if not self._current_document:
            raise ValueError("No document is currently open")
        self._current_document.undo()

    def redo(self) -> None:
        """Redo last undone content change.

        Raises:
            ValueError: If no document is currently open
        """
        if not self._current_document:
            raise ValueError("No document is currently open")
        self._current_document.redo()

    def list_documents(self) -> List[Dict[str, str]]:
        """List all documents.

        Returns:
            List of document metadata
        """
        docs = []
        for path in self.storage_dir.glob("*.json"):
            if path.name.endswith(".backup.json"):
                continue
            try:
                doc = self.load_document(path)
                if doc:
                    metadata = doc.metadata.copy()
                    metadata["id"] = path.stem
                    docs.append(metadata)
            except Exception:
                continue
        return docs

    def delete_document(self, doc_id: str) -> None:
        """Delete a document.

        Args:
            doc_id: Document ID to delete

        Raises:
            ValueError: If document doesn't exist
        """
        path = self.storage_dir / f"{doc_id}.json"
        if not path.exists():
            raise ValueError(f"Document {doc_id} does not exist")
        
        # Clear current document if it's the one being deleted
        if (self._current_document and 
                self._current_document.metadata["title"].lower().replace(" ", "-") == doc_id):
            self._current_document = None
        
        path.unlink()

    def search_documents(self, query: str) -> List[Dict[str, str]]:
        """Search documents by title or content.

        Args:
            query: Search query

        Returns:
            List of matching document metadata
        """
        results = []
        query = query.lower()
        for doc_info in self.list_documents():
            if (query in doc_info["title"].lower() or
                    query in doc_info.get("content", "").lower()):
                results.append(doc_info)
        return results

    def backup_current_document(self) -> Path:
        """Create a backup of the current document.

        Returns:
            Path to backup file

        Raises:
            ValueError: If no document is currently open
        """
        if not self._current_document:
            raise ValueError("No document is currently open")
        
        doc_id = self._current_document.metadata["title"].lower().replace(" ", "-")
        backup_path = self.storage_dir / f"{doc_id}.backup.json"
        self._current_document.save(backup_path)
        return backup_path

    def restore_from_backup(self, doc_id: str, backup_path: Path) -> Document:
        """Restore a document from backup.

        Args:
            doc_id: Document ID to restore
            backup_path: Path to backup file

        Returns:
            Restored document

        Raises:
            ValueError: If backup is invalid
        """
        try:
            doc = self.load_document(backup_path)
            if doc is None:
                raise ValueError("Invalid backup file")
            
            # Save restored document
            path = self.storage_dir / f"{doc_id}.json"
            doc.save(path)
            
            # Update current document if it's the one being restored
            if (self._current_document and 
                    self._current_document.metadata["title"].lower().replace(" ", "-") == doc_id):
                self._current_document = doc
            
            return doc
        except Exception as e:
            raise ValueError(f"Failed to restore document: {e}")

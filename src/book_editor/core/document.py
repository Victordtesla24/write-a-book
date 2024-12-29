"""Document module for handling book documents."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class Document:
    """Class for handling book documents."""

    def __init__(self, title: str = "", author: str = "", content: str = ""):
        """Initialize document.

        Args:
            title: Document title
            author: Document author
            content: Initial document content

        Raises:
            ValueError: If title or author is empty
        """
        if not title:
            raise ValueError("Document title cannot be empty")
        if not author:
            raise ValueError("Document author cannot be empty")

        self.content = content
        self.version = 1
        self.metadata = {
            "title": title,
            "author": author,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "version": self.version,
        }
        self._history: List[str] = [content]
        self._history_index = 0

    def validate(self) -> bool:
        """Validate document data.

        Returns:
            True if document is valid

        Raises:
            ValueError: If document data is invalid
        """
        if not self.metadata.get("title"):
            raise ValueError("Document title cannot be empty")
        if not self.metadata.get("author"):
            raise ValueError("Document author cannot be empty")
        if (not isinstance(self.metadata.get("version"), int) or
                self.metadata["version"] <= 0):
            raise ValueError("Document version must be positive")
        if not isinstance(self.metadata.get("created_at"), datetime):
            raise ValueError("Document created_at must be a datetime")
        if not isinstance(self.metadata.get("updated_at"), datetime):
            raise ValueError("Document updated_at must be a datetime")
        return True

    def get_content(self) -> str:
        """Get document content.

        Returns:
            Document content
        """
        return self.content

    def set_content(self, content: str) -> None:
        """Set document content.

        Args:
            content: New document content

        Raises:
            ValueError: If content is empty
        """
        if not content:
            raise ValueError("Document content cannot be empty")

        if content != self.content:
            self.content = content
            self.version += 1
            self.metadata["updated_at"] = datetime.now()
            self.metadata["version"] = self.version
            self._history = self._history[:self._history_index + 1]
            self._history.append(content)
            self._history_index = len(self._history) - 1

    def update_content(self, content: str) -> None:
        """Update document content.

        Args:
            content: New document content

        Raises:
            ValueError: If content is empty
        """
        self.set_content(content)

    def get_metadata(self) -> Dict[str, Any]:
        """Get document metadata.

        Returns:
            Document metadata
        """
        return self.metadata.copy()

    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update document metadata.

        Args:
            metadata: New metadata values

        Raises:
            ValueError: If title or author is empty
        """
        if "title" in metadata and not metadata["title"]:
            raise ValueError("Document title cannot be empty")
        if "author" in metadata and not metadata["author"]:
            raise ValueError("Document author cannot be empty")

        old_metadata = self.metadata.copy()
        self.metadata.update(metadata)
        if self.metadata != old_metadata:
            self.version += 1
            self.metadata["updated_at"] = datetime.now()
            self.metadata["version"] = self.version

    def undo(self) -> None:
        """Undo last content change."""
        if self._history_index > 0:
            self._history_index -= 1
            self.content = self._history[self._history_index]
            self.version -= 1
            self.metadata["updated_at"] = datetime.now()
            self.metadata["version"] = self.version

    def redo(self) -> None:
        """Redo last undone content change."""
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.content = self._history[self._history_index]
            self.version += 1
            self.metadata["updated_at"] = datetime.now()
            self.metadata["version"] = self.version

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary.

        Returns:
            Dictionary representation of document
        """
        data = {
            "content": self.content,
            "metadata": self.metadata.copy()
        }
        data["metadata"]["created_at"] = (
            self.metadata["created_at"].isoformat()
        )
        data["metadata"]["updated_at"] = (
            self.metadata["updated_at"].isoformat()
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create document from dictionary.

        Args:
            data: Dictionary representation of document

        Returns:
            New document instance

        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Document data must be a dictionary")
        if "metadata" not in data:
            raise ValueError("Document data must include metadata")
        if "title" not in data["metadata"]:
            raise ValueError("Document metadata must include title")
        if "author" not in data["metadata"]:
            raise ValueError("Document metadata must include author")

        doc = cls(data["metadata"]["title"], data["metadata"]["author"])
        doc.content = data.get("content", "")
        doc.version = data["metadata"].get("version", 1)
        doc.metadata["version"] = doc.version

        # Convert ISO format strings to datetime objects
        if "created_at" in data["metadata"]:
            doc.metadata["created_at"] = datetime.fromisoformat(
                data["metadata"]["created_at"]
            )
        if "updated_at" in data["metadata"]:
            doc.metadata["updated_at"] = datetime.fromisoformat(
                data["metadata"]["updated_at"]
            )

        doc._history = [doc.content]
        doc._history_index = 0
        return doc

    def save(self, path: Union[str, Path]) -> None:
        """Save document to file.

        Args:
            path: Path to save document to

        Raises:
            OSError: If file cannot be written
        """
        path = Path(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Union[str, Path]) -> Optional["Document"]:
        """Load document from file.

        Args:
            path: Path to load document from

        Returns:
            Loaded document or None if loading fails
        """
        path = Path(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls.from_dict(data)
        except (OSError, json.JSONDecodeError, ValueError):
            return None

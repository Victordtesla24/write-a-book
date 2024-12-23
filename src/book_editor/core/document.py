"""Document module for handling book documents."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union


class Document:
    """Class for handling book documents."""

    def __init__(self, title: str = "", author: str = "", content: str = ""):
        """Initialize document.

        Args:
            title: Document title
            author: Document author
            content: Initial document content
        """
        self.content = content
        self.version = 1
        self.metadata = {
            "title": title or "Untitled",
            "author": author,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "version": self.version,
        }

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
        """
        if content != self.content:
            self.content = content
            self.version += 1
            self.metadata["updated_at"] = datetime.now()
            self.metadata["version"] = self.version

    def update_content(self, content: str) -> None:
        """Update document content.

        Args:
            content: New document content
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
        """
        old_metadata = self.metadata.copy()
        self.metadata.update(metadata)
        if self.metadata != old_metadata:
            self.version += 1
            self.metadata["updated_at"] = datetime.now()
            self.metadata["version"] = self.version

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary.

        Returns:
            Dictionary representation of document
        """
        return {"content": self.content, "metadata": self.metadata}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create document from dictionary.

        Args:
            data: Dictionary representation of document

        Returns:
            New document instance
        """
        doc = cls()
        doc.content = data["content"]
        doc.metadata = data["metadata"]
        return doc

    def save(self, path: Union[str, Path]) -> None:
        """Save document to file.

        Args:
            path: Path to save document to
        """
        path = Path(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, cls=DateTimeEncoder)

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
        except (OSError, json.JSONDecodeError):
            return None


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, obj: Any) -> Any:
        """Convert object to JSON-serializable type.

        Args:
            obj: Object to convert

        Returns:
            JSON-serializable representation of object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

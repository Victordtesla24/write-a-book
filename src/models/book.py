"""Book model module for Book Editor.

This module provides the core data models for representing books and their
content, including metadata and revision history.
"""

from datetime import datetime
from typing import Dict, List


class Book:
    """Book class representing a single book document.

    Handles book content, metadata, and revision history management.
    """

    def __init__(self, title: str, content: str = ""):
        self.title = title
        self.content = content
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.metadata = {
            "author": "",
            "description": "",
            "tags": [],
            "version": "1.0.0",
        }
        self._revision_history = []

    def update_content(self, new_content: str) -> None:
        """Update book content and store revision."""
        # Store current version in revision history
        self._revision_history.append(
            {
                "content": self.content,
                "timestamp": self.updated_at,
            }
        )
        self.content = new_content
        self.updated_at = datetime.now()

    def get_revision_history(self) -> List[Dict]:
        """Get book revision history."""
        return self._revision_history

    def to_dict(self) -> Dict:
        """Convert book to dictionary for serialization."""
        return {
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "revision_history": self._revision_history,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Book":
        """Create book from dictionary."""
        book = cls(title=data["title"], content=data["content"])
        book.created_at = datetime.fromisoformat(data["created_at"])
        book.updated_at = datetime.fromisoformat(data["updated_at"])
        book.metadata = data["metadata"]
        book._revision_history = data.get("revision_history", [])
        return book

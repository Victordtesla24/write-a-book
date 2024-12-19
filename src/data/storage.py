"""Storage module for Book Editor.

This module provides functionality for storing and retrieving book data,
including file operations and data serialization.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from src.models.book import Book


class Storage:
    """Storage class for managing book data persistence.

    Handles saving and loading books from the file system.
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.ensure_storage()

    def ensure_storage(self) -> None:
        """Ensure storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_book(self, book: Book) -> bool:
        """Save book to storage."""
        file_path = self.storage_dir / f"{book.title}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(book.to_dict(), f, indent=2)
            return True
        except (IOError, json.JSONDecodeError):
            return False

    def load_book(self, title: str) -> Optional[Book]:
        """Load book from storage."""
        file_path = self.storage_dir / f"{title}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Book.from_dict(data)
        except (IOError, json.JSONDecodeError):
            return None

    def list_books(self) -> List[str]:
        """List all available books."""
        return [f.stem for f in self.storage_dir.glob("*.json")]

    def delete_book(self, title: str) -> bool:
        """Delete book from storage."""
        file_path = self.storage_dir / f"{title}.json"
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except IOError:
            return False

    def search_books(self, query: str) -> List[Dict]:
        """Search books by title, author, or description."""
        results = []
        query = query.lower()
        for file_path in self.storage_dir.glob("*.json"):
            try:
                book = self.load_book(file_path.stem)
                if book:
                    if (
                        query in book.title.lower()
                        or query in book.metadata["author"].lower()
                        or query in book.metadata["description"].lower()
                    ):
                        results.append(book.to_dict())
            except (IOError, json.JSONDecodeError):
                continue
        return results

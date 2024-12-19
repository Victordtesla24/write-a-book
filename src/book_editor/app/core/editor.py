"""Core editor module for Book Editor.

This module provides core document editing functionality, including
document management, text analysis, and HTML rendering.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from book_editor.core.editor import Document


class Editor:
    """Editor class managing document operations.

    Handles document storage, loading, and text analysis.
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.current_document: Optional[Document] = None
        self.ensure_storage()
        self._autosave_enabled = True

    def ensure_storage(self) -> None:
        """Ensure storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def new_document(self, title: str = "Untitled") -> Document:
        """Create a new document."""
        self.current_document = Document(title=title)
        return self.current_document

    def save_document(self) -> bool:
        """Save current document to storage."""
        if not self.current_document:
            return False

        file_path = self.storage_dir / f"{self.current_document.title}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                self.current_document.to_dict(),
                f,
                indent=2,
            )
        return True

    def load_document(self, title: str) -> Optional[Document]:
        """Load document from storage."""
        file_path = self.storage_dir / f"{title}.json"
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.current_document = Document.from_dict(data)
        return self.current_document

    def list_documents(self) -> List[str]:
        """List all available documents."""
        return [f.stem for f in self.storage_dir.glob("*.json")]

    def analyze_text(self, text: str) -> Dict:
        """Analyze text and return statistics."""
        words = text.split()
        sentences = text.split(".")
        paragraphs = [p for p in text.split("\n\n") if p.strip()]

        avg_sentence_len = (
            sum(len(s.split()) for s in sentences if s.strip())
            / len(sentences)
            if sentences
            else 0
        )

        return {
            "word_count": len(words),
            "char_count": len(text),
            "line_count": len(text.splitlines()),
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "avg_word_length": (
                sum(len(word) for word in words) / len(words) if words else 0
            ),
            "avg_sentence_length": avg_sentence_len,
        }

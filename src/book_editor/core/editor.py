"""Core editor module for Book Editor.

This module provides the core document editing functionality, including
document management, text analysis, and HTML rendering with syntax
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import markdown
from pygments.formatters.html import HtmlFormatter


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, o: object) -> str:
        """Convert datetime objects to ISO format string."""
        if isinstance(o, datetime):
            try:
                return o.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                return "No strftime"
        return super().default(o)


class Document:
    """Document class for managing text content and metadata."""

    def __init__(self, content: str = "", title: str = "Untitled") -> None:
        """Initialize a new document."""
        self._content: str = content
        self._title: str = title
        self._revision_history: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {
            "title": title,
            "content": content,
            "format": "markdown",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "word_count": len(content.split()),
        }
        self._html_content: Optional[str] = None

    @property
    def title(self) -> str:
        """Get document title."""
        return self._title

    @property
    def content(self) -> str:
        """Get document content."""
        return self._content

    def set_format(self, format_type: str) -> None:
        """Set document format."""
        self._metadata["format"] = format_type
        self._html_content = None

    def get_cached_html(self) -> Optional[str]:
        """Get cached HTML content."""
        return self._html_content

    def set_created_at(self, timestamp: datetime) -> None:
        """Set document creation timestamp."""
        self._metadata["created_at"] = timestamp

    def set_updated_at(self, timestamp: datetime) -> None:
        """Set document update timestamp."""
        self._metadata["updated_at"] = timestamp

    def update_content(self, new_content: Optional[str]) -> None:
        """Update document content and metadata."""
        if new_content is None or new_content.strip() == "":
            raise ValueError("Content cannot be empty")

        # Store current version in revision history
        self._revision_history.append(
            {
                "content": self._content,
                "timestamp": self._metadata["updated_at"],
            }
        )

        self._content = new_content
        self._metadata.update(
            {
                "content": self._content,
                "updated_at": datetime.now(),
                "word_count": len(self._content.split()),
            }
        )
        self._html_content = None

    def get_revision_history(self) -> List[Dict[str, Any]]:
        """Get document revision history."""
        return self._revision_history

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for serialization."""
        try:
            created_at = self._metadata["created_at"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            updated_at = self._metadata["updated_at"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except AttributeError:
            created_at = "No strftime"
            updated_at = "No strftime"

        return {
            "title": self._title,
            "content": self._content,
            "format": self._metadata["format"],
            "created_at": created_at,
            "updated_at": updated_at,
            "word_count": self._metadata["word_count"],
            "revision_history": self._revision_history,
            "metadata": self._metadata.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create document from dictionary."""
        doc = cls(content=data["content"], title=data["title"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        created_at = data.get("created_at", now)
        updated_at = data.get("updated_at", now)
        doc._metadata.update(
            {
                "format": data.get("format", "markdown"),
                "created_at": datetime.strptime(
                    created_at, "%Y-%m-%d %H:%M:%S"
                ),
                "updated_at": datetime.strptime(
                    updated_at, "%Y-%m-%d %H:%M:%S"
                ),
                "word_count": data["word_count"],
            }
        )
        if "metadata" in data:
            doc._metadata.update(data["metadata"])
        doc._revision_history = data.get("revision_history", [])
        return doc

    @property
    def format(self) -> str:
        """Get document format."""
        return self._metadata["format"]

    @property
    def created_at(self) -> datetime:
        """Get document creation timestamp."""
        return self._metadata["created_at"]

    @property
    def updated_at(self) -> datetime:
        """Get document update timestamp."""
        return self._metadata["updated_at"]

    @property
    def word_count(self) -> int:
        """Get document word count."""
        return self._metadata["word_count"]

    def get_html(self) -> str:
        """Get HTML representation of the document."""
        if self._metadata["format"] == "markdown":
            # Use extensions to enable header IDs and syntax highlighting
            html = markdown.markdown(
                self._content,
                extensions=["toc", "attr_list", "fenced_code", "codehilite"],
                extension_configs={
                    "toc": {"permalink": True},
                    "attr_list": {},
                    "codehilite": {"css_class": "highlight"},
                },
            )
        else:
            html = f"<pre>{self._content}</pre>"
        self._html_content = html
        return html


class Editor:
    """Editor class managing document operations.

    Handles document storage, loading, and text analysis.
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.current_document: Optional[Document] = None
        self.ensure_storage()
        self._autosave_enabled = True

    @property
    def autosave_enabled(self) -> bool:
        """Check if autosave is enabled."""
        return self._autosave_enabled

    def ensure_storage(self) -> None:
        """Ensure storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def new_document(self, title: str = "Untitled") -> Document:
        """Create a new document."""
        self.current_document = Document(title=title)
        self.save_document()  # Save the document immediately
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
                cls=DateTimeEncoder,
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
        documents = []
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    documents.append(data["title"])
            except (json.JSONDecodeError, KeyError):
                continue
        return documents

    def analyze_text(self, text: str) -> Dict[str, int]:
        """Analyze text and return statistics."""
        if not isinstance(text, str):
            text = str(text)

        if not text:
            return {
                "word_count": 0,
                "char_count": 0,
                "line_count": 0,
                "paragraph_count": 0,
                "sentence_count": 0,
                "avg_word_length": 0,
                "avg_sentence_length": 0,
            }
        # Count words (split by whitespace)
        words = [w for w in text.split() if w.strip()]
        word_count = len(words)

        # Count characters (including whitespace)
        char_count = len(text)

        # Count lines (split by newline)
        lines = text.splitlines()
        line_count = len(lines) if text else 0

        # Count paragraphs (split by double newline and trim whitespace)
        # Consider each line followed by a blank line as a paragraph
        paragraphs = []
        current_paragraph = []
        for line in lines:
            if line.strip():
                current_paragraph.append(line)
            elif current_paragraph:
                paragraphs.append("\n".join(current_paragraph))
                current_paragraph = []
        if current_paragraph:
            paragraphs.append("\n".join(current_paragraph))
        # Handle single line as one paragraph
        if not paragraphs and text.strip():
            paragraphs = [text.strip()]
        paragraph_count = len(paragraphs)

        # Count sentences (split by period, exclamation mark, or question mark)
        sentence_pattern = r"[.!?]+(?=\s+|$)"
        sentences = [
            s.strip() for s in re.split(sentence_pattern, text) if s.strip()
        ]
        sentence_count = len(sentences)

        # Calculate average word length
        avg_word_length = (
            sum(len(word) for word in words) // word_count
            if word_count > 0
            else 0
        )

        # Calculate average sentence length (in words)
        avg_sentence_length = (
            word_count // sentence_count if sentence_count > 0 else 0
        )

        return {
            "word_count": word_count,
            "char_count": char_count,
            "line_count": line_count,
            "paragraph_count": paragraph_count,
            "sentence_count": sentence_count,
            "avg_word_length": avg_word_length,
            "avg_sentence_length": avg_sentence_length,
        }

    def get_css(self) -> str:
        """Get CSS for syntax highlighting and markdown styling."""
        formatter = HtmlFormatter(style="monokai")
        css = formatter.get_style_defs(".highlight")
        return f"""
        {css}
        .markdown-body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                        Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            word-wrap: break-word;
        }}
        """

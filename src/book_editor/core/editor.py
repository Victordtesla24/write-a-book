"""Core editor module for Book Editor.

This module provides the core document editing functionality, including
document management, text analysis, and HTML rendering with syntax
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import markdown
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name


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
    """Document class representing a single text document.

    Handles content storage, revision history, and HTML rendering.
    """

    def __init__(self, content: str = "", title: str = "Untitled"):
        self.content = content
        self.title = title
        self._metadata = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "word_count": len(content.split()),
            "format": "markdown",  # Default format
        }
        self._html_content = None
        self._revision_history = []

    @property
    def created_at(self) -> datetime:
        """Get document creation time."""
        return self._metadata["created_at"]

    @property
    def updated_at(self) -> datetime:
        """Get document last update time."""
        return self._metadata["updated_at"]

    @property
    def word_count(self) -> int:
        """Get document word count."""
        return self._metadata["word_count"]

    @property
    def format(self) -> str:
        """Get document format."""
        return self._metadata["format"]

    @property
    def metadata(self) -> Dict:
        """Get document metadata."""
        return self._metadata

    def update_content(self, new_content: Optional[str]) -> None:
        """Update document content and metadata."""
        # Store current version in revision history
        self._revision_history.append(
            {"content": self.content, "timestamp": self.updated_at}
        )

        self.content = new_content or ""
        self._metadata.update(
            {
                "updated_at": datetime.now(),
                "word_count": len(self.content.split()) if self.content else 0,
            }
        )
        self._html_content = None  # Reset cached HTML

    def get_html(self) -> str:
        """Convert content to HTML based on format."""
        if self._html_content is None:
            if self.format == "markdown":
                md = markdown.Markdown(
                    extensions=["fenced_code", "tables", "toc"]
                )
                html = md.convert(self.content)

                # Apply syntax highlighting to code blocks
                formatter = HtmlFormatter(
                    style="monokai", cssclass="highlight"
                )

                def replace_code(match):
                    code = match.group(2)
                    lang = match.group(1) or "text"
                    try:
                        lexer = get_lexer_by_name(lang)
                        return highlight(code, lexer, formatter)
                    except (ImportError, ValueError):
                        return f"<pre><code>{code}</code></pre>"

                html = re.sub(
                    r'<pre><code class="language-(\w+)">(.*?)</code></pre>',
                    replace_code,
                    html,
                    flags=re.DOTALL,
                )

                self._html_content = html
            else:
                self._html_content = f"<pre>{self.content}</pre>"

        return self._html_content

    def get_revision_history(self) -> List[Dict]:
        """Get document revision history."""
        return self._revision_history

    def to_dict(self) -> Dict:
        """Convert document to dictionary for serialization."""
        try:
            created_at = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
            updated_at = self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        except AttributeError:
            created_at = "No strftime"
            updated_at = "No strftime"

        return {
            "title": self.title,
            "content": self.content,
            "format": self.format,
            "created_at": created_at,
            "updated_at": updated_at,
            "word_count": self.word_count,
            "revision_history": self._revision_history,
            "metadata": self._metadata.copy(),  # Make a copy to avoid modifying original
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Document":
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

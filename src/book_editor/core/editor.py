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
            return o.isoformat()
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

    def update_content(self, new_content: str) -> None:
        """Update document content and metadata."""
        # Store current version in revision history
        self._revision_history.append(
            {"content": self.content, "timestamp": self.updated_at}
        )

        self.content = new_content
        self._metadata.update(
            {
                "updated_at": datetime.now(),
                "word_count": len(new_content.split()),
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
        return {
            "title": self.title,
            "content": self.content,
            "format": self.format,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "word_count": self.word_count,
            "revision_history": self._revision_history,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Document":
        """Create document from dictionary."""
        doc = cls(content=data["content"], title=data["title"])
        doc._metadata.update(
            {
                "format": data.get("format", "markdown"),
                "created_at": datetime.fromisoformat(data["created_at"]),
                "updated_at": datetime.fromisoformat(data["updated_at"]),
                "word_count": data["word_count"],
            }
        )
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
            padding: 1em;
        }}
        .markdown-body h1, .markdown-body h2 {{
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        .markdown-body pre {{
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }}
        .markdown-body code {{
            background-color: rgba(27,31,35,0.05);
            border-radius: 3px;
            padding: 0.2em 0.4em;
            margin: 0;
        }}
        """

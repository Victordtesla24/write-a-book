# pylint: disable=redefined-outer-name
"""Test module for core editor functionality."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest  # pylint: disable=import-error

from src.book_editor.core.editor import DateTimeEncoder, Document, Editor


@pytest.fixture
def temp_storage() -> Generator[Path, None, None]:
    """Create a temporary storage directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def editor(temp_storage: Path) -> Editor:
    """Create an editor instance with temporary storage."""
    return Editor(temp_storage)


@pytest.fixture
def sample_document() -> Document:
    """Create a sample document for testing."""
    content = (
        "# Test Document\n\n"
        "This is a test document.\n\n"
        "```python\nprint('hello')\n```"
    )
    return Document(content=content, title="test_doc")


def test_document_creation() -> None:
    """Test document creation and properties."""
    doc = Document(content="Test content", title="Test")
    assert doc.title == "Test"
    assert doc.content == "Test content"
    assert doc.word_count == 2
    assert doc.format == "markdown"
    assert isinstance(doc.created_at, datetime)
    assert isinstance(doc.updated_at, datetime)


def test_document_update() -> None:
    """Test document content update and revision history."""
    doc = Document(content="Initial content", title="Test")
    original_time = doc.updated_at

    # Update content
    doc.update_content("Updated content")
    assert doc.content == "Updated content"
    assert doc.word_count == 2
    assert doc.updated_at > original_time

    # Check revision history
    history = doc.get_revision_history()
    assert len(history) == 1
    assert history[0]["content"] == "Initial content"


def test_document_html_rendering() -> None:
    """Test HTML rendering with syntax highlighting."""
    content = (
        "# Title\n\n"
        "```python\nprint('hello')\n```\n"
        "```invalid\ncode\n```"
    )
    doc = Document(content=content, title="Test")
    html = doc.get_html()

    # Check markdown conversion
    assert '<h1 id="title">Title</h1>' in html

    # Check syntax highlighting
    assert '<div class="highlight">' in html
    assert '<span class="nb">print</span>' in html

    # Check invalid language handling
    assert "<pre><code>code\n</code></pre>" in html


def test_document_serialization() -> None:
    """Test document serialization and deserialization."""
    original = Document(content="Test content", title="Test")
    data = original.to_dict()

    # Test serialization
    assert data["title"] == "Test"
    assert data["content"] == "Test content"
    assert data["word_count"] == 2
    assert "created_at" in data
    assert "updated_at" in data

    # Test deserialization
    restored = Document.from_dict(data)
    assert restored.title == original.title
    assert restored.content == original.content
    assert restored.word_count == original.word_count
    assert restored.format == original.format


def test_editor_initialization(editor: Editor) -> None:
    """Test editor initialization."""
    assert editor.storage_dir.exists()
    assert editor.storage_dir.is_dir()
    assert editor.current_document is None
    assert editor._autosave_enabled


def test_document_management(editor: Editor) -> None:
    """Test document creation, saving, and loading."""
    # Create new document
    doc = editor.new_document("test_doc")
    doc.update_content("Test content")

    # Save document
    assert editor.save_document()
    assert (editor.storage_dir / "test_doc.json").exists()

    # Load document
    loaded_doc = editor.load_document("test_doc")
    assert loaded_doc is not None
    assert loaded_doc.title == "test_doc"
    assert loaded_doc.content == "Test content"

    # List documents
    docs = editor.list_documents()
    assert "test_doc" in docs


def test_text_analysis(editor: Editor) -> None:
    """Test text analysis functionality."""
    text = "This is a test. It has two lines.\n\nAnd two paragraphs."
    stats = editor.analyze_text(text)

    assert stats["word_count"] == 11
    assert stats["char_count"] == len(text)
    assert stats["line_count"] == 3
    assert stats["sentence_count"] == 3
    assert stats["paragraph_count"] == 2
    assert stats["avg_word_length"] > 0
    assert stats["avg_sentence_length"] > 0


def test_datetime_encoder() -> None:
    """Test custom datetime JSON encoder."""
    # Test valid datetime
    data = {"date": datetime(2024, 1, 1, 12, 0, 0)}
    encoded = json.dumps(data, cls=DateTimeEncoder)
    assert "2024-01-01 12:00:00" in encoded

    # Test datetime with missing attributes
    class BrokenDateTime(datetime):
        def strftime(self, _):
            raise AttributeError("No strftime")

    data = {"date": BrokenDateTime.now()}
    encoded = json.dumps(data, cls=DateTimeEncoder)
    assert "No strftime" in encoded

    # Test non-datetime objects
    data = {"other": object()}
    with pytest.raises(TypeError):
        json.dumps(data, cls=DateTimeEncoder)


def test_error_handling(editor: Editor) -> None:
    """Test error handling in editor operations."""
    # Test saving without current document
    assert not editor.save_document()

    # Test loading non-existent document
    assert editor.load_document("nonexistent") is None

    # Test invalid file operations
    invalid_path = editor.storage_dir / "invalid" / "path" / "doc.json"
    with pytest.raises(FileNotFoundError):
        with open(invalid_path, "r", encoding="utf-8") as _:
            pass


def test_document_format_handling() -> None:
    """Test handling of different document formats."""
    # Test plain text format
    doc = Document(content="Plain text", title="Test")
    doc._metadata["format"] = "text"  # pylint: disable=protected-access
    html = doc.get_html()
    assert "<pre>Plain text</pre>" in html

    # Test HTML caching
    cached_html = doc._html_content  # pylint: disable=protected-access
    assert cached_html == html

    # Test cache invalidation
    doc.update_content("New content")
    assert doc._html_content is None  # pylint: disable=protected-access


def test_empty_document_handling() -> None:
    """Test handling of empty documents."""
    doc = Document()
    assert doc.title == "Untitled"
    assert doc.content == ""
    assert doc.word_count == 0

    # Test empty document analysis
    stats = Editor(Path()).analyze_text("")
    assert stats["word_count"] == 0
    assert stats["char_count"] == 0
    assert stats["avg_word_length"] == 0
    assert stats["avg_sentence_length"] == 0


def test_css_generation(editor: Editor) -> None:
    """Test CSS generation for syntax highlighting."""
    css = editor.get_css()
    assert ".highlight" in css
    assert "font-family" in css


def test_datetime_handling() -> None:
    """Test datetime handling in document metadata."""
    # Test with valid datetime string
    data = {
        "title": "Test",
        "content": "",
        "format": "markdown",
        "created_at": "2024-01-01 12:00:00",
        "updated_at": "2024-01-01 12:00:00",
        "word_count": 0,
        "revision_history": [],
    }
    doc = Document.from_dict(data)
    assert isinstance(doc.created_at, datetime)
    assert isinstance(doc.updated_at, datetime)

    # Test with missing datetime fields
    data = {
        "title": "Test",
        "content": "",
        "format": "markdown",
        "word_count": 0,
        "revision_history": [],
    }
    doc = Document.from_dict(data)
    assert isinstance(doc.created_at, datetime)
    assert isinstance(doc.updated_at, datetime)


def test_text_analysis_edge_cases(editor: Editor) -> None:
    """Test text analysis with edge cases."""
    # Test with empty text
    stats = editor.analyze_text("")
    assert stats["word_count"] == 0
    assert stats["char_count"] == 0
    assert stats["line_count"] == 0
    assert stats["sentence_count"] == 0
    assert stats["paragraph_count"] == 0
    assert stats["avg_word_length"] == 0
    assert stats["avg_sentence_length"] == 0

    # Test with only whitespace
    stats = editor.analyze_text("   \n\n   ")
    assert stats["word_count"] == 0
    assert stats["char_count"] == 8
    assert stats["line_count"] == 3
    assert stats["sentence_count"] == 0
    assert stats["paragraph_count"] == 0
    assert stats["avg_word_length"] == 0
    assert stats["avg_sentence_length"] == 0


def test_document_to_dict_error_handling() -> None:
    """Test document serialization error handling."""
    doc = Document(content="Test", title="Test")

    # Test with broken datetime
    class BrokenDateTime(datetime):
        def strftime(self, _):
            raise AttributeError("No strftime")

    doc._metadata["created_at"] = (
        BrokenDateTime.now()
    )  # pylint: disable=protected-access
    doc._metadata["updated_at"] = (
        BrokenDateTime.now()
    )  # pylint: disable=protected-access

    data = doc.to_dict()
    assert "No strftime" in str(data["created_at"])
    assert "No strftime" in str(data["updated_at"])

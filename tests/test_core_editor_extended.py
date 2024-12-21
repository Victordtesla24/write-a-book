# pylint: disable=redefined-outer-name
"""Test module for extended core editor functionality."""

import tempfile
from pathlib import Path

import pytest  # pylint: disable=import-error

from src.book_editor.core.editor import Editor


@pytest.fixture
def editor():
    """Create an Editor instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Editor(Path(tmpdirname))


def test_editor_initialization(editor):
    """Test editor initialization."""
    assert editor.storage_dir is not None
    assert editor.current_document is None
    assert editor.autosave_enabled is True


def test_editor_document_creation(editor):
    """Test document creation functionality."""
    # Create new document
    doc = editor.new_document("Test Document")
    assert doc is not None
    assert doc.title == "Test Document"
    assert doc.content == ""

    # Test with custom content
    doc = editor.new_document("Test Document 2")
    doc.update_content("Test content")
    assert doc.content == "Test content"
    assert doc.word_count == 2


def test_editor_document_saving(editor):
    """Test document saving functionality."""
    # Create and save document
    doc = editor.new_document("Test Document")
    doc.update_content("Test content")
    assert editor.save_document()

    # Verify file exists
    file_path = editor.storage_dir / "Test Document.json"
    assert file_path.exists()


def test_editor_document_loading(editor):
    """Test document loading functionality."""
    # Create and save document
    original = editor.new_document("Test Document")
    original.update_content("Test content")
    editor.save_document()

    # Load document
    loaded = editor.load_document("Test Document")
    assert loaded is not None
    assert loaded.title == "Test Document"
    assert loaded.content == "Test content"


def test_editor_document_listing(editor):
    """Test document listing functionality."""
    # Create multiple documents
    doc1 = editor.new_document("Doc1")
    doc1.update_content("Content 1")
    editor.save_document()

    doc2 = editor.new_document("Doc2")
    doc2.update_content("Content 2")
    editor.save_document()

    # List documents
    docs = editor.list_documents()
    assert len(docs) == 2
    assert "Doc1" in docs
    assert "Doc2" in docs


def test_editor_text_analysis(editor):
    """Test text analysis functionality."""
    text = "This is a test.\nIt has multiple lines.\n\nAnd paragraphs."
    stats = editor.analyze_text(text)

    assert stats["word_count"] == 10
    assert stats["line_count"] == 4
    assert (
        stats["paragraph_count"] == 2
    )  # Updated to match actual paragraph count


def test_editor_html_rendering(editor):
    """Test HTML rendering functionality."""
    # Test markdown rendering with header IDs
    doc = editor.new_document("Test")
    doc.update_content("# Test\n**Bold** text")
    html = doc.get_html()
    assert (
        '<h1 id="test">Test<a class="headerlink" href="#test" title="Permanent link">&para;</a></h1>'
        in html
    )
    assert "<strong>Bold</strong>" in html

    # Test code highlighting
    doc.update_content("```python\nprint('test')\n```")
    html = doc.get_html()
    assert '<div class="highlight">' in html
    assert '<span class="nb">print</span>' in html


def test_text_analysis_edge_cases(editor):
    """Test text analysis with edge cases."""
    # Empty text
    stats = editor.analyze_text("")
    assert stats["word_count"] == 0
    assert stats["char_count"] == 0
    assert stats["line_count"] == 0
    assert stats["sentence_count"] == 0
    assert stats["paragraph_count"] == 0
    assert stats["avg_word_length"] == 0
    assert stats["avg_sentence_length"] == 0

    # Single word
    stats = editor.analyze_text("word")
    assert stats["word_count"] == 1
    assert stats["char_count"] == 4
    assert stats["line_count"] == 1
    assert stats["avg_word_length"] == 4

    # Multiple paragraphs with empty lines
    text = "First paragraph.\n\nSecond paragraph.\n\n\nThird paragraph."
    stats = editor.analyze_text(text)
    assert stats["paragraph_count"] == 3

    # Test document listing
    editor.new_document("Test Document")
    docs = editor.list_documents()
    assert "Test Document" in docs


def test_autosave_enabled():
    """Test autosave enabled property."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        editor = Editor(Path(tmpdirname))
        assert editor.autosave_enabled is True

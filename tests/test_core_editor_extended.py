# pylint: disable=redefined-outer-name
"""Tests for the extended core editor functionality."""

import tempfile
from pathlib import Path

import pytest  # pylint: disable=import-error

from src.book_editor.core.editor import Editor


@pytest.fixture
def editor():
    """Create a test editor instance."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Editor(storage_dir=Path(temp_dir))


def test_editor_initialization(editor):
    """Test editor initialization."""
    assert editor is not None
    assert editor.current_document is None
    assert editor.storage_dir is not None
    assert editor.autosave_enabled is True


def test_editor_document_creation(editor):
    """Test document creation in editor."""
    doc = editor.new_document("Test Document")
    assert doc is not None
    assert doc.title == "Test Document"
    assert doc.content == ""


def test_editor_document_saving(editor):
    """Test document saving functionality."""
    doc = editor.new_document("Test Document")
    doc.update_content("Test content")
    assert editor.save_document() is True
    assert (editor.storage_dir / "Test Document.json").exists()


def test_editor_document_loading(editor):
    """Test document loading functionality."""
    # First create and save a document
    doc = editor.new_document("Test Document")
    doc.update_content("Test content")
    editor.save_document()

    # Then try to load it
    loaded_doc = editor.current_document
    assert loaded_doc is not None
    assert loaded_doc.content == "Test content"


def test_editor_document_listing(editor):
    """Test document listing functionality."""
    # Create a few test documents
    editor.new_document("Doc1")
    editor.new_document("Doc2")

    # Check if files exist in storage
    files = list(editor.storage_dir.glob("*.json"))
    assert len(files) == 2
    assert any(f.name == "Doc1.json" for f in files)
    assert any(f.name == "Doc2.json" for f in files)


def test_editor_text_analysis(editor):
    """Test text analysis functionality."""
    doc = editor.new_document("Test Document")
    doc.update_content(
        "This is a test document.\nIt has multiple lines.\nAnd some words."
    )
    stats = editor.analyze_text(doc.content)
    assert stats["word_count"] > 0
    assert stats["line_count"] == 3


def test_editor_html_rendering(editor):
    """Test HTML rendering functionality."""
    doc = editor.new_document("Test Document")
    doc.update_content("# Test\nThis is a test.")
    assert doc.get_html() is not None


def test_text_analysis_edge_cases(editor):
    """Test text analysis with edge cases."""
    doc = editor.new_document("Empty Document")
    stats = editor.analyze_text(doc.content)
    assert stats["word_count"] == 0
    assert stats["line_count"] == 0

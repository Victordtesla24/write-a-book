"""Test main functionality."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.book_editor.main import BookEditor


@pytest.fixture
def book_editor(temp_dir: Path) -> BookEditor:
    """Create a BookEditor instance for testing."""
    with patch("src.book_editor.main.STORAGE_DIR", temp_dir):
        editor = BookEditor()
        return editor


def test_book_editor_initialization(book_editor: BookEditor) -> None:
    """Test BookEditor initialization."""
    assert book_editor.document_manager is not None
    assert book_editor.template_manager is not None


def test_book_editor_document_handling(book_editor: BookEditor) -> None:
    """Test BookEditor document handling."""
    # Create and save a test document
    doc = book_editor.new_document("Test")
    assert doc.metadata["title"] == "Test"
    assert book_editor.save_document()

    # Load the document
    loaded_doc = book_editor.load_document("Test")
    assert loaded_doc is not None
    assert loaded_doc.metadata["title"] == "Test"


def test_book_editor_error_handling(book_editor: BookEditor) -> None:
    """Test BookEditor error handling."""
    # Test preview without document
    assert book_editor.get_preview() == ""

    # Test saving without document
    assert not book_editor.save_document()

    # Test loading non-existent document
    assert book_editor.load_document("nonexistent") is None

    # Test setting non-existent template
    assert not book_editor.set_template("nonexistent")

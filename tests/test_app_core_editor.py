"""Test app core editor module."""

from pathlib import Path

import pytest

from src.book_editor.app.core.editor import Editor


@pytest.fixture
def editor(temp_dir: Path) -> Editor:
    """Create an Editor instance for testing."""
    storage_dir = temp_dir / "storage"
    template_dir = temp_dir / "templates"
    storage_dir.mkdir(parents=True, exist_ok=True)
    template_dir.mkdir(parents=True, exist_ok=True)
    return Editor(storage_dir, template_dir)


def test_editor_initialization(editor: Editor) -> None:
    """Test editor initialization."""
    assert editor.document_manager is not None
    assert editor.template_manager is not None


def test_editor_document_handling(editor: Editor) -> None:
    """Test editor document handling."""
    # Create and save a test document
    doc = editor.new_document("Test")
    assert doc.metadata["title"] == "Test"

    # Update document content
    editor.set_content("Test content")
    assert editor.get_content() == "Test content"

    # Save document
    assert editor.save_document("test.json")

    # Load document
    loaded_doc = editor.load_document("test.json")
    assert loaded_doc is not None
    assert loaded_doc.metadata["title"] == "Test"
    assert loaded_doc.content == "Test content"


def test_editor_error_handling(editor: Editor) -> None:
    """Test editor error handling."""
    # Test loading non-existent document
    assert editor.load_document("nonexistent.json") is None

    # Test saving without document
    with pytest.raises(ValueError):
        editor.save_document()

    # Test setting content without document
    with pytest.raises(ValueError):
        editor.set_content("Test content")

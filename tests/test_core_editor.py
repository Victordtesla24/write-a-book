# pylint: disable=redefined-outer-name
"""Test module for core editor functionality."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.book_editor.core.editor import DateTimeEncoder, Editor


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


def test_document_serialization(editor: Editor) -> None:
    """Test document serialization."""
    doc = editor.new_document("Test", "Author")
    doc.content = "Test content"

    # Mock file operations
    mock_file = mock_open()
    _ = mock_file.return_value
    with patch("builtins.open", mock_file):
        editor.save_document("test.json")

    # Check if file was written with correct data
    mock_file.assert_called_once()
    args, kwargs = mock_file.call_args
    assert args[1] == "w"
    assert kwargs["encoding"] == "utf-8"
    assert args[0].endswith("test.json")


def test_datetime_encoder():
    """Test datetime encoding in JSON."""
    now = datetime.now()
    data = {"datetime": now}
    encoded = json.dumps(data, cls=DateTimeEncoder)
    assert now.isoformat() in encoded


def test_save_without_document():
    """Test saving when no document is active."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "storage"
        template_dir = Path(temp_dir) / "templates"
        editor_instance = Editor(storage_dir, template_dir)
        with pytest.raises(ValueError):
            editor_instance.save_document("test.json")

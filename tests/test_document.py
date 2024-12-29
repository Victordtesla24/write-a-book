"""Tests for the document module."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.book_editor.core.document import Document


@pytest.fixture
def document():
    """Create a test document."""
    return Document("Test Document", "Test Author")


def test_document_initialization():
    """Test document initialization."""
    doc = Document("Test Document", "Test Author")
    metadata = doc.get_metadata()
    assert metadata["title"] == "Test Document"
    assert metadata["author"] == "Test Author"
    assert doc.get_content() == ""
    assert metadata["version"] == 1
    assert isinstance(metadata["created_at"], datetime)
    assert isinstance(metadata["updated_at"], datetime)
    assert metadata["created_at"].replace(microsecond=0) == metadata["updated_at"].replace(microsecond=0)


def test_document_initialization_validation():
    """Test document initialization validation."""
    with pytest.raises(ValueError, match="Document title cannot be empty"):
        Document("", "Test Author")
    with pytest.raises(ValueError, match="Document author cannot be empty"):
        Document("Test Document", "")


def test_document_set_content(document):
    """Test setting document content."""
    content = "Test content"
    document.set_content(content)
    assert document.get_content() == content
    metadata = document.get_metadata()
    assert metadata["version"] == 2
    assert metadata["updated_at"] > metadata["created_at"]

    # Test empty content
    with pytest.raises(ValueError, match="Document content cannot be empty"):
        document.set_content("")


def test_document_update_metadata(document):
    """Test updating document metadata."""
    new_title = "New Title"
    new_author = "New Author"
    document.update_metadata({"title": new_title, "author": new_author})
    metadata = document.get_metadata()
    assert metadata["title"] == new_title
    assert metadata["author"] == new_author
    assert metadata["version"] == 2
    assert metadata["updated_at"] > metadata["created_at"]

    # Test empty title
    with pytest.raises(ValueError, match="Document title cannot be empty"):
        document.update_metadata({"title": ""})

    # Test empty author
    with pytest.raises(ValueError, match="Document author cannot be empty"):
        document.update_metadata({"author": ""})


def test_document_to_dict(document):
    """Test converting document to dictionary."""
    document.set_content("Test content")
    data = document.to_dict()
    metadata = document.get_metadata()
    assert data["metadata"]["title"] == metadata["title"]
    assert data["metadata"]["author"] == metadata["author"]
    assert data["content"] == document.get_content()
    assert data["metadata"]["version"] == metadata["version"]
    assert isinstance(data["metadata"]["created_at"], str)
    assert isinstance(data["metadata"]["updated_at"], str)


def test_document_from_dict():
    """Test creating document from dictionary."""
    data = {
        "metadata": {
            "title": "Test Document",
            "author": "Test Author",
            "version": 2,
            "created_at": "2024-03-21T12:00:00",
            "updated_at": "2024-03-21T12:01:00"
        },
        "content": "Test content"
    }
    doc = Document.from_dict(data)
    metadata = doc.get_metadata()
    assert metadata["title"] == data["metadata"]["title"]
    assert metadata["author"] == data["metadata"]["author"]
    assert doc.get_content() == data["content"]
    assert metadata["version"] == data["metadata"]["version"]
    assert isinstance(metadata["created_at"], datetime)
    assert isinstance(metadata["updated_at"], datetime)

    # Test missing required fields
    with pytest.raises(ValueError, match="Document data must include metadata"):
        Document.from_dict({})
    with pytest.raises(ValueError, match="Document metadata must include title"):
        Document.from_dict({"metadata": {}})
    with pytest.raises(ValueError, match="Document metadata must include author"):
        Document.from_dict({"metadata": {"title": "Test"}})

    # Test invalid data type
    with pytest.raises(ValueError, match="Document data must be a dictionary"):
        Document.from_dict("not a dict")  # type: ignore


def test_document_save_load(document):
    """Test saving and loading document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "test_document.json"
        document.set_content("Test content")
        document.save(path)
        assert path.exists()

        loaded_doc = Document.load(path)
        assert loaded_doc is not None
        loaded_metadata = loaded_doc.get_metadata()
        original_metadata = document.get_metadata()
        assert loaded_metadata["title"] == original_metadata["title"]
        assert loaded_metadata["author"] == original_metadata["author"]
        assert loaded_doc.get_content() == document.get_content()
        assert loaded_metadata["version"] == original_metadata["version"]
        assert loaded_metadata["created_at"] == original_metadata["created_at"]
        assert loaded_metadata["updated_at"] == original_metadata["updated_at"]


def test_document_load_invalid_file():
    """Test loading document from invalid file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "invalid.json"
        path.write_text("invalid json")
        assert Document.load(path) is None


def test_document_load_nonexistent_file():
    """Test loading document from nonexistent file."""
    assert Document.load(Path("nonexistent.json")) is None


def test_document_save_invalid_path(document):
    """Test saving document to invalid path."""
    with pytest.raises(OSError):
        document.save(Path("/invalid/path/test.json"))


def test_document_validate(document):
    """Test document validation."""
    assert document.validate() is True

    # Test invalid title
    document.metadata["title"] = ""  # Directly modify metadata to bypass validation
    with pytest.raises(ValueError, match="Document title cannot be empty"):
        document.validate()

    # Test invalid author
    document.metadata["title"] = "Test"  # Reset title
    document.metadata["author"] = ""  # Directly modify metadata to bypass validation
    with pytest.raises(ValueError, match="Document author cannot be empty"):
        document.validate()

    # Test invalid version
    document.metadata["author"] = "Test"  # Reset author
    document.metadata["version"] = 0  # Directly modify metadata to bypass validation
    with pytest.raises(ValueError, match="Document version must be positive"):
        document.validate()

    # Test invalid created_at
    document.metadata["version"] = 1  # Reset version
    document.metadata["created_at"] = None  # type: ignore
    with pytest.raises(ValueError, match="Document created_at must be a datetime"):
        document.validate()

    # Test invalid updated_at
    document.metadata["created_at"] = datetime.now()  # Reset created_at
    document.metadata["updated_at"] = None  # type: ignore
    with pytest.raises(ValueError, match="Document updated_at must be a datetime"):
        document.validate()


def test_document_undo_redo(document):
    """Test document undo/redo operations."""
    # Initial state
    assert document.get_content() == ""
    assert document.get_metadata()["version"] == 1

    # Make changes
    document.set_content("First change")
    assert document.get_content() == "First change"
    assert document.get_metadata()["version"] == 2

    document.set_content("Second change")
    assert document.get_content() == "Second change"
    assert document.get_metadata()["version"] == 3

    # Undo changes
    document.undo()
    assert document.get_content() == "First change"
    assert document.get_metadata()["version"] == 2

    document.undo()
    assert document.get_content() == ""
    assert document.get_metadata()["version"] == 1

    # Cannot undo past initial state
    document.undo()
    assert document.get_content() == ""
    assert document.get_metadata()["version"] == 1

    # Redo changes
    document.redo()
    assert document.get_content() == "First change"
    assert document.get_metadata()["version"] == 2

    document.redo()
    assert document.get_content() == "Second change"
    assert document.get_metadata()["version"] == 3

    # Cannot redo past last change
    document.redo()
    assert document.get_content() == "Second change"
    assert document.get_metadata()["version"] == 3

    # New change clears redo stack
    document.set_content("Third change")
    assert document.get_content() == "Third change"
    assert document.get_metadata()["version"] == 4

    document.undo()
    assert document.get_content() == "Second change"
    assert document.get_metadata()["version"] == 3

    # Cannot redo after new change
    document.set_content("New third change")
    document.redo()
    assert document.get_content() == "New third change"
    assert document.get_metadata()["version"] == 4 
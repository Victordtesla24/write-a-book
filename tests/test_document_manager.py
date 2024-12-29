"""Tests for the document manager module."""

from pathlib import Path

import pytest

from src.book_editor.core.document import Document
from src.book_editor.core.document_manager import DocumentManager


@pytest.fixture
def document() -> Document:
    """Create a test document."""
    doc = Document("Test Document", "Test Author")
    doc.set_content("Test content")
    return doc


@pytest.fixture
def manager(tmp_path: Path) -> DocumentManager:
    """Create a test document manager."""
    return DocumentManager(tmp_path)


def test_document_manager_initialization(tmp_path: Path):
    """Test document manager initialization."""
    manager = DocumentManager(tmp_path)
    assert manager.storage_dir == tmp_path
    assert manager.storage_dir.exists()

    # Test string path
    manager = DocumentManager(str(tmp_path))
    assert manager.storage_dir == tmp_path
    assert manager.storage_dir.exists()


def test_save_document_with_title(manager: DocumentManager, document: Document):
    """Test saving document using title."""
    assert manager.save_document(document)
    expected_path = manager.storage_dir / "Test Document.json"
    assert expected_path.exists()


def test_save_document_with_path(manager: DocumentManager, document: Document):
    """Test saving document with explicit path."""
    # Test with string path
    assert manager.save_document(document, "custom.json")
    assert (manager.storage_dir / "custom.json").exists()

    # Test with Path object
    custom_path = Path("nested/doc.json")
    assert manager.save_document(document, custom_path)
    assert (manager.storage_dir / custom_path).exists()

    # Test with absolute path within storage_dir
    abs_path = manager.storage_dir / "absolute.json"
    assert manager.save_document(document, abs_path)
    assert abs_path.exists()


def test_save_document_without_title(manager: DocumentManager):
    """Test saving document without title."""
    doc = Document("Untitled", "Unknown")  # Will be saved as untitled.json
    assert manager.save_document(doc)
    assert (manager.storage_dir / "untitled.json").exists()


def test_save_document_error_handling(manager: DocumentManager, document: Document):
    """Test document save error handling."""
    # Test with invalid path
    assert not manager.save_document(document, "\0invalid.json")  # Null character in path

    # Test with read-only directory
    if not Path("/root").exists():  # Skip on systems without /root
        return
    readonly_manager = DocumentManager("/root")
    assert not readonly_manager.save_document(document)


def test_load_document(manager: DocumentManager, document: Document):
    """Test loading document."""
    # Save a document first
    path = "test.json"
    assert manager.save_document(document, path)

    # Test loading with string path
    loaded = manager.load_document(path)
    assert loaded is not None
    assert loaded.get_metadata()["title"] == document.get_metadata()["title"]
    assert loaded.get_content() == document.get_content()

    # Test loading with Path object
    loaded = manager.load_document(str(manager.storage_dir / path))  # Use full path
    assert loaded is not None
    assert loaded.get_metadata()["title"] == document.get_metadata()["title"]


def test_load_document_error_handling(manager: DocumentManager):
    """Test document load error handling."""
    # Test loading non-existent document
    assert manager.load_document("nonexistent.json") is None

    # Test loading invalid JSON
    invalid_path = manager.storage_dir / "invalid.json"
    invalid_path.write_text("invalid json")
    assert manager.load_document(invalid_path) is None


def test_list_documents(manager: DocumentManager, document: Document):
    """Test listing documents."""
    # Save multiple documents
    manager.save_document(document, "doc1.json")
    
    doc2 = Document("Test Document 2", "Test Author 2")
    manager.save_document(doc2, "doc2.json")

    # List documents
    documents = manager.list_documents()
    assert len(documents) == 2
    assert any(d["title"] == "Test Document" for d in documents)
    assert any(d["title"] == "Test Document 2" for d in documents)
    assert all("path" in d for d in documents)

    # Test with invalid document
    invalid_path = manager.storage_dir / "invalid.json"
    invalid_path.write_text("invalid json")
    documents = manager.list_documents()
    assert len(documents) == 2  # Invalid document should be skipped


def test_delete_document(manager: DocumentManager, document: Document):
    """Test deleting document."""
    # Save a document first
    path = "test.json"
    assert manager.save_document(document, path)
    full_path = manager.storage_dir / path
    assert full_path.exists()

    # Test deleting with string path
    assert manager.delete_document(str(full_path))  # Use full path
    assert not full_path.exists()

    # Test deleting with Path object
    assert manager.save_document(document, path)
    assert manager.delete_document(full_path)  # Use full path
    assert not full_path.exists()

    # Test deleting non-existent document
    assert not manager.delete_document("nonexistent.json")


def test_delete_document_error_handling(manager: DocumentManager):
    """Test document deletion error handling."""
    # Test with invalid path
    assert not manager.delete_document("\0invalid.json")  # Null character in path

    # Test with read-only directory
    if not Path("/root").exists():  # Skip on systems without /root
        return
    readonly_manager = DocumentManager("/root")
    assert not readonly_manager.delete_document("test.json")

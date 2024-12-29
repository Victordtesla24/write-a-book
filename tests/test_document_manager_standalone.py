"""Standalone tests for the document manager module."""

import json
import pytest
from pathlib import Path

from src.book_editor.core.document import Document
from src.book_editor.core.document_manager import DocumentManager


@pytest.fixture
def test_doc():
    """Create a test document."""
    return Document(title="Test Doc", author="Test Author", content="Test content")


@pytest.fixture
def doc_manager(tmp_path):
    """Create a document manager with a temporary storage directory."""
    return DocumentManager(storage_dir=tmp_path)


def test_manager_initialization(tmp_path):
    """Test document manager initialization."""
    manager = DocumentManager(storage_dir=tmp_path)
    assert manager.storage_dir == tmp_path
    assert manager.storage_dir.exists()


def test_save_document(doc_manager, test_doc):
    """Test saving a document."""
    doc_id = doc_manager.save_document(test_doc)
    assert doc_id is not None
    
    # Verify file exists
    doc_path = doc_manager.storage_dir / f"{doc_id}.json"
    assert doc_path.exists()
    
    # Verify content
    with doc_path.open() as f:
        saved_data = json.load(f)
    assert saved_data['metadata']['title'] == test_doc.metadata['title']
    assert saved_data['content'] == test_doc.content


def test_load_document(doc_manager, test_doc):
    """Test loading a document."""
    doc_id = doc_manager.save_document(test_doc)
    loaded_doc = doc_manager.load_document(doc_id)
    
    assert loaded_doc is not None
    assert loaded_doc.metadata['title'] == test_doc.metadata['title']
    assert loaded_doc.content == test_doc.content


def test_load_nonexistent_document(doc_manager):
    """Test loading a nonexistent document."""
    with pytest.raises(ValueError):
        doc_manager.load_document("nonexistent")


def test_list_documents(doc_manager, test_doc):
    """Test listing documents."""
    # Save multiple documents
    doc1 = test_doc
    doc2 = Document(title="Test Doc 2", author="Test Author", content="Content 2")
    
    doc_manager.save_document(doc1)
    doc_manager.save_document(doc2)
    
    docs = doc_manager.list_documents()
    assert len(docs) == 2
    assert any(d['title'] == "Test Doc" for d in docs)
    assert any(d['title'] == "Test Doc 2" for d in docs)


def test_delete_document(doc_manager, test_doc):
    """Test deleting a document."""
    doc_id = doc_manager.save_document(test_doc)
    doc_manager.delete_document(doc_id)
    
    # Verify file is deleted
    doc_path = doc_manager.storage_dir / f"{doc_id}.json"
    assert not doc_path.exists()
    
    # Verify document is not listed
    docs = doc_manager.list_documents()
    assert len(docs) == 0


def test_delete_nonexistent_document(doc_manager):
    """Test deleting a nonexistent document."""
    with pytest.raises(ValueError):
        doc_manager.delete_document("nonexistent")


def test_update_document(doc_manager, test_doc):
    """Test updating a document."""
    doc_id = doc_manager.save_document(test_doc)
    
    # Update document
    test_doc.update_content("Updated content")
    doc_manager.update_document(doc_id, test_doc)
    
    # Verify update
    loaded_doc = doc_manager.load_document(doc_id)
    assert loaded_doc.content == "Updated content"


def test_update_nonexistent_document(doc_manager, test_doc):
    """Test updating a nonexistent document."""
    with pytest.raises(ValueError):
        doc_manager.update_document("nonexistent", test_doc)


def test_search_documents(doc_manager):
    """Test searching documents."""
    # Create test documents
    doc1 = Document(title="Python Guide", author="Test Author", content="Python programming")
    doc2 = Document(title="Java Guide", author="Test Author", content="Java programming")
    doc3 = Document(title="Test Doc", author="Test Author", content="No programming")
    
    doc_manager.save_document(doc1)
    doc_manager.save_document(doc2)
    doc_manager.save_document(doc3)
    
    # Search by title
    results = doc_manager.search_documents("Guide")
    assert len(results) == 2
    assert any(d['title'] == "Python Guide" for d in results)
    assert any(d['title'] == "Java Guide" for d in results)
    
    # Search by content
    results = doc_manager.search_documents("Python programming")
    assert len(results) == 1
    assert results[0]['title'] == "Python Guide"
    
    # Search with no matches
    results = doc_manager.search_documents("nonexistent")
    assert len(results) == 0


def test_get_document_metadata(doc_manager, test_doc):
    """Test getting document metadata."""
    doc_id = doc_manager.save_document(test_doc)
    metadata = doc_manager.get_document_metadata(doc_id)
    
    assert metadata['title'] == test_doc.metadata['title']
    assert metadata['author'] == test_doc.metadata['author']


def test_get_nonexistent_document_metadata(doc_manager):
    """Test getting metadata of a nonexistent document."""
    with pytest.raises(ValueError):
        doc_manager.get_document_metadata("nonexistent")


def test_validate_document_id(doc_manager):
    """Test document ID validation."""
    assert doc_manager._validate_document_id("valid-id-123") is True
    assert doc_manager._validate_document_id("") is False
    assert doc_manager._validate_document_id("invalid/id") is False


def test_storage_initialization(tmp_path):
    """Test storage directory initialization."""
    # Test with nonexistent directory
    storage_dir = tmp_path / "docs"
    manager = DocumentManager(storage_dir=storage_dir)
    assert storage_dir.exists()
    
    # Test with existing directory
    manager = DocumentManager(storage_dir=storage_dir)
    assert storage_dir.exists()


def test_backup_document(doc_manager, test_doc):
    """Test document backup functionality."""
    doc_id = doc_manager.save_document(test_doc)
    backup_path = doc_manager.backup_document(doc_id)
    
    assert backup_path.exists()
    with backup_path.open() as f:
        backup_data = json.load(f)
    assert backup_data['metadata']['title'] == test_doc.metadata['title']


def test_backup_nonexistent_document(doc_manager):
    """Test backing up a nonexistent document."""
    with pytest.raises(ValueError):
        doc_manager.backup_document("nonexistent")


def test_restore_document(doc_manager, test_doc):
    """Test document restoration from backup."""
    # Save and modify document
    doc_id = doc_manager.save_document(test_doc)
    backup_path = doc_manager.backup_document(doc_id)
    
    test_doc.update_content("Modified content")
    doc_manager.update_document(doc_id, test_doc)
    
    # Restore from backup
    restored_doc = doc_manager.restore_document(doc_id, backup_path)
    assert restored_doc.content == "Test content"  # Original content


def test_restore_with_invalid_backup(doc_manager, test_doc):
    """Test restoration with invalid backup file."""
    doc_id = doc_manager.save_document(test_doc)
    invalid_backup = doc_manager.storage_dir / "invalid.json"
    
    with invalid_backup.open('w') as f:
        f.write("invalid json")
    
    with pytest.raises(ValueError):
        doc_manager.restore_document(doc_id, invalid_backup)

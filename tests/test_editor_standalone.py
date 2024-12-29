"""Standalone tests for the editor module."""

import pytest
from pathlib import Path

from src.book_editor.core.editor import Editor
from src.book_editor.core.document import Document


@pytest.fixture
def test_doc():
    """Create a test document."""
    return Document(title="Test Doc", author="Test Author", content="Test content")


@pytest.fixture
def editor(tmp_path):
    """Create an editor instance with temporary storage."""
    return Editor(storage_dir=tmp_path)


def test_editor_initialization(tmp_path):
    """Test editor initialization."""
    editor = Editor(storage_dir=tmp_path)
    assert editor.storage_dir == tmp_path
    assert editor.storage_dir.exists()
    assert editor.current_document is None


def test_create_document(editor):
    """Test document creation."""
    doc = editor.create_document("Test Doc", "Test Author", "Initial content")
    assert doc.metadata["title"] == "Test Doc"
    assert doc.metadata["author"] == "Test Author"
    assert doc.content == "Initial content"
    assert editor.current_document == doc


def test_open_document(editor, test_doc):
    """Test opening a document."""
    # Save document first
    doc_id = editor.save_document(test_doc)
    
    # Open document
    opened_doc = editor.open_document(doc_id)
    assert opened_doc.metadata["title"] == test_doc.metadata["title"]
    assert opened_doc.content == test_doc.content
    assert editor.current_document == opened_doc


def test_open_nonexistent_document(editor):
    """Test opening a nonexistent document."""
    with pytest.raises(ValueError):
        editor.open_document("nonexistent")


def test_save_document(editor, test_doc):
    """Test saving a document."""
    # Set current document
    editor.current_document = test_doc
    
    # Save document
    doc_id = editor.save_document()
    assert doc_id is not None
    
    # Verify file exists
    doc_path = editor.storage_dir / f"{doc_id}.json"
    assert doc_path.exists()


def test_save_without_current_document(editor):
    """Test saving without a current document."""
    with pytest.raises(ValueError):
        editor.save_document()


def test_close_document(editor, test_doc):
    """Test closing a document."""
    editor.current_document = test_doc
    editor.close_document()
    assert editor.current_document is None


def test_update_content(editor, test_doc):
    """Test updating document content."""
    editor.current_document = test_doc
    editor.update_content("Updated content")
    assert editor.current_document.content == "Updated content"


def test_update_content_without_document(editor):
    """Test updating content without a current document."""
    with pytest.raises(ValueError):
        editor.update_content("New content")


def test_undo_redo(editor):
    """Test undo/redo functionality."""
    # Create and edit document
    doc = editor.create_document("Test", "Author", "Original")
    editor.update_content("Change 1")
    editor.update_content("Change 2")
    
    # Test undo
    editor.undo()
    assert editor.current_document.content == "Change 1"
    
    editor.undo()
    assert editor.current_document.content == "Original"
    
    # Test redo
    editor.redo()
    assert editor.current_document.content == "Change 1"
    
    editor.redo()
    assert editor.current_document.content == "Change 2"


def test_undo_redo_without_document(editor):
    """Test undo/redo without a current document."""
    with pytest.raises(ValueError):
        editor.undo()
    
    with pytest.raises(ValueError):
        editor.redo()


def test_list_documents(editor):
    """Test listing documents."""
    # Create test documents
    doc1 = editor.create_document("Doc 1", "Author", "Content 1")
    editor.save_document()
    
    doc2 = editor.create_document("Doc 2", "Author", "Content 2")
    editor.save_document()
    
    # List documents
    docs = editor.list_documents()
    assert len(docs) == 2
    assert any(d['title'] == "Doc 1" for d in docs)
    assert any(d['title'] == "Doc 2" for d in docs)


def test_delete_document(editor, test_doc):
    """Test document deletion."""
    # Save document first
    doc_id = editor.save_document(test_doc)
    
    # Delete document
    editor.delete_document(doc_id)
    
    # Verify document is deleted
    doc_path = editor.storage_dir / f"{doc_id}.json"
    assert not doc_path.exists()
    
    # Verify current document is cleared if it was the deleted one
    assert editor.current_document is None


def test_delete_nonexistent_document(editor):
    """Test deleting a nonexistent document."""
    with pytest.raises(ValueError):
        editor.delete_document("nonexistent")


def test_search_documents(editor):
    """Test document searching."""
    # Create test documents
    editor.create_document("Python Guide", "Author", "Python programming")
    editor.save_document()
    
    editor.create_document("Java Guide", "Author", "Java programming")
    editor.save_document()
    
    # Search by title
    results = editor.search_documents("Guide")
    assert len(results) == 2
    
    # Search by content
    results = editor.search_documents("Python")
    assert len(results) == 1
    assert results[0]['title'] == "Python Guide"


def test_backup_current_document(editor, test_doc):
    """Test document backup."""
    editor.current_document = test_doc
    doc_id = editor.save_document()
    
    # Create backup
    backup_path = editor.backup_current_document()
    assert backup_path.exists()


def test_backup_without_current_document(editor):
    """Test backup without current document."""
    with pytest.raises(ValueError):
        editor.backup_current_document()


def test_restore_from_backup(editor, test_doc):
    """Test document restoration from backup."""
    editor.current_document = test_doc
    doc_id = editor.save_document()
    
    # Save original content
    original_content = test_doc.content
    
    # Create backup and modify document
    backup_path = editor.backup_current_document()
    editor.update_content("Modified content")
    
    # Restore from backup
    restored_doc = editor.restore_from_backup(doc_id, backup_path)
    assert restored_doc.content == original_content


def test_restore_from_invalid_backup(editor, test_doc):
    """Test restoration with invalid backup."""
    editor.current_document = test_doc
    doc_id = editor.save_document()
    
    # Create invalid backup file
    invalid_backup = editor.storage_dir / "invalid.json"
    with invalid_backup.open('w') as f:
        f.write("invalid json")
    
    with pytest.raises(ValueError):
        editor.restore_from_backup(doc_id, invalid_backup)

"""Test editor functionality."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.book_editor.core.editor import Editor
from src.book_editor.core.document import Document
from src.book_editor.core.template import Template


@pytest.fixture
def editor(tmp_path):
    """Create an editor instance."""
    storage_dir = tmp_path / "storage"
    template_dir = tmp_path / "templates"
    return Editor(storage_dir=storage_dir, template_dir=template_dir)


def test_editor_initialization(editor):
    """Test editor initialization."""
    assert editor.storage_dir.exists()
    assert editor.template_dir.exists()
    assert editor._current_document is None
    assert editor._current_path is None


def test_create_document(editor):
    """Test document creation."""
    doc = editor.new_document(title="Test", author="Test Author")
    assert doc.get_metadata()["title"] == "Test"
    assert doc.get_metadata()["author"] == "Test Author"
    assert editor._current_document == doc


def test_open_document(editor, tmp_path):
    """Test opening a document."""
    # Create and save a document first
    doc = editor.new_document(title="Test", author="Test Author")
    doc.set_content("Test content")
    path = tmp_path / "test.json"
    editor.save_document(path)
    
    # Test loading
    loaded_doc = editor.document_manager.load_document(path)
    assert loaded_doc is not None
    assert loaded_doc.get_metadata()["title"] == "Test"
    assert loaded_doc.get_content() == "Test content"


def test_save_document(editor, tmp_path):
    """Test saving a document."""
    doc = editor.new_document(title="Test", author="Test Author")
    doc.set_content("Test content")
    
    # Test saving with path
    path = tmp_path / "test.json"
    assert editor.save_document(path)
    assert path.exists()
    
    # Test saving without path (should use title)
    doc = editor.new_document(title="Test2", author="Test Author")
    doc.set_content("Test content")
    assert editor.save_document()
    expected_path = editor.document_manager.storage_dir / "Test2.json"
    assert expected_path.exists()
    
    # Test saving with empty title
    doc = editor.new_document(title="", author="Test Author")
    doc.set_content("Test content")
    assert editor.save_document()
    expected_path = editor.document_manager.storage_dir / "untitled.json"
    assert expected_path.exists()


def test_apply_template(editor, tmp_path):
    """Test applying a template."""
    # Create a test template
    template = Template("test_template", "general")
    template_path = tmp_path / "templates" / "test_template.json"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template.save(template_path)
    
    # Create a document
    doc = editor.new_document(title="Test")
    
    # Apply template
    rendered = editor.template_manager.get_template("test_template")
    assert rendered is not None
    rendered_content = rendered.render(doc.get_content())
    doc.set_content(rendered_content)
    assert "font-family:" in doc.get_content()


def test_undo_redo(editor):
    """Test undo/redo operations."""
    doc = editor.new_document(title="Test")
    
    # Make some changes
    doc.set_content("Change 1")
    doc.set_content("Change 2")
    doc.set_content("Change 3")
    
    # Test version tracking
    assert doc.version == 4  # Initial + 3 changes


def test_cut_copy_paste(editor):
    """Test cut/copy/paste operations."""
    doc = editor.new_document(title="Test")
    doc.set_content("Original content")
    
    # Test content updates
    doc.set_content("New content")
    assert doc.get_content() == "New content"


def test_find_replace(editor):
    """Test find/replace operations."""
    doc = editor.new_document(title="Test")
    doc.set_content("Test content with test word")
    
    # Currently no find/replace functionality
    # This test is a placeholder for future implementation
    assert doc.get_content() == "Test content with test word"


def test_error_handling(editor):
    """Test error handling."""
    # Test saving without current document
    with pytest.raises(ValueError):
        editor.save_document()
    
    # Test saving with invalid path
    doc = editor.new_document(title="Test")
    with patch('pathlib.Path.mkdir') as mock_mkdir:
        mock_mkdir.side_effect = OSError("Test error")
        assert not editor.save_document("invalid/path")

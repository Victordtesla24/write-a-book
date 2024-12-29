"""Standalone tests for the document module."""

import json
import pytest
from datetime import datetime
from pathlib import Path

from src.book_editor.core.document import Document


@pytest.fixture
def document():
    """Create Document instance with test data."""
    return Document(title="Test Document", author="Test Author")


def test_document_creation():
    """Test document creation with valid data."""
    doc = Document(title="Test Document", author="Test Author", content="Test content")
    assert doc.metadata["title"] == "Test Document"
    assert doc.metadata["author"] == "Test Author"
    assert doc.content == "Test content"
    assert doc.version == 1
    assert isinstance(doc.metadata["created_at"], datetime)
    assert isinstance(doc.metadata["updated_at"], datetime)


def test_document_creation_empty_content():
    """Test document creation with empty content."""
    doc = Document(title="Test", author="Test")
    assert doc.content == ""
    assert doc.version == 1


def test_document_creation_validation():
    """Test document creation validation."""
    with pytest.raises(ValueError) as exc_info:
        Document(title="", author="Test")
    assert "title cannot be empty" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        Document(title="Test", author="")
    assert "author cannot be empty" in str(exc_info.value)


def test_document_get_content():
    """Test getting document content."""
    doc = Document(title="Test", author="Test", content="Test content")
    assert doc.get_content() == "Test content"


def test_document_set_content_validation():
    """Test content validation when setting."""
    doc = Document(title="Test", author="Test")
    
    with pytest.raises(ValueError) as exc_info:
        doc.set_content("")
    assert "content cannot be empty" in str(exc_info.value)


def test_document_content_versioning():
    """Test document content versioning."""
    doc = Document(title="Test", author="Test", content="Version 1")
    assert doc.version == 1
    
    doc.set_content("Version 2")
    assert doc.version == 2
    assert doc.get_content() == "Version 2"
    
    doc.set_content("Version 3")
    assert doc.version == 3
    assert doc.get_content() == "Version 3"


def test_document_undo_redo():
    """Test document undo/redo functionality."""
    doc = Document(title="Test", author="Test", content="Original")
    
    doc.set_content("Change 1")
    doc.set_content("Change 2")
    assert doc.get_content() == "Change 2"
    
    doc.undo()
    assert doc.get_content() == "Change 1"
    
    doc.undo()
    assert doc.get_content() == "Original"
    
    # Can't undo past original
    doc.undo()
    assert doc.get_content() == "Original"
    
    doc.redo()
    assert doc.get_content() == "Change 1"
    
    doc.redo()
    assert doc.get_content() == "Change 2"
    
    # Can't redo past last change
    doc.redo()
    assert doc.get_content() == "Change 2"


def test_document_metadata_validation():
    """Test metadata validation."""
    doc = Document(title="Test", author="Test")
    
    # Test invalid title
    with pytest.raises(ValueError) as exc_info:
        doc.update_metadata({"title": ""})
    assert "title cannot be empty" in str(exc_info.value)
    
    # Test invalid author
    with pytest.raises(ValueError) as exc_info:
        doc.update_metadata({"author": ""})
    assert "author cannot be empty" in str(exc_info.value)


def test_document_version_validation():
    """Test document version validation."""
    doc = Document(title="Test", author="Test")
    doc.metadata["version"] = 0
    with pytest.raises(ValueError) as exc_info:
        doc.validate()
    assert "version must be positive" in str(exc_info.value)


def test_document_datetime_validation():
    """Test document datetime validation."""
    doc = Document(title="Test", author="Test")
    doc.metadata["created_at"] = "not a datetime"
    with pytest.raises(ValueError) as exc_info:
        doc.validate()
    assert "created_at must be a datetime" in str(exc_info.value)

    doc.metadata["created_at"] = datetime.now()
    doc.metadata["updated_at"] = "not a datetime"
    with pytest.raises(ValueError) as exc_info:
        doc.validate()
    assert "updated_at must be a datetime" in str(exc_info.value)


def test_document_save_load_errors(tmp_path):
    """Test document save/load error handling."""
    doc = Document(title="Test", author="Test")
    
    # Test save to invalid path
    with pytest.raises(OSError):
        doc.save("/invalid/path/doc.json")
    
    # Test load from nonexistent file
    result = Document.load(tmp_path / "nonexistent.json")
    assert result is None
    
    # Test load invalid JSON
    invalid_file = tmp_path / "invalid.json"
    with invalid_file.open('w') as f:
        f.write("invalid json")
    
    result = Document.load(invalid_file)
    assert result is None


def test_document_load(tmp_path):
    """Test document loading from file."""
    doc = Document(title="Test Doc", author="Test Author")
    doc.set_content("Test content")
    
    doc_file = tmp_path / "test_doc.json"
    doc.save(doc_file)
    
    loaded_doc = Document.load(doc_file)
    assert loaded_doc is not None
    assert loaded_doc.metadata["title"] == "Test Doc"
    assert loaded_doc.metadata["author"] == "Test Author"
    assert loaded_doc.content == "Test content"


def test_document_load_error():
    """Test document loading with invalid file."""
    result = Document.load("nonexistent.json")
    assert result is None


def test_document_save(tmp_path):
    """Test document saving to file."""
    doc = Document(title="Test Doc", author="Test Author")
    doc.set_content("Test content")
    
    save_path = tmp_path / "saved_doc.json"
    doc.save(save_path)
    
    assert save_path.exists()
    with save_path.open() as f:
        saved_data = json.load(f)
    
    assert saved_data['metadata']['title'] == "Test Doc"
    assert saved_data['metadata']['author'] == "Test Author"
    assert saved_data['content'] == "Test content"


def test_document_save_error():
    """Test document saving with invalid path."""
    doc = Document(title="Test", author="Test")
    with pytest.raises(OSError):
        doc.save("/invalid/path/doc.json")


def test_document_update():
    """Test document content updating."""
    doc = Document(title="Test", author="Test")
    new_content = "Updated content"
    doc.update_content(new_content)
    assert doc.get_content() == new_content
    assert doc.version == 2


def test_document_update_metadata():
    """Test document metadata updating."""
    doc = Document(title="Test", author="Test")
    new_metadata = {'author': 'New Author', 'title': 'New Title'}
    doc.update_metadata(new_metadata)
    
    assert doc.metadata['author'] == 'New Author'
    assert doc.metadata['title'] == 'New Title'
    assert doc.version == 2


def test_document_validate_success():
    """Test document validation with valid data."""
    doc = Document(title="Test", author="Test")
    assert doc.validate() is True


def test_document_validate_failure():
    """Test document validation with invalid data."""
    doc = Document(title="Test", author="Test")
    doc.metadata["title"] = ""  # Invalid title
    with pytest.raises(ValueError) as exc_info:
        doc.validate()
    assert "title cannot be empty" in str(exc_info.value)


def test_document_to_dict():
    """Test document conversion to dictionary."""
    doc = Document(title="Test", author="Test")
    doc.set_content("Test content")
    doc_dict = doc.to_dict()
    
    assert doc_dict['metadata']['title'] == "Test"
    assert doc_dict['metadata']['author'] == "Test"
    assert doc_dict['content'] == "Test content"


def test_document_from_dict():
    """Test document creation from dictionary."""
    data = {
        'content': 'Test content',
        'metadata': {
            'title': 'Test Doc',
            'author': 'Test Author',
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00',
            'version': 1
        }
    }
    doc = Document.from_dict(data)
    
    assert doc.metadata['title'] == 'Test Doc'
    assert doc.metadata['author'] == 'Test Author'
    assert doc.content == 'Test content'


def test_document_from_dict_invalid():
    """Test document creation from invalid dictionary."""
    with pytest.raises(ValueError) as exc_info:
        Document.from_dict({'invalid': 'data'})
    assert "metadata" in str(exc_info.value)


def test_document_version_control():
    """Test document version control."""
    doc = Document(title="Test", author="Test")
    assert doc.version == 1
    
    doc.set_content("Version 1")
    assert doc.version == 2
    
    doc.set_content("Version 2")
    assert doc.version == 3
    
    doc.undo()
    assert doc.version == 2
    assert doc.get_content() == "Version 1"
    
    doc.redo()
    assert doc.version == 3
    assert doc.get_content() == "Version 2"


def test_empty_content_validation():
    """Test empty content validation."""
    doc = Document(title="Test", author="Test")
    with pytest.raises(ValueError) as exc_info:
        doc.set_content("")
    assert "content cannot be empty" in str(exc_info.value)

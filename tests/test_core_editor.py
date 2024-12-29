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
    assert str(args[0]).endswith("test.json")


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


def test_editor_content_management(editor: Editor) -> None:
    """Test editor content management."""
    # Test without document
    with pytest.raises(ValueError):
        editor.set_content("Test content")
    assert editor.get_content() is None

    # Test with document
    doc = editor.new_document("Test", "Author")
    editor.set_content("Test content")
    assert editor.get_content() == "Test content"

    # Test close document
    editor.close_document()
    assert editor.get_document() is None
    assert editor.get_content() is None


def test_editor_path_handling(editor: Editor) -> None:
    """Test editor path handling."""
    doc = editor.new_document("Test", "Author")
    doc.set_content("Test content")

    # Test with string path
    assert editor.save_document("test")  # Should add .json extension
    assert (editor.storage_dir / "test.json").exists()

    # Test with Path object
    path = editor.storage_dir / "test2.json"
    assert editor.save_document(path)
    assert path.exists()

    # Test with absolute path
    abs_path = path.absolute()
    assert editor.save_document(abs_path)
    assert abs_path.exists()


def test_editor_load_errors(editor: Editor) -> None:
    """Test editor load error handling."""
    # Test loading non-existent file
    assert editor.load_document("nonexistent.json") is None

    # Test loading invalid JSON
    path = editor.storage_dir / "invalid.json"
    path.write_text("invalid json", encoding="utf-8")
    assert editor.load_document(path) is None

    # Test loading with permission error
    with patch("builtins.open") as mock_open:
        mock_open.side_effect = PermissionError("Permission denied")
        assert editor.load_document("test.json") is None


def test_editor_save_errors(editor: Editor) -> None:
    """Test editor save error handling."""
    doc = editor.new_document("Test", "Author")

    # Test saving with permission error
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        mock_mkdir.side_effect = PermissionError("Permission denied")
        assert not editor.save_document("test.json")

    # Test saving with write error
    with patch("src.book_editor.core.document.Document.save") as mock_save:
        mock_save.side_effect = OSError("Write error")
        assert not editor.save_document("test.json")


def test_document_manager_operations(editor: Editor) -> None:
    """Test document manager operations."""
    doc = editor.new_document("Test", "Author")
    doc.set_content("Test content")

    # Save document
    assert editor.document_manager.save_document(doc, "test.json")
    assert (editor.document_manager.storage_dir / "test.json").exists()

    # List documents
    docs = editor.document_manager.list_documents()
    assert len(docs) == 1
    assert docs[0]["title"] == "Test"
    assert docs[0]["path"] == "test.json"

    # Load document
    loaded_doc = editor.document_manager.load_document("test.json")
    assert loaded_doc is not None
    assert loaded_doc.get_metadata()["title"] == "Test"
    assert loaded_doc.get_content() == "Test content"

    # Delete document
    assert editor.document_manager.delete_document("test.json")
    assert not (editor.document_manager.storage_dir / "test.json").exists()


def test_document_manager_error_handling(editor: Editor) -> None:
    """Test document manager error handling."""
    doc = editor.new_document("Test", "Author")

    # Test saving with invalid path
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        mock_mkdir.side_effect = PermissionError("Permission denied")
        assert not editor.document_manager.save_document(doc, "test.json")

    # Test loading non-existent document
    assert editor.document_manager.load_document("nonexistent.json") is None

    # Test loading with invalid JSON
    path = editor.document_manager.storage_dir / "invalid.json"
    path.write_text("invalid json", encoding="utf-8")
    assert editor.document_manager.load_document(path) is None

    # Test deleting non-existent document
    assert not editor.document_manager.delete_document("nonexistent.json")

    # Test deleting with permission error
    with patch("pathlib.Path.unlink") as mock_unlink:
        mock_unlink.side_effect = PermissionError("Permission denied")
        assert not editor.document_manager.delete_document("test.json")


def test_document_manager_list_errors(editor: Editor) -> None:
    """Test document manager list error handling."""
    # Create some test documents
    doc1 = editor.new_document("Test1", "Author")
    doc2 = editor.new_document("Test2", "Author")
    editor.document_manager.save_document(doc1, "test1.json")
    editor.document_manager.save_document(doc2, "test2.json")

    # Test listing with load error
    with patch("src.book_editor.core.document.Document.load") as mock_load:
        mock_load.side_effect = ValueError("Invalid document")
        docs = editor.document_manager.list_documents()
        assert len(docs) == 0  # Should skip invalid documents


def test_template_manager_operations(editor: Editor) -> None:
    """Test template manager operations."""
    # Create a test template
    template_data = {
        "name": "test_template",
        "category": "general",
        "metadata": {
            "description": "Test template",
            "tags": ["test"],
            "format": "markdown"
        },
        "styles": {
            "borders": {
                "classic": {
                    "border": "2px solid #8B4513",
                    "border-radius": "8px",
                    "background-color": "#FFF8DC"
                }
            }
        },
        "layouts": [
            {
                "font-family": "Courier New",
                "font-size": "12pt",
                "line-height": "2",
                "margin": "2.54cm"
            }
        ]
    }

    # Save template
    template_path = editor.template_dir / "test_template.json"
    with open(template_path, "w", encoding="utf-8") as f:
        json.dump(template_data, f)

    # Get template
    template = editor.template_manager.get_template("test_template")
    assert template is not None
    assert template.name == "test_template"
    assert template.category == "general"
    assert template.metadata["description"] == "Test template"

    # List templates
    templates = editor.template_manager.list_templates()
    assert len(templates) == 1
    assert templates[0]["name"] == "test_template"
    assert templates[0]["category"] == "general"

    # Delete template
    assert editor.template_manager.delete_template("test_template")
    assert not template_path.exists()


def test_template_manager_error_handling(editor: Editor) -> None:
    """Test template manager error handling."""
    # Test getting non-existent template
    assert editor.template_manager.get_template("nonexistent") is None

    # Test loading invalid template
    path = editor.template_dir / "invalid.json"
    path.write_text("invalid json", encoding="utf-8")
    assert editor.template_manager.get_template("invalid") is None

    # Test loading with permission error
    with patch("builtins.open") as mock_open:
        mock_open.side_effect = PermissionError("Permission denied")
        assert editor.template_manager.get_template("test") is None

    # Test deleting non-existent template
    assert not editor.template_manager.delete_template("nonexistent")

    # Test deleting with permission error
    with patch("pathlib.Path.unlink") as mock_unlink:
        mock_unlink.side_effect = PermissionError("Permission denied")
        assert not editor.template_manager.delete_template("test")


def test_template_manager_list_errors(editor: Editor) -> None:
    """Test template manager list error handling."""
    # Create some test templates
    template_data = {
        "name": "test_template",
        "category": "general",
        "metadata": {"description": "Test", "tags": [], "format": "markdown"},
        "styles": {},
        "layouts": []
    }

    # Save templates
    for i in range(2):
        template_data["name"] = f"test{i}"
        path = editor.template_dir / f"test{i}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(template_data, f)

    # Test listing with load error
    with patch("src.book_editor.core.template.Template.load") as mock_load:
        mock_load.side_effect = ValueError("Invalid template")
        templates = editor.template_manager.list_templates()
        assert len(templates) == 0  # Should skip invalid templates


def test_template_manager_validation(editor: Editor) -> None:
    """Test template manager validation."""
    # Test with invalid template data
    template_data = {
        "name": "",  # Invalid: empty name
        "category": "general",
        "metadata": {"description": "Test", "tags": [], "format": "markdown"},
        "styles": {},
        "layouts": []
    }

    path = editor.template_dir / "invalid_template.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(template_data, f)

    # Should return None for invalid template
    assert editor.template_manager.get_template("invalid_template") is None


def test_template_creation_and_modification(editor: Editor) -> None:
    """Test template creation and modification."""
    # Create a template
    template = editor.template_manager.create_template(
        name="test_template",
        category="general",
        description="Test template",
        tags=["test"],
        format="markdown"
    )
    assert template is not None
    assert template.name == "test_template"
    assert template.category == "general"
    assert template.metadata["description"] == "Test template"
    assert template.metadata["tags"] == ["test"]
    assert template.metadata["format"] == "markdown"

    # Add styles
    style_data = {
        "font-family": "Arial",
        "font-size": "14pt",
        "color": "#000000"
    }
    template.add_style("fonts", "modern", style_data)
    assert "fonts" in template.styles
    assert "modern" in template.styles["fonts"]
    assert template.styles["fonts"]["modern"] == style_data

    # Add layout
    layout_data = {
        "margin": "2cm",
        "padding": "1cm",
        "line-height": "1.5"
    }
    template.add_layout(layout_data)
    assert layout_data in template.layouts

    # Save and load
    path = editor.template_dir / "test_template.json"
    template.save(path)
    loaded = editor.template_manager.get_template("test_template")
    assert loaded is not None
    assert loaded.name == template.name
    assert loaded.styles == template.styles
    assert loaded.layouts == template.layouts


def test_template_rendering(editor: Editor) -> None:
    """Test template rendering functionality."""
    # Create a template with styles and layout
    template = editor.template_manager.create_template(
        name="test_template",
        category="general",
        description="Test template",
        tags=["test"],
        format="markdown"
    )
    
    # Add some styles
    template.add_style("fonts", "modern", {
        "font-family": "Arial",
        "font-size": "14pt"
    })
    template.add_style("colors", "dark", {
        "color": "#000000",
        "background-color": "#FFFFFF"
    })

    # Add a layout
    template.add_layout({
        "margin": "2cm",
        "padding": "1cm",
        "line-height": "1.5"
    })

    # Test rendering content
    content = "# Test Content\n\nThis is a test."
    rendered = template.render(content)
    
    # Check that styles and layout are applied
    assert "font-family: Arial" in rendered
    assert "font-size: 14pt" in rendered
    assert "margin: 2cm" in rendered
    assert "Test Content" in rendered


def test_template_validation_and_errors(editor: Editor) -> None:
    """Test template validation and error handling."""
    # Test creating template with invalid data
    with pytest.raises(ValueError):
        editor.template_manager.create_template(
            name="",  # Invalid: empty name
            category="general",
            description="Test",
            tags=[],
            format="markdown"
        )

    # Test creating template with invalid format
    with pytest.raises(ValueError):
        editor.template_manager.create_template(
            name="test",
            category="general",
            description="Test",
            tags=[],
            format="invalid"  # Invalid format
        )

    # Test adding invalid style
    template = editor.template_manager.create_template(
        name="test",
        category="general",
        description="Test",
        tags=[],
        format="markdown"
    )
    with pytest.raises(ValueError):
        template.add_style("", "modern", {})  # Invalid: empty category

    # Test adding invalid layout
    with pytest.raises(ValueError):
        template.add_layout(None)  # Invalid: None layout

    # Test rendering with invalid content
    assert template.render(None) == ""  # Should handle None content gracefully

"""Test app core functionality."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.book_editor.app.core.editor import DocumentManager, EditorApp
from src.book_editor.app.core.preview import PreviewManager
from src.book_editor.core.document import Document
from src.book_editor.core.template import Template, TemplateManager


@pytest.fixture
def document_manager(temp_dir: Path) -> DocumentManager:
    """Create a DocumentManager instance for testing."""
    return DocumentManager(str(temp_dir))


@pytest.fixture
def template_manager(temp_dir: Path) -> TemplateManager:
    """Create a TemplateManager instance for testing."""
    return TemplateManager(temp_dir)


@pytest.fixture
def preview_manager() -> PreviewManager:
    """Create a PreviewManager instance for testing."""
    return PreviewManager()


@pytest.fixture
def editor_app(temp_dir: Path) -> EditorApp:
    """Create an EditorApp instance for testing."""
    with patch("src.book_editor.app.core.editor.STORAGE_DIR", temp_dir):
        app = EditorApp()
        return app


def test_editor_app_initialization(editor_app: EditorApp) -> None:
    """Test EditorApp initialization."""
    assert editor_app.document_manager is not None
    assert editor_app.template_manager is not None


def test_document_manager_operations(
    document_manager: DocumentManager,
) -> None:
    """Test DocumentManager operations."""
    # Test document creation
    doc = document_manager.create_document("Test", "Test content")
    assert doc.metadata["title"] == "Test"
    assert doc.content == "Test content"

    # Test document saving
    assert document_manager.save_document(doc)

    # Test document loading
    loaded_doc = document_manager.load_document("Test")
    assert loaded_doc is not None
    assert loaded_doc.metadata["title"] == "Test"
    assert loaded_doc.content == "Test content"

    # Test document deletion
    assert document_manager.delete_document("Test")
    assert document_manager.load_document("Test") is None


def test_template_renderer_operations(
    template_manager: TemplateManager,
) -> None:
    """Test template renderer operations."""
    # Create a test template
    template = Template("default", "general")
    template.metadata["description"] = "Default template"
    template_manager.save_template(template)

    # Test template loading
    loaded_template = template_manager.get_template("default")
    assert loaded_template is not None
    assert loaded_template.name == "default"
    assert loaded_template.metadata["description"] == "Default template"

    # Test template listing
    templates = template_manager.list_templates()
    assert "default" in templates


def test_preview_manager_operations(preview_manager: PreviewManager) -> None:
    """Test preview manager operations."""
    # Create a test document
    doc = Document("Test")
    doc.content = "# Test\nThis is a test"

    # Test preview without template
    preview = preview_manager.get_preview(doc)
    assert preview == "# Test\nThis is a test"

    # Test preview with template
    template = Template("default", "general")
    preview_manager.set_template(template)
    preview = preview_manager.get_preview(doc)
    assert "<h1>Test</h1>" in preview
    assert "<p>This is a test</p>" in preview


def test_editor_app_document_handling(editor_app: EditorApp) -> None:
    """Test EditorApp document handling."""
    # Create and save a test document
    doc = editor_app.new_document("Test")
    assert doc.metadata["title"] == "Test"
    assert editor_app.save_document()

    # Load the document
    loaded_doc = editor_app.load_document("Test")
    assert loaded_doc is not None
    assert loaded_doc.metadata["title"] == "Test"


def test_editor_app_template_handling(editor_app: EditorApp) -> None:
    """Test EditorApp template handling."""
    # Create and save a test template
    template = Template("default", "general")
    editor_app.template_manager.save_template(template)

    # Test template listing
    templates = editor_app.template_manager.list_templates()
    assert "default" in templates


def test_editor_app_error_handling(editor_app: EditorApp) -> None:
    """Test EditorApp error handling."""
    # Test preview without document
    assert editor_app.get_preview() == ""

    # Test saving without document
    assert not editor_app.save_document()

    # Test loading non-existent document
    assert editor_app.load_document("nonexistent") is None

    # Test setting non-existent template
    assert not editor_app.set_template("nonexistent")


def test_document_manager_validation(
    document_manager: DocumentManager,
) -> None:
    """Test DocumentManager validation."""
    # Test creating document with empty title
    doc = document_manager.create_document("")
    assert doc.metadata["title"] == "Untitled"

    # Test saving document with empty content
    assert document_manager.save_document(doc)

    # Test loading non-existent document
    assert document_manager.load_document("nonexistent") is None

    # Test deleting non-existent document
    assert not document_manager.delete_document("nonexistent")


def test_template_renderer_validation(
    template_manager: TemplateManager,
) -> None:
    """Test template renderer validation."""
    # Test loading non-existent template
    assert template_manager.get_template("nonexistent") is None

    # Test saving template with empty name
    template = Template("", "general")
    assert not template_manager.save_template(template)  # Should fail for empty name

    # Test saving template with valid name
    template = Template("test", "general")
    assert template_manager.save_template(template)  # Should succeed

# pylint: disable=redefined-outer-name
"""Test module for app core functionality."""

import tempfile
from unittest.mock import patch

import pytest  # pylint: disable=import-error

from book_editor.core.template import Template
from src.book_editor.app.core.editor import (
    AppEditor,
    DocumentManager,
    PreviewManager,
    TemplateRenderer,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def app_editor(temp_dir):
    """Create an AppEditor instance for testing."""
    with patch("src.book_editor.app.config.settings.TEMPLATE_DIR", temp_dir):
        with patch(
            "src.book_editor.app.config.settings.STORAGE_DIR", temp_dir
        ):
            return AppEditor()


@pytest.fixture
def document_manager(temp_dir):
    """Create a DocumentManager instance for testing."""
    with patch("src.book_editor.app.config.settings.STORAGE_DIR", temp_dir):
        return DocumentManager()


@pytest.fixture
def template_renderer(temp_dir):
    """Create a TemplateRenderer instance for testing."""
    return TemplateRenderer(temp_dir)


@pytest.fixture
def preview_manager():
    """Create a PreviewManager instance for testing."""
    return PreviewManager()


def test_app_editor_initialization(app_editor):
    """Test AppEditor initialization."""
    assert app_editor.document_manager is not None
    assert app_editor.template_renderer is not None
    assert app_editor.preview_manager is not None
    assert app_editor.current_document is None


def test_document_manager_operations(document_manager):
    """Test DocumentManager operations."""
    # Test document creation
    doc = document_manager.create_document("Test", "Test content")
    assert doc.title == "Test"
    assert doc.content == "Test content"

    # Test document saving
    assert document_manager.save_document(doc)
    assert document_manager.get_document(doc.title) == doc

    # Test document listing
    docs = document_manager.list_documents()
    assert len(docs) == 1
    assert docs[0].title == "Test"

    # Test document deletion
    assert document_manager.delete_document(doc.title)
    assert document_manager.get_document(doc.title) is None


def test_template_renderer_operations(template_renderer):
    """Test TemplateRenderer operations."""
    # Create a test template
    template = Template("default", "general")
    template.metadata["description"] = "Default template"
    template_renderer.save_template(template)

    # Test template loading
    loaded_template = template_renderer.load_template("default")
    assert loaded_template is not None
    assert loaded_template.name == "default"
    assert loaded_template.metadata["description"] == "Default template"


def test_preview_manager_operations(preview_manager, temp_dir):
    """Test PreviewManager operations."""
    # Test preview generation
    content = "# Test\nThis is a test"
    with patch("src.book_editor.app.config.settings.TEMPLATE_DIR", temp_dir):
        preview = preview_manager.generate_preview(content)
        assert "<h1>" in preview
        assert "This is a test" in preview

    # Test style application
    styles = {"font-family": "Arial"}
    styled_preview = preview_manager.apply_styles(preview, styles)
    assert "font-family: Arial" in styled_preview
    # Test preview caching
    preview_manager.cache_preview(content, preview)
    assert preview_manager.get_cached_preview(content) == preview


@patch("streamlit.markdown")
def test_app_editor_document_handling(mock_markdown, app_editor):
    """Test AppEditor document handling."""
    # Test document creation
    doc = app_editor.create_document("Test")
    assert doc.title == "Test"
    assert app_editor.current_document == doc

    # Test content update
    app_editor.update_content("Test content")
    assert app_editor.current_document.content == "Test content"

    # Test preview update
    app_editor.update_preview()
    mock_markdown.assert_called_once_with("Test content")

    # Test document saving
    assert app_editor.save_document()
    assert app_editor.document_manager.get_document("Test") == doc


def test_app_editor_template_handling(app_editor):
    """Test AppEditor template handling."""
    # Create and save a test template
    template = Template("default", "general")
    template.styles = {
        "borders": {},
        "colors": {},
        "fonts": {"font-family": "Arial"},
    }
    app_editor.template_renderer.save_template(template)

    # Test template loading
    loaded = app_editor.template_renderer.load_template("default")
    assert loaded is not None
    assert loaded.styles["fonts"]["font-family"] == "Arial"


def test_app_editor_error_handling(app_editor):
    """Test AppEditor error handling."""
    # Test invalid document operations
    with pytest.raises(ValueError):
        app_editor.create_document("")  # Empty title

    with pytest.raises(ValueError):
        app_editor.update_content(None)  # None content

    # Test invalid template operations
    with pytest.raises(ValueError):
        app_editor.select_template("")  # Empty template name

    with pytest.raises(ValueError):
        app_editor.customize_template(None)  # None styles


def test_document_manager_validation(document_manager):
    """Test DocumentManager validation."""
    # Test invalid document creation
    with pytest.raises(ValueError):
        document_manager.create_document("", "")  # Empty title and content

    # Test non-existent document operations
    assert not document_manager.delete_document("nonexistent")
    assert document_manager.get_document("nonexistent") is None

    # Test duplicate document handling
    document_manager.create_document("Test", "Content 1")
    document_manager.create_document("Test", "Content 2")
    assert document_manager.get_document("Test").content == "Content 2"


def test_template_renderer_validation(template_renderer):
    """Test TemplateRenderer validation."""
    # Test invalid template customization
    with pytest.raises(ValueError):
        template_renderer.customize_template("", {})  # Empty template name

    with pytest.raises(ValueError):
        template_renderer.customize_template("default", None)  # None styles


def test_preview_manager_validation(preview_manager):
    """Test PreviewManager validation."""
    # Test invalid preview generation
    with pytest.raises(ValueError):
        preview_manager.generate_preview(None)  # None content

    # Test invalid style application
    with pytest.raises(ValueError):
        preview_manager.apply_styles("", None)  # None styles

    # Test invalid cache operations
    with pytest.raises(ValueError):
        preview_manager.cache_preview("", "")  # Empty content and preview

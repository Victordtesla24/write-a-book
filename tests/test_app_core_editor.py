# pylint: disable=redefined-outer-name
"""Test module for app core editor functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest  # pylint: disable=import-error

from src.book_editor.app.core.editor import (
    AppEditor,
    DocumentManager,
    PreviewManager,
    TemplateRenderer,
)
from src.book_editor.core.template import Template


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_path = Path(tmpdirname)
        temp_path.mkdir(parents=True, exist_ok=True)
        yield temp_path


@pytest.fixture
def template_renderer(temp_dir):
    """Create a template renderer instance for testing."""
    return TemplateRenderer(str(temp_dir))


@pytest.fixture
def preview_manager(template_renderer):
    """Create a PreviewManager instance for testing."""
    return PreviewManager(template_renderer)


@pytest.fixture
def document_manager(temp_dir):
    """Create a DocumentManager instance for testing."""
    with patch("src.book_editor.app.core.editor.STORAGE_DIR", str(temp_dir)):
        return DocumentManager()


@pytest.fixture
def app_editor(temp_dir):
    """Create an AppEditor instance for testing."""
    # Need to patch both the import-time and runtime access to TEMPLATE_DIR
    with patch(
        "src.book_editor.app.core.editor.TEMPLATE_DIR", str(temp_dir)
    ), patch(
        "src.book_editor.app.core.editor.STORAGE_DIR", str(temp_dir)
    ), patch(
        "src.book_editor.app.config.settings.TEMPLATE_DIR", str(temp_dir)
    ), patch(
        "src.book_editor.app.config.settings.STORAGE_DIR", str(temp_dir)
    ):
        return AppEditor()


def test_template_renderer_operations(template_renderer):
    """Test template renderer operations."""
    # Create a test template
    template = Template("default", "general")
    template.metadata["description"] = "Default template"
    template_renderer.save_template(template)

    # Test template loading
    loaded_template = template_renderer.load_template("default")
    assert loaded_template is not None
    assert loaded_template.name == "default"
    assert loaded_template.metadata["description"] == "Default template"


def test_preview_manager_operations(preview_manager):
    """Test preview manager operations."""
    # Test preview generation
    content = "# Test\nThis is a test"
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


def test_app_editor_initialization(app_editor):
    """Test app editor initialization."""
    assert app_editor.document_manager is not None
    assert app_editor.template_renderer is not None
    assert app_editor.preview_manager is not None
    assert app_editor.current_document is None


def test_app_editor_document_operations(app_editor):
    """Test app editor document operations."""
    # Test document creation
    doc = app_editor.create_document("Test")
    assert doc.title == "Test"
    assert app_editor.current_document == doc

    # Test content update
    app_editor.update_content("Test content")
    assert app_editor.current_document.content == "Test content"

    # Test document saving
    assert app_editor.save_document()
    assert app_editor.document_manager.get_document("Test") == doc


def test_app_editor_template_operations(app_editor):
    """Test app editor template operations."""
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


def test_app_editor_validation(app_editor):
    """Test app editor validation."""
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

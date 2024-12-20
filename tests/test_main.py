# pylint: disable=redefined-outer-name
"""Test module for main functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest  # pylint: disable=import-error

from src.book_editor.main import BookEditor, main, render_template_manager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_path = Path(tmpdirname)
        temp_path.mkdir(parents=True, exist_ok=True)
        yield temp_path


@pytest.fixture
def editor_instance(temp_dir):
    """Create a BookEditor instance for testing."""
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
        editor = BookEditor()
        editor.templates_dir = temp_dir
        editor.ensure_directories()
        editor.template_manager = editor.template_manager.__class__(temp_dir)
        return editor


def test_book_editor_initialization(editor_instance):
    """Test BookEditor initialization."""
    assert editor_instance.editor is not None
    assert editor_instance.template_manager is not None
    assert editor_instance.last_save_time > 0
    assert editor_instance.auto_save_interval == 60


@patch("streamlit.session_state")
def test_render_template_manager(mock_session_state):
    """Test template manager rendering."""
    # Mock session state
    mock_session_state.editor = MagicMock()
    mock_session_state.editor.template_manager.get_categories.return_value = [
        "general"
    ]

    # Test rendering
    render_template_manager()
    mock_session_state.editor.template_manager.get_categories.assert_called_once()


@patch("streamlit.session_state")
@patch("streamlit.sidebar")
@patch("streamlit.title")
def test_main(mock_title, mock_sidebar, mock_session_state):
    """Test main function."""
    # Mock session state
    mock_session_state.__contains__.return_value = False
    mock_session_state.editor = MagicMock()
    mock_session_state.editor.template_manager.get_categories.return_value = [
        "general"
    ]
    mock_session_state.editor.template_manager.list_templates.return_value = []
    mock_session_state.get.return_value = (
        ""  # Return empty string for editor_content
    )

    # Mock sidebar context
    mock_sidebar.return_value.__enter__.return_value = MagicMock()

    # Test initialization of editor
    main()
    mock_title.assert_called_once_with("📚 Book Editor")


def test_auto_save(editor_instance):
    """Test auto-save functionality."""
    # Test initial state
    assert not editor_instance.check_auto_save("test content")

    # Test after interval
    editor_instance.last_save_time = 0  # Force auto-save check
    assert not editor_instance.check_auto_save(
        "test content"
    )  # Should still be False as no current document


def test_template_management(editor_instance):
    """Test template management functionality."""
    # Test category management
    name = "test"
    description = "Test category"
    # Ensure the template manager is properly initialized
    editor_instance.template_manager.ensure_storage()
    # Add the category
    result = editor_instance.template_manager.add_category(
        name=name, description=description
    )
    assert result, "Failed to add category"
    categories = editor_instance.template_manager.get_categories()
    assert name in categories, f"Category {name} not found in {categories}"

    # Test duplicate category
    assert not editor_instance.template_manager.add_category(
        name=name, description="Duplicate"
    )


def test_template_search(editor_instance):
    """Test template search functionality."""
    # Create a test template
    template = editor_instance.template_manager.load_template("test")
    if template:
        template.metadata["description"] = "Test template"
        template.metadata["tags"] = ["test", "example"]
        editor_instance.template_manager.save_template(template)

        # Search templates
        results = editor_instance.template_manager.search_templates("test")
        assert len(results) > 0
        assert results[0]["name"] == "test"


def test_template_preview(editor_instance):
    """Test template preview functionality."""
    # Create a test template with styles
    template = editor_instance.template_manager.load_template("test")
    if template:
        template.styles["borders"] = {"border": "1px solid black"}
        template.layouts = [{"margin": "1em"}]
        editor_instance.template_manager.save_template(template)

        # Load and verify template
        loaded = editor_instance.template_manager.load_template("test")
        assert loaded is not None
        assert loaded.styles["borders"]["border"] == "1px solid black"
        assert loaded.layouts[0]["margin"] == "1em"


def test_editor_content_handling(editor_instance):
    """Test editor content handling."""
    # Test content update
    doc = editor_instance.editor.new_document("test")
    doc.update_content("Test content")
    assert doc.content == "Test content"

    # Test content preview
    html = doc.get_html()
    assert "Test content" in html


def test_editor_statistics(editor_instance):
    """Test editor statistics calculation."""
    # Test with empty content
    stats = editor_instance.editor.analyze_text("")
    assert stats["word_count"] == 0
    assert stats["char_count"] == 0

    # Test with actual content
    content = "This is a test.\nIt has multiple lines.\n\nAnd paragraphs."
    stats = editor_instance.editor.analyze_text(content)
    assert stats["word_count"] == 10
    assert stats["line_count"] == 4
    assert stats["paragraph_count"] == 2


def test_document_history(editor_instance):
    """Test document revision history."""
    # Create and update document
    doc = editor_instance.editor.new_document("test")
    doc.update_content("Version 1")
    doc.update_content("Version 2")

    # Check history
    history = doc.get_revision_history()
    assert len(history) == 2
    assert history[0]["content"] == ""  # Initial content
    assert history[1]["content"] == "Version 1"

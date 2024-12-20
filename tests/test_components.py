# pylint: disable=redefined-outer-name
"""Test module for editor components."""

from src.components.text_editor import EditorComponent


def test_editor_component_initialization() -> None:
    """Test editor component initialization."""
    editor = EditorComponent()
    assert editor.content == ""
    assert editor.cursor_position == 0


def test_editor_content_update() -> None:
    """Test content update functionality."""
    editor = EditorComponent()
    test_content = "Hello, World!"
    editor.set_content(test_content)
    assert editor.content == test_content
    assert editor.get_content() == test_content


def test_cursor_movement() -> None:
    """Test cursor movement functionality."""
    editor = EditorComponent()
    editor.set_content("Test content")
    editor.move_cursor(5)
    assert editor.cursor_position == 5

    # Test bounds
    editor.move_cursor(-10)  # Should clamp to 0
    assert editor.cursor_position == 0

    editor.move_cursor(100)  # Should clamp to content length
    assert editor.cursor_position == len(editor.content)


def test_text_selection() -> None:
    """Test text selection functionality."""
    editor = EditorComponent()
    editor.set_content("Select this text")
    editor.select_text(0, 6)
    assert editor.get_selected_text() == "Select"


def test_undo_redo() -> None:
    """Test undo/redo functionality."""
    editor = EditorComponent()

    # Make some changes
    editor.set_content("First")
    editor.set_content("Second")
    editor.set_content("Third")

    # Test undo
    editor.undo()
    assert editor.content == "Second"
    editor.undo()
    assert editor.content == "First"

    # Test redo
    editor.redo()
    assert editor.content == "Second"

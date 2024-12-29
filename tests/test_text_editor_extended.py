# pylint: disable=redefined-outer-name
"""Extended test module for text editor component."""

import pytest  # pylint: disable=import-error

from src.components.text_editor import EditorComponent


@pytest.fixture
def editor():
    """Create an editor component for testing."""
    return EditorComponent()


def test_editor_initialization(editor):
    """Test editor component initialization."""
    assert editor.content == ""
    assert editor.cursor_position == 0
    assert editor.selection_start is None
    assert editor.selection_end is None
    # Access to protected members is necessary for testing internal state
    assert len(editor._undo_stack) == 0  # pylint: disable=protected-access
    assert len(editor._redo_stack) == 0  # pylint: disable=protected-access


def test_content_management(editor):
    """Test content management functionality."""
    # Set initial content
    editor.set_content("Initial content")
    assert editor.get_content() == "Initial content"
    assert editor.cursor_position == len("Initial content")

    # Update content
    editor.set_content("Updated content")
    assert editor.get_content() == "Updated content"
    # Access to protected member is necessary for testing undo stack state
    assert len(editor._undo_stack) == 2  # pylint: disable=protected-access


def test_cursor_movement_bounds(editor):
    """Test cursor movement with boundary conditions."""
    editor.set_content("Test content")

    # Move cursor to negative position
    editor.move_cursor(-5)
    assert editor.cursor_position == 0

    # Move cursor beyond content length
    editor.move_cursor(100)
    assert editor.cursor_position == len(editor.content)

    # Move cursor to middle
    editor.move_cursor(5)
    assert editor.cursor_position == 5


def test_text_selection_operations(editor):
    """Test text selection operations."""
    editor.set_content("Select this text")

    # Normal selection
    editor.select_text(0, 6)
    assert editor.get_selected_text() == "Select"
    assert editor.cursor_position == 6

    # Reverse selection
    editor.select_text(6, 0)
    assert editor.get_selected_text() == "Select"

    # Selection beyond bounds
    editor.select_text(-5, 100)
    assert editor.get_selected_text() == editor.content

    # Clear selection
    editor.clear_selection()
    assert editor.selection_start is None
    assert editor.selection_end is None


def test_undo_redo_operations(editor):
    """Test undo/redo stack operations."""
    # Initial state
    assert editor.get_content() == ""

    # First edit
    editor.set_content("First")
    assert editor.get_content() == "First"

    # Second edit
    editor.set_content("Second")
    assert editor.get_content() == "Second"

    # Undo to first edit
    editor.undo()
    assert editor.get_content() == "First"

    # Undo to initial state
    editor.undo()
    assert editor.get_content() == ""

    # Redo first edit
    editor.redo()
    assert editor.get_content() == "First"


def test_empty_operations(editor):
    """Test operations with empty content."""
    # Empty selection
    editor.select_text(0, 0)
    assert editor.get_selected_text() == ""

    # Undo with empty stack
    editor.undo()
    assert editor.content == ""

    # Redo with empty stack
    editor.redo()
    assert editor.content == ""


def test_cursor_selection_interaction(editor):
    """Test interaction between cursor and selection."""
    editor.set_content("Test content")

    # Selection should update cursor
    editor.select_text(0, 4)
    assert editor.cursor_position == 4

    # Moving cursor should clear selection
    editor.move_cursor(2)
    assert editor.selection_start is None
    assert editor.selection_end is None


def test_content_state_management(editor):
    """Test content state management."""
    # Initial state
    # Access to protected members is necessary for testing stack states
    assert len(editor._undo_stack) == 0  # pylint: disable=protected-access

    # Single update
    editor.set_content("First")
    assert len(editor._undo_stack) == 1  # pylint: disable=protected-access
    assert len(editor._redo_stack) == 0  # pylint: disable=protected-access

    # Multiple updates
    editor.set_content("Second")
    editor.set_content("Third")
    assert len(editor._undo_stack) == 3  # pylint: disable=protected-access

    # Undo and new update
    editor.undo()
    editor.set_content("New content")
    assert len(editor._redo_stack) == 0  # pylint: disable=protected-access


def test_selection_edge_cases(editor):
    """Test selection edge cases."""
    editor.set_content("Test content")

    # Zero-length selection
    editor.select_text(5, 5)
    assert editor.get_selected_text() == ""

    # Selection with swapped start/end
    editor.select_text(6, 4)
    assert len(editor.get_selected_text()) == 2

    # Selection beyond content
    editor.select_text(-10, 100)
    assert editor.get_selected_text() == editor.content

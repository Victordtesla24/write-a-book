# pylint: disable=redefined-outer-name
"""Test module for editor functionality."""

import pytest  # pylint: disable=import-error

from src.components.editor import Editor
from src.models.book import Book


@pytest.fixture
def editor() -> Editor:
    """Create an editor instance for testing."""
    return Editor()


@pytest.fixture
def sample_book() -> Book:
    """Create a sample book for testing."""
    book = Book(title="Test Book", author="Test Author")
    book.add_chapter("Chapter 1", "Content 1")
    book.add_chapter("Chapter 2", "Content 2")
    return book


def test_editor_initialization(editor: Editor) -> None:
    """Test editor initialization."""
    assert editor.current_book is None
    assert editor.current_chapter_index == 0
    assert editor.undo_stack == []
    assert editor.redo_stack == []


def test_book_loading(editor: Editor, sample_book: Book) -> None:
    """Test book loading functionality."""
    editor.load_book(sample_book)
    assert editor.current_book == sample_book
    assert editor.current_chapter_index == 0


def test_chapter_navigation(editor: Editor, sample_book: Book) -> None:
    """Test chapter navigation."""
    editor.load_book(sample_book)

    # Test next chapter
    assert editor.current_chapter_index == 0
    editor.next_chapter()
    assert editor.current_chapter_index == 1

    # Test previous chapter
    editor.previous_chapter()
    assert editor.current_chapter_index == 0

    # Test bounds
    editor.previous_chapter()  # Should not go below 0
    assert editor.current_chapter_index == 0

    editor.next_chapter()
    editor.next_chapter()  # Should not exceed last chapter
    assert editor.current_chapter_index == 1


def test_content_editing(editor: Editor, sample_book: Book) -> None:
    """Test content editing functionality."""
    editor.load_book(sample_book)

    # Test update content
    new_content = "Updated content"
    editor.update_content(new_content)
    assert editor.current_book.chapters[0].content == new_content

    # Test undo
    editor.undo()
    assert editor.current_book.chapters[0].content == "Content 1"

    # Test redo
    editor.redo()
    assert editor.current_book.chapters[0].content == new_content


def test_chapter_management(editor: Editor, sample_book: Book) -> None:
    """Test chapter management functionality."""
    editor.load_book(sample_book)

    # Test add chapter
    editor.add_chapter("New Chapter", "New Content")
    assert len(editor.current_book.chapters) == 3
    assert editor.current_book.chapters[2].title == "New Chapter"

    # Test delete chapter
    editor.delete_chapter(1)
    assert len(editor.current_book.chapters) == 2
    assert editor.current_book.chapters[1].title == "New Chapter"

    # Test move chapter
    editor.move_chapter(1, 0)
    assert editor.current_book.chapters[0].title == "New Chapter"


def test_error_handling(editor: Editor) -> None:
    """Test error handling in editor operations."""
    # Test operations without loaded book
    with pytest.raises(ValueError):
        editor.update_content("New content")

    with pytest.raises(ValueError):
        editor.next_chapter()

    with pytest.raises(ValueError):
        editor.previous_chapter()

    with pytest.raises(ValueError):
        editor.add_chapter("Title", "Content")

    with pytest.raises(ValueError):
        editor.delete_chapter(0)

    with pytest.raises(ValueError):
        editor.move_chapter(0, 1)


def test_undo_redo_stack(editor: Editor, sample_book: Book) -> None:
    """Test undo/redo stack functionality."""
    editor.load_book(sample_book)

    # Test multiple edits
    editor.update_content("Edit 1")
    editor.update_content("Edit 2")
    editor.update_content("Edit 3")

    # Test undo stack
    editor.undo()
    assert editor.current_book.chapters[0].content == "Edit 2"
    editor.undo()
    assert editor.current_book.chapters[0].content == "Edit 1"

    # Test redo stack
    editor.redo()
    assert editor.current_book.chapters[0].content == "Edit 2"

    # Test stack clearing on new edit
    editor.update_content("New edit")
    assert len(editor.redo_stack) == 0


def test_chapter_validation(editor: Editor, sample_book: Book) -> None:
    """Test chapter validation functionality."""
    editor.load_book(sample_book)

    # Test empty title
    with pytest.raises(ValueError):
        editor.add_chapter("", "Content")

    # Test None content
    with pytest.raises(ValueError):
        editor.add_chapter("Title", None)

    # Test invalid chapter index
    with pytest.raises(IndexError):
        editor.delete_chapter(99)

    # Test invalid move indices
    with pytest.raises(IndexError):
        editor.move_chapter(0, 99)
    with pytest.raises(IndexError):
        editor.move_chapter(99, 0)


def test_empty_undo_redo(editor: Editor, sample_book: Book) -> None:
    """Test undo/redo operations with empty stacks."""
    editor.load_book(sample_book)

    # Test undo with empty stack
    editor.undo()  # Should not raise error
    assert editor.current_book.chapters[0].content == "Content 1"

    # Test redo with empty stack
    editor.redo()  # Should not raise error
    assert editor.current_book.chapters[0].content == "Content 1"


def test_chapter_index_adjustment(editor: Editor, sample_book: Book) -> None:
    """Test chapter index adjustment after deletion."""
    editor.load_book(sample_book)

    # Move to last chapter
    editor.next_chapter()
    assert editor.current_chapter_index == 1

    # Delete current chapter
    editor.delete_chapter(1)
    assert editor.current_chapter_index == 0  # Should adjust to valid index


def test_multiple_chapter_operations(
    editor: Editor, sample_book: Book
) -> None:
    """Test multiple chapter operations in sequence."""
    editor.load_book(sample_book)

    # Add multiple chapters
    editor.add_chapter("Chapter 3", "Content 3")
    editor.add_chapter("Chapter 4", "Content 4")
    assert len(editor.current_book.chapters) == 4

    # Delete multiple chapters
    editor.delete_chapter(0)
    editor.delete_chapter(0)
    assert len(editor.current_book.chapters) == 2
    assert editor.current_book.chapters[0].title == "Chapter 3"

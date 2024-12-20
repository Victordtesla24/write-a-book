"""Editor component for managing book content."""

from typing import Any, Dict, List, Optional

from src.models.book import Book


class Editor:
    """Editor class for managing book content and operations."""

    def __init__(self) -> None:
        """Initialize the editor."""
        self.current_book: Optional[Book] = None
        self.current_chapter_index: int = 0
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []

    def load_book(self, book: Book) -> None:
        """Load a book into the editor.

        Args:
            book: The book to load
        """
        self.current_book = book
        self.current_chapter_index = 0
        self.undo_stack.clear()
        self.redo_stack.clear()

    def next_chapter(self) -> None:
        """Move to the next chapter."""
        if not self.current_book:
            raise ValueError("No book loaded")

        if self.current_chapter_index < len(self.current_book.chapters) - 1:
            self.current_chapter_index += 1

    def previous_chapter(self) -> None:
        """Move to the previous chapter."""
        if not self.current_book:
            raise ValueError("No book loaded")

        if self.current_chapter_index > 0:
            self.current_chapter_index -= 1

    def update_content(self, new_content: str) -> None:
        """Update the content of the current chapter.

        Args:
            new_content: The new content to set
        """
        if not self.current_book:
            raise ValueError("No book loaded")

        chapter = self.current_book.chapters[self.current_chapter_index]
        old_content = chapter.content
        self.undo_stack.append(
            {
                "chapter_index": self.current_chapter_index,
                "content": old_content,
            }
        )
        self.redo_stack.clear()
        chapter.content = new_content

    def add_chapter(self, title: str, content: str) -> None:
        """Add a new chapter to the book.

        Args:
            title: The chapter title
            content: The chapter content
        """
        if not self.current_book:
            raise ValueError("No book loaded")
        if not title:
            raise ValueError("Chapter title cannot be empty")
        if content is None:
            raise ValueError("Chapter content cannot be None")

        self.current_book.add_chapter(title, content)

    def delete_chapter(self, index: int) -> None:
        """Delete a chapter from the book.

        Args:
            index: The index of the chapter to delete
        """
        if not self.current_book:
            raise ValueError("No book loaded")
        if index < 0 or index >= len(self.current_book.chapters):
            raise IndexError("Invalid chapter index")

        self.current_book.delete_chapter(index)
        if self.current_chapter_index >= len(self.current_book.chapters):
            self.current_chapter_index = len(self.current_book.chapters) - 1

    def move_chapter(self, from_index: int, to_index: int) -> None:
        """Move a chapter from one position to another.

        Args:
            from_index: The current index of the chapter
            to_index: The target index for the chapter
        """
        if not self.current_book:
            raise ValueError("No book loaded")
        if (
            from_index < 0
            or from_index >= len(self.current_book.chapters)
            or to_index < 0
            or to_index >= len(self.current_book.chapters)
        ):
            raise IndexError("Invalid chapter index")

        chapter = self.current_book.chapters.pop(from_index)
        self.current_book.chapters.insert(to_index, chapter)

    def undo(self) -> None:
        """Undo the last content change."""
        if not self.current_book or not self.undo_stack:
            return

        current_state = self.undo_stack.pop()
        chapter_index = current_state["chapter_index"]
        chapter = self.current_book.chapters[chapter_index]
        current_content = chapter.content

        self.redo_stack.append(
            {"chapter_index": chapter_index, "content": current_content}
        )
        chapter.content = current_state["content"]

    def redo(self) -> None:
        """Redo the last undone change."""
        if not self.current_book or not self.redo_stack:
            return

        next_state = self.redo_stack.pop()
        chapter_index = next_state["chapter_index"]
        chapter = self.current_book.chapters[chapter_index]
        current_content = chapter.content

        self.undo_stack.append(
            {"chapter_index": chapter_index, "content": current_content}
        )
        chapter.content = next_state["content"]

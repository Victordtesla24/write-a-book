# pylint: disable=redefined-outer-name
"""Test module for book functionality."""

from src.models.book import Book


def test_book_creation() -> None:
    """Test book model creation and basic properties."""
    book = Book("Test Book", "John Doe")
    assert book.title == "Test Book"
    assert book.author == "John Doe"
    assert len(book.chapters) == 0
    assert not book.metadata


def test_chapter_management() -> None:
    """Test chapter creation and management."""
    book = Book("Test Book", "John Doe")

    # Add chapters
    chapter1 = book.add_chapter("Chapter 1", "Introduction")
    book.add_chapter("Chapter 2", "Development")

    assert len(book.chapters) == 2
    assert book.chapters[0].title == "Chapter 1"
    assert book.chapters[1].title == "Chapter 2"

    # Remove chapter
    book.remove_chapter(chapter1)
    assert len(book.chapters) == 1
    assert book.chapters[0].title == "Chapter 2"

    # Try to remove non-existent chapter
    non_existent = book.add_chapter("Test")
    book.remove_chapter(non_existent)
    book.remove_chapter(non_existent)  # Should not raise error


def test_section_management() -> None:
    """Test section management within chapters."""
    book = Book("Test Book", "John Doe")
    chapter = book.add_chapter("Chapter 1", "Test Chapter")

    # Add sections
    section1 = chapter.add_section("Section 1", "First section content")
    chapter.add_section("Section 2", "Second section content")

    assert len(chapter.sections) == 2
    assert chapter.sections[0].title == "Section 1"
    assert chapter.sections[1].content == "Second section content"

    # Remove section
    chapter.remove_section(section1)
    assert len(chapter.sections) == 1
    assert chapter.sections[0].title == "Section 2"

    # Try to remove non-existent section
    non_existent = chapter.add_section("Test")
    chapter.remove_section(non_existent)
    chapter.remove_section(non_existent)  # Should not raise error


def test_metadata_management() -> None:
    """Test metadata management for book and chapters."""
    book = Book("Test Book", "John Doe")

    # Book metadata
    book.set_metadata("genre", "Fiction")
    book.set_metadata("year", 2024)

    assert book.metadata["genre"] == "Fiction"
    assert book.metadata["year"] == 2024

    # Chapter metadata
    chapter = book.add_chapter("Chapter 1")
    chapter.set_metadata("status", "draft")
    chapter.set_metadata("word_count", 1000)

    assert chapter.metadata["status"] == "draft"
    assert chapter.metadata["word_count"] == 1000

    # Section metadata
    section = chapter.add_section("Section 1")
    section.set_metadata("type", "introduction")
    assert section.metadata["type"] == "introduction"


def test_content_operations() -> None:
    """Test content manipulation operations."""
    book = Book("Test Book", "John Doe")
    chapter = book.add_chapter("Chapter 1")
    section = chapter.add_section("Section 1", "Initial content")

    # Update content
    section.update_content("Updated content")
    assert section.content == "Updated content"

    # Append content
    section.append_content(" More content")
    assert section.content == "Updated content More content"

    # Clear content
    section.clear_content()
    assert section.content == ""


def test_chapter_operations() -> None:
    """Test chapter operations."""
    book = Book("Test Book", "John Doe")

    # Test invalid chapter index
    book.delete_chapter(-1)  # Should not raise error
    book.delete_chapter(0)  # Should not raise error
    book.update_chapter(-1, "Title", "Content")  # Should not raise error
    book.update_chapter(0, "Title", "Content")  # Should not raise error

    # Add and update chapter
    book.add_chapter("Chapter 1")
    book.update_chapter(0, "Updated Title", "Updated Content")
    assert book.chapters[0].title == "Updated Title"
    assert book.chapters[0].content == "Updated Content"

    # Delete chapter
    book.delete_chapter(0)
    assert len(book.chapters) == 0

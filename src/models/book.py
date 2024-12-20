"""Book model module for managing book structure and content."""

from typing import Any, Dict, List


class Section:
    """Represents a section within a chapter."""

    def __init__(self, title: str, content: str = "") -> None:
        self.title = title
        self.content = content
        self.metadata: Dict[str, Any] = {}

    def update_content(self, content: str) -> None:
        """Update section content."""
        self.content = content

    def append_content(self, content: str) -> None:
        """Append content to existing section content."""
        self.content += content

    def clear_content(self) -> None:
        """Clear section content."""
        self.content = ""

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary for serialization."""
        return {
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
        }


class Chapter:
    """Represents a chapter in the book."""

    def __init__(self, title: str, content: str = "") -> None:
        self.title = title
        self.content = content
        self.sections: List[Section] = []
        self.metadata: Dict[str, Any] = {}

    def add_section(self, title: str, content: str = "") -> Section:
        """Add a new section to the chapter."""
        section = Section(title, content)
        self.sections.append(section)
        return section

    def remove_section(self, section: Section) -> None:
        """Remove a section from the chapter."""
        if section in self.sections:
            self.sections.remove(section)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert chapter to dictionary for serialization."""
        return {
            "title": self.title,
            "content": self.content,
            "sections": [section.to_dict() for section in self.sections],
            "metadata": self.metadata,
        }


class Book:
    """Represents a book with chapters and metadata."""

    def __init__(self, title: str, author: str) -> None:
        self.title = title
        self.author = author
        self.chapters: List[Chapter] = []
        self.metadata: Dict[str, Any] = {}
        self.description = ""

    def add_chapter(self, title: str, content: str = "") -> Chapter:
        """Add a new chapter to the book."""
        chapter = Chapter(title, content)
        self.chapters.append(chapter)
        return chapter

    def remove_chapter(self, chapter: Chapter) -> None:
        """Remove a chapter from the book."""
        if chapter in self.chapters:
            self.chapters.remove(chapter)

    def delete_chapter(self, index: int) -> None:
        """Delete a chapter by index."""
        if 0 <= index < len(self.chapters):
            del self.chapters[index]

    def update_chapter(self, index: int, title: str, content: str) -> None:
        """Update chapter title and content."""
        if 0 <= index < len(self.chapters):
            chapter = self.chapters[index]
            chapter.title = title
            chapter.content = content

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert book to dictionary for serialization."""
        return {
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "chapters": [chapter.to_dict() for chapter in self.chapters],
            "metadata": self.metadata,
        }

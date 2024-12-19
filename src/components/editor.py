"""Book editor component for the Streamlit application."""

import streamlit as st

from src.data.storage import BookStorage
from src.models.book import Book


def render_chapter_editor(book: Book, chapter_index: int) -> None:
    """Render editor for a specific chapter."""
    chapter = book.chapters[chapter_index]

    # Chapter title input
    new_title = st.text_input(
        "Chapter Title",
        value=chapter.title,
        key=f"chapter_title_{chapter_index}",
    )

    # Chapter content editor
    new_content = st.text_area(
        "Chapter Content",
        value=chapter.content,
        height=400,
        key=f"chapter_content_{chapter_index}",
    )

    # Update chapter if content changed
    if new_title != chapter.title or new_content != chapter.content:
        book.update_chapter(chapter_index, new_title, new_content)


def render_book_editor(book: Book, storage: BookStorage) -> None:
    """Render the main book editor interface."""
    st.title(book.title)
    st.write(f"By {book.author}")

    # Book description
    new_description = st.text_area(
        "Book Description", value=book.description, height=100
    )
    if new_description != book.description:
        book.description = new_description
        storage.save_book(book)

    # Chapter management
    st.markdown("## Chapters")

    # Add new chapter button
    if st.button("Add Chapter"):
        book.add_chapter(f"Chapter {len(book.chapters) + 1}")
        storage.save_book(book)
        st.experimental_rerun()

    # Chapter tabs
    if book.chapters:
        chapter_tabs = st.tabs(
            [
                f"Chapter {i + 1}: {ch.title}"
                for i, ch in enumerate(book.chapters)
            ]
        )

        # Render editor for each chapter
        for i, tab in enumerate(chapter_tabs):
            with tab:
                render_chapter_editor(book, i)

                # Delete chapter button
                if st.button(f"Delete Chapter {i + 1}"):
                    if st.warning(
                        "Are you sure you want to delete this chapter?"
                    ):
                        book.delete_chapter(i)
                        storage.save_book(book)
                        st.experimental_rerun()

    # Save changes button
    if st.button("Save Changes"):
        storage.save_book(book)
        st.success("Changes saved successfully!")

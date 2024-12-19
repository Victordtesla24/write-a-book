"""Main Streamlit application for the book editor."""

import streamlit as st

from src.components.editor import render_book_editor
from src.data.storage import BookStorage
from src.models.book import Book


def create_new_book(storage: BookStorage) -> None:
    """Create a new book from user input."""
    st.sidebar.markdown("---")
    with st.sidebar.form("new_book_form"):
        st.write("Create New Book")
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        description = st.text_area("Description")

        if st.form_submit_button("Create Book"):
            if title and author:
                book = Book(
                    title=title, author=author, description=description
                )
                storage.save_book(book)
                st.success(f"Created new book: {title}")
                st.experimental_rerun()
            else:
                st.error("Title and author are required!")


def handle_existing_book(storage: BookStorage, selected_book: str) -> None:
    """Handle operations for an existing book."""
    book = storage.load_book(selected_book)
    if not book:
        st.error("Failed to load book!")
        return

    # Delete book button
    if st.sidebar.button("Delete Book"):
        if st.sidebar.warning("Are you sure you want to delete this book?"):
            if storage.delete_book(selected_book):
                st.sidebar.success("Book deleted!")
                st.experimental_rerun()
            else:
                st.sidebar.error("Failed to delete book!")

    # Render book editor
    render_book_editor(book, storage)


def main() -> None:
    """Main application entry point."""
    # Initialize storage
    storage = BookStorage()

    # Page config
    st.set_page_config(page_title="Book Editor", page_icon="📚", layout="wide")

    # Sidebar
    st.sidebar.title("Book Editor")

    # List existing books or create new one
    book_files = storage.list_books()
    if book_files:
        selected_book = st.sidebar.selectbox(
            "Select a book", ["Create New Book"] + book_files
        )
    else:
        selected_book = "Create New Book"

    # Handle book selection
    if selected_book == "Create New Book":
        create_new_book(storage)
    else:
        handle_existing_book(storage, selected_book)


if __name__ == "__main__":
    main()

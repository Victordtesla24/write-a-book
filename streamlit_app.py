"""Main Streamlit application entry point."""

from typing import Optional

import streamlit as st

from src.book_editor.main import render_book_editor
from src.data.storage import Storage


def main() -> Optional[str]:
    """Main application entry point.

    Returns:
        Optional[str]: Status message if any
    """
    st.set_page_config(page_title="Book Editor", page_icon="📚", layout="wide")

    storage = Storage()
    return render_book_editor(storage)


if __name__ == "__main__":
    main()

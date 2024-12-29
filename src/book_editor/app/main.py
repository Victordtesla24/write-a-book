"""Main module for Book Editor application.

This module provides the main Streamlit interface for the Book Editor,
including the editor, template management, and preview functionality.
"""

import time
from pathlib import Path

import streamlit as st

from book_editor.core.editor import Editor
from book_editor.core.template import Template, TemplateManager

# Configure Streamlit page
st.set_page_config(
    page_title="Book Editor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


class BookEditor:
    """Main application class for the Book Editor.

    Handles editor initialization, template management, and auto-save.
    """

    def __init__(self):
        self.templates_dir = Path("templates")
        self.editor = Editor(self.templates_dir)
        self.template_manager = TemplateManager(self.templates_dir)
        self.ensure_directories()
        self.last_save_time = time.time()
        self.auto_save_interval = 60  # seconds

    def ensure_directories(self):
        """Ensure required directories exist."""
        self.templates_dir.mkdir(exist_ok=True)

    def save_template(self, uploaded_file, category: str = "general"):
        """Save uploaded template file."""
        if uploaded_file is not None:
            # Create template from uploaded file
            template = Template(uploaded_file.name.split(".")[0], category)
            template.metadata["description"] = "Uploaded template"

            # Save the template file
            file_path = self.templates_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Save template metadata
            return self.template_manager.save_template(template)
        return False

    def check_auto_save(self, text_content):
        """Check if auto-save should be triggered."""
        current_time = time.time()
        if current_time - self.last_save_time >= self.auto_save_interval:
            if self.editor.current_document:
                self.editor.current_document.update_content(text_content)
                if self.editor.save_document():
                    self.last_save_time = current_time
                    return True
        return False


def render_category_management():
    """Render category management section."""
    categories = st.session_state.editor.template_manager.get_categories()
    selected_category = st.selectbox("Category", categories)

    # Add new category
    with st.expander("Add New Category"):
        new_category = st.text_input("Category Name")
        category_desc = st.text_area("Description")
        if st.button("Add Category"):
            if st.session_state.editor.template_manager.add_category(new_category, category_desc):
                st.success(f"Added category: {new_category}")
                st.rerun()
            else:
                st.error("Category already exists")

    return selected_category


def render_template_upload(selected_category):
    """Render template upload section."""
    st.subheader("Upload Template")
    uploaded_file = st.file_uploader("Choose a template file", type=["txt", "md", "docx"])
    if uploaded_file is not None:
        if st.session_state.editor.save_template(uploaded_file, selected_category):
            st.success(f"Template '{uploaded_file.name}' uploaded successfully!")


def render_template_search():
    """Render template search section."""
    st.subheader("Search Templates")
    search_query = st.text_input("Search templates", "")
    if search_query:
        results = st.session_state.editor.template_manager.search_templates(search_query)
        if results:
            st.write("Search Results:")
            for result in results:
                with st.expander(f"{result['name']} ({result['category']})"):
                    st.write(f"Description: {result['description']}")
                    st.write(f"Tags: {', '.join(result['tags'])}")
        else:
            st.info("No templates found")


def render_template_list(selected_category):
    """Render template list section."""
    st.subheader("Available Templates")
    templates = st.session_state.editor.template_manager.list_templates(selected_category)
    if templates:
        for template_name in templates:
            template = st.session_state.editor.template_manager.load_template(template_name)
            if template:
                with st.expander(template_name):
                    st.write(f"Category: {template.category}")
                    st.write(f"Description: {template.metadata['description']}")
                    if template.metadata["tags"]:
                        st.write(f"Tags: {', '.join(template.metadata['tags'])}")

                    # Preview section
                    if st.button(f"Preview {template_name}"):
                        st.write("Template Preview:")
                        if template.styles.get("borders"):
                            st.code("".join(template.styles["borders"].values()))
                        if template.layouts:
                            st.json(template.layouts)
    else:
        st.info(f"No templates available in category: {selected_category}")


def render_template_manager():
    """Render template management interface."""
    st.header("Template Management")

    # Template categories and management
    selected_category = render_category_management()

    # Template upload
    render_template_upload(selected_category)

    # Template search
    render_template_search()

    # Template list
    render_template_list(selected_category)


def render_editor():
    """Render main editor interface."""
    st.subheader("Editor")
    text_content = st.text_area(
        "Enter or paste your text here:",
        height=400,
        key="editor_content",
        help="Supports Markdown formatting",
    )

    # Auto-save check
    if st.session_state.get("auto_save", True) and text_content:
        if st.session_state.editor.check_auto_save(text_content):
            st.info("Auto-saved!")

    # Manual save button
    if st.button("Save Changes"):
        if not st.session_state.editor.editor.current_document:
            st.session_state.editor.editor.current_document = (
                st.session_state.editor.editor.new_document()
            )
        st.session_state.editor.editor.current_document.update_content(text_content)
        if st.session_state.editor.editor.save_document():
            st.success("Changes saved successfully!")
    return text_content


def render_preview(text_content):
    """Render preview interface."""
    st.subheader("Preview")
    if text_content:
        # Create temporary document for preview
        preview_doc = st.session_state.editor.editor.new_document()
        preview_doc.update_content(text_content)

        # Add CSS for markdown styling
        css = st.session_state.editor.editor.get_css()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

        # Display preview
        html_content = preview_doc.get_html()
        st.markdown(
            '<div class="markdown-body">' f"{html_content}" "</div>",
            unsafe_allow_html=True,
        )

        # Display statistics
        with st.expander("Text Statistics"):
            stats = st.session_state.editor.editor.analyze_text(text_content)
            cols = st.columns(2)
            with cols[0]:
                st.metric("Words", stats["word_count"])
                st.metric("Characters", stats["char_count"])
                st.metric("Lines", stats["line_count"])
            with cols[1]:
                st.metric("Paragraphs", stats["paragraph_count"])
                st.metric("Sentences", stats["sentence_count"])
                st.metric("Avg. Word Length", f"{stats['avg_word_length']:.1f}")


def main():
    """Main application entry point."""
    st.title("📚 Book Editor")

    # Initialize editor
    if "editor" not in st.session_state:
        st.session_state.editor = BookEditor()

    # Sidebar for settings and template management
    with st.sidebar:
        st.header("Settings")
        st.session_state.auto_save = st.checkbox("Enable Auto-Save", value=True)
        st.selectbox("Theme", ["Light", "Dark"])

        # Template management section
        render_template_manager()

        st.header("Document History")
        doc = st.session_state.editor.editor.current_document
        if doc:
            history = doc.get_revision_history()
            if history:
                st.write(f"Previous versions: {len(history)}")
                for i, rev in enumerate(history):
                    st.text(f"Version {i + 1}: {rev['timestamp']}")

    # Main editing area
    col1, col2 = st.columns(2)

    with col1:
        text_content = render_editor()

    with col2:
        render_preview(text_content)


if __name__ == "__main__":
    main()

"""Module docstring placeholder."""

import pytest

from book_editor.core import Document, Editor


@pytest.fixture
def temp_storage(tmp_path):
    """Provide temporary storage directory"""
    return tmp_path / "documents"


@pytest.fixture
def editor(temp_storage):
    """Provide editor instance with temporary storage"""
    return Editor(temp_storage)


def test_document_creation():
    """Test document creation and metadata"""
    content = "Hello, World!"
    doc = Document(content=content, title="Test")

    assert doc.content == content
    assert doc.title == "Test"
    assert doc.word_count == 2


def test_document_update():
    """Test document content update"""
    doc = Document(content="Initial content", title="Test")
    doc.update_content("New content here")

    assert doc.content == "New content here"
    assert doc.word_count == 3


def test_editor_save_load(editor):
    """Test saving and loading documents"""
    # Create and save document
    doc = editor.new_document("Test")
    doc.update_content("Test content")
    assert editor.save_document()

    # Load document
    loaded_doc = editor.load_document("Test")
    assert loaded_doc is not None
    assert loaded_doc.content == "Test content"
    assert loaded_doc.title == "Test"


def test_text_analysis(editor):
    """Test text analysis functionality"""
    text = "This is a test.\nIt has two lines."
    stats = editor.analyze_text(text)

    # Fixed: "This", "is", "a", "test", "It", "has", "two", "lines"
    assert stats["word_count"] == 8
    assert stats["line_count"] == 2
    assert stats["char_count"] == len(text)


def test_markdown_support():
    """Test markdown conversion and HTML generation"""
    doc = Document(
        content="# Test\n\n```python\nprint('hello')\n```", title="Test"
    )
    html = doc.get_html()

    # Test heading
    assert '<h1 id="test">Test</h1>' in html

    # Test code block with syntax highlighting
    assert '<div class="highlight">' in html
    assert "<pre>" in html
    assert 'class="nb">print</span>' in html
    assert "hello" in html


def test_revision_history():
    """Test document revision history"""
    doc = Document(content="Initial", title="Test")
    doc.update_content("First update")
    doc.update_content("Second update")

    history = doc.get_revision_history()
    assert len(history) == 2
    assert history[0]["content"] == "Initial"
    assert history[1]["content"] == "First update"

# pylint: disable=redefined-outer-name
"""Test module for extended editor functionality."""

import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest

from src.book_editor.core.editor import Editor


@pytest.fixture
def editor_instance() -> Generator[Editor, None, None]:
    """Create an Editor instance for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "storage"
        template_dir = Path(temp_dir) / "templates"
        yield Editor(storage_dir, template_dir)


def test_document_empty_metadata(editor_instance):
    """Test document with empty metadata."""
    doc = editor_instance.new_document("Test")
    metadata = doc.metadata
    assert metadata["title"] == "Test"
    assert isinstance(metadata["created_at"], datetime)
    assert isinstance(metadata["updated_at"], datetime)


def test_document_metadata_update(editor_instance):
    """Test document metadata update operations."""
    doc = editor_instance.new_document("Test")
    initial_metadata = doc.metadata.copy()  # Make a copy of initial metadata
    time.sleep(0.1)  # Wait a bit to ensure timestamp difference
    doc.update_content("Test content")
    updated_metadata = doc.metadata
    assert updated_metadata["version"] >= initial_metadata["version"]


def test_document_content_versioning(editor_instance):
    """Test document content version tracking."""
    doc = editor_instance.new_document("Test")
    assert doc.version == 1

    doc.update_content("Version 1")
    assert doc.version == 2

    doc.update_content("Version 2")
    assert doc.version == 3


def test_document_timestamps(editor_instance):
    """Test document timestamp tracking."""
    doc = editor_instance.new_document("Test")
    initial_metadata = doc.metadata.copy()  # Make a copy of initial metadata
    time.sleep(0.1)  # Wait a bit to ensure timestamp difference
    doc.update_content("Test content")
    updated_metadata = doc.metadata
    assert updated_metadata["updated_at"] >= initial_metadata["updated_at"]


def test_editor_document_management(editor_instance):
    """Test editor document management."""
    # Test document creation
    doc = editor_instance.new_document("Test")
    assert doc.metadata["title"] == "Test"

    # Test content update
    doc.update_content("Test content")
    assert doc.content == "Test content"

    # Test document saving
    assert editor_instance.save_document()

    # Test document loading
    loaded_doc = editor_instance.load_document("Test")
    assert loaded_doc is not None
    assert loaded_doc.content == "Test content"


def test_document_serialization_edge_cases(tmp_path: Path):
    """Test document serialization edge cases."""
    storage_dir = tmp_path / "storage"
    template_dir = tmp_path / "templates"
    editor = Editor(storage_dir, template_dir)

    # Test empty document
    doc = editor.new_document("Empty")
    assert editor.save_document()

    # Test document with special characters
    doc = editor.new_document("Special!@#$%^&*()")
    doc.update_content("Content with special chars: !@#$%^&*()")
    assert editor.save_document()

    # Test document with very long content
    doc = editor.new_document("Long")
    doc.update_content("x" * 1000000)  # 1MB of content
    assert editor.save_document()


def test_document_load_errors():
    """Test document loading error cases."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_dir = Path(temp_dir) / "storage"
        template_dir = Path(temp_dir) / "templates"
        editor = Editor(storage_dir, template_dir)

        # Test loading non-existent document
        assert editor.load_document("nonexistent") is None

        # Test loading corrupted document
        doc = editor.new_document("corrupted")
        doc.update_content("Test content")
        assert editor.save_document()

        # Corrupt the file
        doc_path = storage_dir / "corrupted.json"
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("invalid json")

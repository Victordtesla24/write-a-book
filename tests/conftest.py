"""Test fixtures."""

from pathlib import Path

import pytest

from src.book_editor.app.core.editor import DocumentManager, EditorApp
from src.book_editor.app.core.preview import PreviewManager
from src.book_editor.core.editor import Editor
from src.book_editor.core.template import Template, TemplateManager


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def editor(temp_dir: Path) -> Editor:
    """Create an Editor instance for testing."""
    storage_dir = temp_dir / "storage"
    template_dir = temp_dir / "templates"
    storage_dir.mkdir(parents=True, exist_ok=True)
    template_dir.mkdir(parents=True, exist_ok=True)
    return Editor(storage_dir, template_dir)


@pytest.fixture
def document_manager(temp_dir: Path) -> DocumentManager:
    """Create a DocumentManager instance for testing."""
    storage_dir = temp_dir / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return DocumentManager(storage_dir)


@pytest.fixture
def template_manager(temp_dir: Path) -> TemplateManager:
    """Create a TemplateManager instance for testing."""
    template_dir = temp_dir / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    return TemplateManager(template_dir)


@pytest.fixture
def preview_manager() -> PreviewManager:
    """Create a PreviewManager instance for testing."""
    return PreviewManager()


@pytest.fixture
def editor_app(temp_dir: Path) -> EditorApp:
    """Create an EditorApp instance for testing."""
    storage_dir = temp_dir / "storage"
    template_dir = temp_dir / "templates"
    storage_dir.mkdir(parents=True, exist_ok=True)
    template_dir.mkdir(parents=True, exist_ok=True)
    return EditorApp(storage_dir, template_dir)


@pytest.fixture
def template() -> Template:
    """Create a template instance for testing."""
    template = Template("test_template", "general")
    template.metadata["description"] = "Test template"
    template.metadata["tags"] = ["test"]
    return template

"""Standalone tests for the template manager module."""

import json
import pytest
from pathlib import Path

from src.book_editor.core.template import Template
from src.book_editor.core.template_manager import TemplateManager


@pytest.fixture
def test_template():
    """Create a test template."""
    template = Template(name="Test Template", category="test")
    template.metadata.update({
        "description": "A test template",
        "tags": ["test"],
        "format": "markdown"
    })
    return template


@pytest.fixture
def manager(tmp_path):
    """Create a template manager with temporary storage."""
    return TemplateManager(template_dir=tmp_path)


def test_manager_initialization(tmp_path):
    """Test template manager initialization."""
    manager = TemplateManager(template_dir=tmp_path)
    assert manager.template_dir == tmp_path
    assert manager.template_dir.exists()
    assert "general" in manager.categories


def test_add_category(manager):
    """Test adding template categories."""
    assert manager.add_category("novels") is True
    assert "novels" in manager.categories
    
    # Test adding existing category
    assert manager.add_category("novels") is False
    
    # Test adding empty category
    assert manager.add_category("") is False


def test_get_categories(manager):
    """Test getting template categories."""
    manager.add_category("novels")
    manager.add_category("articles")
    
    categories = manager.get_categories()
    assert "general" in categories
    assert "novels" in categories
    assert "articles" in categories


def test_save_template(manager, test_template):
    """Test saving a template."""
    # Add template category first
    manager.add_category(test_template.category)
    
    # Save template
    assert manager.save_template(test_template) is True
    
    # Verify file exists
    template_path = manager.template_dir / f"{test_template.name}.json"
    assert template_path.exists()


def test_save_template_invalid_category(manager, test_template):
    """Test saving template with invalid category."""
    # Category not added yet
    assert manager.save_template(test_template) is False


def test_get_template(manager, test_template):
    """Test getting a template."""
    # Add category and save template
    manager.add_category(test_template.category)
    manager.save_template(test_template)
    
    # Get template
    loaded = manager.get_template(test_template.name)
    assert loaded is not None
    assert loaded.name == test_template.name
    assert loaded.category == test_template.category


def test_get_nonexistent_template(manager):
    """Test getting a nonexistent template."""
    assert manager.get_template("nonexistent") is None


def test_list_templates(manager):
    """Test listing templates."""
    # Create and save test templates
    template1 = Template(name="Template 1", category="test")
    template2 = Template(name="Template 2", category="test")
    
    manager.add_category("test")
    manager.save_template(template1)
    manager.save_template(template2)
    
    # List all templates
    templates = manager.list_templates()
    assert len(templates) == 2
    assert "Template 1" in templates
    assert "Template 2" in templates
    
    # List by category
    templates = manager.list_templates(category="test")
    assert len(templates) == 2
    assert "Template 1" in templates
    assert "Template 2" in templates
    
    # List by nonexistent category
    templates = manager.list_templates(category="nonexistent")
    assert len(templates) == 0


def test_search_templates(manager):
    """Test searching templates."""
    # Create and save test templates
    template1 = Template(name="Python Guide", category="test")
    template1.metadata.update({
        "description": "A guide for Python",
        "tags": ["python", "programming"],
        "format": "markdown"
    })
    
    template2 = Template(name="Java Guide", category="test")
    template2.metadata.update({
        "description": "A guide for Java",
        "tags": ["java", "programming"],
        "format": "markdown"
    })
    
    manager.add_category("test")
    manager.save_template(template1)
    manager.save_template(template2)
    
    # Search by name
    results = manager.search_templates("Python")
    assert len(results) == 1
    assert results[0].name == "Python Guide"
    
    # Search by description
    results = manager.search_templates("guide for")
    assert len(results) == 2
    
    # Search by tag
    results = manager.search_templates("programming")
    assert len(results) == 2
    
    # Search with no matches
    results = manager.search_templates("nonexistent")
    assert len(results) == 0


def test_load_template(manager, test_template):
    """Test loading a template."""
    # Add category and save template
    manager.add_category(test_template.category)
    manager.save_template(test_template)
    
    # Load template
    loaded = manager.load_template(test_template.name)
    assert loaded is not None
    assert loaded.name == test_template.name
    assert loaded.category == test_template.category


def test_load_nonexistent_template(manager):
    """Test loading a nonexistent template."""
    assert manager.load_template("nonexistent") is None


def test_load_invalid_template(manager):
    """Test loading an invalid template file."""
    # Create invalid template file
    invalid_path = manager.template_dir / "invalid.json"
    with invalid_path.open('w') as f:
        f.write("invalid json")
    
    assert manager.load_template("invalid") is None


def test_save_load_with_styles(manager):
    """Test saving and loading template with styles."""
    template = Template(name="Styled Template", category="test")
    template.add_style("fonts", "custom", {"font-family": "Arial"})
    
    manager.add_category("test")
    manager.save_template(template)
    
    loaded = manager.load_template(template.name)
    assert loaded is not None
    assert "fonts" in loaded.styles
    assert "custom" in loaded.styles["fonts"]
    assert loaded.styles["fonts"]["custom"] == {"font-family": "Arial"}


def test_save_load_with_layouts(manager):
    """Test saving and loading template with layouts."""
    template = Template(name="Layout Template", category="test")
    template.add_layout({"margin": "2cm"})
    
    manager.add_category("test")
    manager.save_template(template)
    
    loaded = manager.load_template(template.name)
    assert loaded is not None
    assert {"margin": "2cm"} in loaded.layouts

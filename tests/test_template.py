"""Module docstring placeholder."""

import pytest

from book_editor.core.template import (
    PAGE_LAYOUTS,
    VINTAGE_BORDERS,
    Template,
    TemplateManager,
)


@pytest.fixture
def template_storage(tmp_path):
    """Provide temporary template storage directory"""
    return tmp_path / "templates"


@pytest.fixture
def template_manager(template_storage):
    """Provide template manager instance"""
    return TemplateManager(template_storage)


def test_template_creation():
    """Test template creation and metadata"""
    template = Template("Test Template", "fiction")

    assert template.name == "Test Template"
    assert template.category == "fiction"
    assert template.metadata["version"] == "1.0.0"
    assert isinstance(template.styles["borders"], dict)
    assert isinstance(template.layouts, dict)


def test_template_serialization():
    """Test template serialization and deserialization"""
    template = Template("Test")
    template.metadata["author"] = "John Doe"
    template.styles["borders"] = VINTAGE_BORDERS["ornate"]
    template.layouts["custom"] = PAGE_LAYOUTS["manuscript"]

    data = template.to_dict()
    loaded = Template.from_dict(data)

    assert loaded.name == template.name
    assert loaded.metadata["author"] == "John Doe"
    assert loaded.styles["borders"] == VINTAGE_BORDERS["ornate"]
    assert loaded.layouts["custom"] == PAGE_LAYOUTS["manuscript"]


def test_template_manager_categories(template_manager):
    """Test template category management"""
    # Default category should exist
    assert "general" in template_manager.get_categories()

    # Add new category
    assert template_manager.add_category("fiction", "Fiction templates")
    assert "fiction" in template_manager.get_categories()

    # Duplicate category should fail
    assert not template_manager.add_category("fiction")


def test_template_manager_save_load(template_manager):
    """Test saving and loading templates"""
    template = Template("Novel", "fiction")
    template.metadata["description"] = "A novel template"
    template.metadata["tags"] = ["fiction", "novel"]

    # Should fail with non-existent category
    assert not template_manager.save_template(template)

    # Add category and try again
    template_manager.add_category("fiction")
    assert template_manager.save_template(template)

    # Load and verify
    loaded = template_manager.load_template("Novel")
    assert loaded is not None
    assert loaded.name == "Novel"
    assert loaded.metadata["tags"] == ["fiction", "novel"]


def test_template_manager_listing(template_manager):
    """Test template listing and filtering"""
    # Add categories
    template_manager.add_category("fiction")
    template_manager.add_category("non-fiction")

    # Add templates
    templates = [
        Template("Novel", "fiction"),
        Template("Short Story", "fiction"),
        Template("Biography", "non-fiction"),
    ]

    for template in templates:
        template_manager.save_template(template)

    # List all templates
    all_templates = template_manager.list_templates()
    assert len(all_templates) == 3
    assert "Novel" in all_templates

    # List by category
    fiction_templates = template_manager.list_templates("fiction")
    assert len(fiction_templates) == 2
    assert "Biography" not in fiction_templates


def test_template_search(template_manager):
    """Test template search functionality"""
    # Add category and templates
    template_manager.add_category("fiction")

    template1 = Template("Mystery Novel", "fiction")
    template1.metadata["description"] = "A template for mystery novels"
    template1.metadata["tags"] = ["mystery", "novel"]

    template2 = Template("Romance", "fiction")
    template2.metadata["description"] = "A template for romance novels"
    template2.metadata["tags"] = ["romance", "love"]

    template_manager.save_template(template1)
    template_manager.save_template(template2)

    # Search by name
    results = template_manager.search_templates("mystery")
    assert len(results) == 1
    assert results[0]["name"] == "Mystery Novel"

    # Search by tag
    results = template_manager.search_templates("romance")
    assert len(results) == 1
    assert results[0]["tags"] == ["romance", "love"]

    # Search by description
    results = template_manager.search_templates("template for")
    assert len(results) == 2

# pylint: disable=redefined-outer-name

"""Test module for template functionality."""

from typing import Any, Dict, cast

import pytest  # pylint: disable=import-error

from book_editor.core.template import (
    PAGE_LAYOUTS,
    VINTAGE_BORDERS,
    Template,
    TemplateManager,
)


@pytest.fixture(scope="function")
def test_storage_dir(tmp_path):
    """Create a temporary storage directory for testing."""
    storage_dir = tmp_path / "templates"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir


@pytest.fixture(scope="function")
def test_manager(test_storage_dir):
    """Create a test template manager instance."""
    return TemplateManager(test_storage_dir)


def test_template_creation():
    """Test template creation and metadata"""
    template = Template("Test Template", "fiction")

    assert template.name == "Test Template"
    assert template.category == "fiction"
    # Use get() for optional TypedDict fields
    assert template.metadata.get("format", "") == "markdown"
    assert isinstance(template.styles, dict)
    assert isinstance(template.layouts, list)


def test_template_serialization():
    """Test template serialization and deserialization"""
    template = Template("Test")
    # Set optional metadata fields explicitly
    template.metadata["description"] = "Test template"
    template.add_style("borders", "classic", VINTAGE_BORDERS["classic"])
    template.add_layout(PAGE_LAYOUTS["manuscript"])

    data = template.to_dict()
    # Cast the dictionary to the correct type
    template_data = cast(Dict[str, Any], data)
    loaded = Template.from_dict(template_data)

    assert loaded.name == template.name
    # Use get() for optional TypedDict fields
    assert loaded.metadata.get("description") == "Test template"
    assert loaded.styles["borders"]["classic"] == VINTAGE_BORDERS["classic"]
    assert loaded.layouts[0] == PAGE_LAYOUTS["manuscript"]


def test_template_manager_categories(test_manager):
    """Test template category management."""
    # Default category should exist
    assert "general" in test_manager.get_categories()

    # Add new category
    assert test_manager.add_category("fiction", "Fiction templates")
    assert "fiction" in test_manager.get_categories()

    # Duplicate category should fail
    assert not test_manager.add_category("fiction")


def test_template_manager_save_load(test_manager):
    """Test saving and loading templates."""
    template = Template("Novel", "fiction")
    template.metadata["description"] = "A novel template"
    template.metadata["tags"] = ["fiction", "novel"]

    # Should fail with non-existent category
    assert not test_manager.save_template(template)

    # Add category and try again
    test_manager.add_category("fiction")
    assert test_manager.save_template(template)

    # Load and verify
    loaded = test_manager.load_template("Novel")
    assert loaded is not None
    assert loaded.name == "Novel"
    assert loaded.metadata["tags"] == ["fiction", "novel"]


def test_template_manager_listing(test_manager):
    """Test template listing and filtering."""
    # Add categories
    test_manager.add_category("fiction")
    test_manager.add_category("non-fiction")

    # Add templates
    templates = [
        Template("Novel", "fiction"),
        Template("Short Story", "fiction"),
        Template("Biography", "non-fiction"),
    ]

    for template in templates:
        test_manager.save_template(template)

    # List all templates
    all_templates = test_manager.list_templates()
    assert len(all_templates) == 3
    assert "Novel" in all_templates

    # List by category
    fiction_templates = test_manager.list_templates("fiction")
    assert len(fiction_templates) == 2
    assert "Biography" not in fiction_templates


def test_template_search(test_manager):
    """Test template search functionality."""
    # Add category and templates
    test_manager.add_category("fiction")

    template1 = Template("Mystery Novel", "fiction")
    template1.metadata["description"] = "A template for mystery novels"
    template1.metadata["tags"] = ["mystery", "novel"]

    template2 = Template("Romance", "fiction")
    template2.metadata["description"] = "A template for romance novels"
    template2.metadata["tags"] = ["romance", "love"]

    test_manager.save_template(template1)
    test_manager.save_template(template2)

    # Search by name
    results = test_manager.search_templates("mystery")
    assert len(results) == 1
    assert results[0]["name"] == "Mystery Novel"

    # Search by tag
    results = test_manager.search_templates("romance")
    assert len(results) == 1
    assert results[0]["metadata"]["tags"] == ["romance", "love"]

    # Search by description
    results = test_manager.search_templates("template for")
    assert len(results) == 2

"""Tests for the template manager module."""

import json
import tempfile
from pathlib import Path

import pytest

from src.book_editor.core.template import Template
from src.book_editor.core.template_manager import TemplateManager


@pytest.fixture
def template_dir():
    """Create a temporary template directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def template_manager(template_dir):
    """Create a test template manager."""
    return TemplateManager(template_dir)


@pytest.fixture
def template():
    """Create a test template."""
    return Template("Test Template", "test")


def test_template_manager_initialization(template_dir):
    """Test template manager initialization."""
    manager = TemplateManager(template_dir)
    assert manager.template_dir == template_dir
    assert manager.template_dir.exists()

    # Test with string path
    manager = TemplateManager(str(template_dir))
    assert manager.template_dir == template_dir
    assert manager.template_dir.exists()


def test_template_manager_initialization_validation():
    """Test template manager initialization validation."""
    with pytest.raises(ValueError, match="Template directory path cannot be empty"):
        TemplateManager("")
    with pytest.raises(ValueError, match="Template directory path cannot be empty"):
        TemplateManager(None)  # type: ignore


def test_template_manager_save_load_template(template_manager, template):
    """Test saving and loading templates."""
    # Save template
    path = template_manager.save_template(template)
    assert path.exists()
    assert path.name == "Test_Template.json"

    # Load template
    loaded_template = template_manager.load_template(path)
    assert loaded_template is not None
    assert loaded_template.name == template.name
    assert loaded_template.category == template.category
    assert loaded_template.metadata == template.metadata
    assert loaded_template.styles == template.styles
    assert loaded_template.layouts == template.layouts

    # Test loading with string path
    loaded_template = template_manager.load_template(str(path))
    assert loaded_template is not None
    assert loaded_template.name == template.name


def test_template_manager_load_nonexistent_template(template_manager):
    """Test loading nonexistent template."""
    path = template_manager.template_dir / "nonexistent.json"
    assert template_manager.load_template(path) is None

    # Test with string path
    assert template_manager.load_template(str(path)) is None


def test_template_manager_load_invalid_template(template_manager):
    """Test loading invalid template file."""
    # Test with invalid JSON
    path = template_manager.template_dir / "invalid.json"
    path.write_text("invalid json")
    assert template_manager.load_template(path) is None

    # Test with valid JSON but invalid template data
    path.write_text('{"name": "Test", "invalid": true}')
    assert template_manager.load_template(path) is None


def test_template_manager_list_templates(template_manager, template):
    """Test listing templates."""
    # Initially empty
    templates = template_manager.list_templates()
    assert len(templates) == 0

    # Save a template
    template_manager.save_template(template)
    templates = template_manager.list_templates()
    assert len(templates) == 1
    assert templates[0].name == template.name

    # Save another template
    template2 = Template("Another Template", "test")
    template_manager.save_template(template2)
    templates = template_manager.list_templates()
    assert len(templates) == 2
    assert any(t.name == "Another Template" for t in templates)

    # Test with invalid template file in directory
    invalid_path = template_manager.template_dir / "invalid.json"
    invalid_path.write_text("invalid json")
    templates = template_manager.list_templates()
    assert len(templates) == 2  # Invalid template should be skipped


def test_template_manager_list_templates_by_category(template_manager, template):
    """Test listing templates by category."""
    # Save templates in different categories
    template_manager.save_template(template)
    template2 = Template("Another Template", "other")
    template_manager.save_template(template2)

    # List by category
    test_templates = template_manager.list_templates(category="test")
    assert len(test_templates) == 1
    assert test_templates[0].name == template.name

    other_templates = template_manager.list_templates(category="other")
    assert len(other_templates) == 1
    assert other_templates[0].name == template2.name

    # List nonexistent category
    none_templates = template_manager.list_templates(category="nonexistent")
    assert len(none_templates) == 0

    # List with empty category
    empty_templates = template_manager.list_templates(category="")
    assert len(empty_templates) == 0


def test_template_manager_get_template(template_manager, template):
    """Test getting template by name."""
    # Save template
    template_manager.save_template(template)

    # Get by name
    found_template = template_manager.get_template("Test Template")
    assert found_template is not None
    assert found_template.name == template.name

    # Get nonexistent template
    assert template_manager.get_template("Nonexistent") is None

    # Get with empty name
    assert template_manager.get_template("") is None

    # Get with None name
    assert template_manager.get_template(None) is None  # type: ignore


def test_template_manager_delete_template(template_manager, template):
    """Test deleting template."""
    # Save template
    path = template_manager.save_template(template)
    assert path.exists()

    # Delete template
    assert template_manager.delete_template(template.name) is True
    assert not path.exists()

    # Delete nonexistent template
    assert template_manager.delete_template("Nonexistent") is False

    # Delete with empty name
    assert template_manager.delete_template("") is False

    # Delete with None name
    assert template_manager.delete_template(None) is False  # type: ignore


def test_template_manager_save_invalid_template(template_manager, template):
    """Test saving invalid template."""
    # Make the template invalid by setting its name to empty
    template.name = ""  # type: ignore
    with pytest.raises(ValueError, match="Template name cannot be empty"):
        template_manager.save_template(template)

    # Test with None template
    with pytest.raises(AttributeError):
        template_manager.save_template(None)  # type: ignore


def test_template_manager_update_template(template_manager, template):
    """Test updating template."""
    # Save initial template
    path = template_manager.save_template(template)
    assert path.exists()

    # Update template
    template.metadata["description"] = "Updated description"
    updated_path = template_manager.save_template(template)
    assert updated_path == path
    assert updated_path.exists()

    # Load and verify update
    loaded_template = template_manager.load_template(path)
    assert loaded_template is not None
    assert loaded_template.metadata["description"] == "Updated description"

    # Test updating with invalid template
    template.name = ""  # type: ignore
    with pytest.raises(ValueError, match="Template name cannot be empty"):
        template_manager.save_template(template)


def test_template_manager_list_categories(template_manager, template):
    """Test listing template categories."""
    # Initially empty
    categories = template_manager.list_categories()
    assert len(categories) == 0

    # Save templates in different categories
    template_manager.save_template(template)
    template2 = Template("Another Template", "other")
    template_manager.save_template(template2)

    # List categories
    categories = template_manager.list_categories()
    assert len(categories) == 2
    assert "test" in categories
    assert "other" in categories

    # Test with invalid template file
    invalid_path = template_manager.template_dir / "invalid.json"
    invalid_path.write_text("invalid json")
    categories = template_manager.list_categories()
    assert len(categories) == 2  # Invalid template should be skipped


def test_template_manager_validate_template_name(template_manager):
    """Test template name validation."""
    assert template_manager.validate_template_name("Valid Name") is True
    assert template_manager.validate_template_name("valid-name") is True
    assert template_manager.validate_template_name("valid_name") is True
    assert template_manager.validate_template_name("123") is True
    assert template_manager.validate_template_name("") is False
    assert template_manager.validate_template_name("   ") is False
    assert template_manager.validate_template_name("Invalid/Name") is False
    assert template_manager.validate_template_name("Invalid\\Name") is False
    assert template_manager.validate_template_name(None) is False  # type: ignore


def test_template_manager_validate_category_name(template_manager):
    """Test category name validation."""
    assert template_manager.validate_category_name("valid") is True
    assert template_manager.validate_category_name("valid-name") is True
    assert template_manager.validate_category_name("123") is True
    assert template_manager.validate_category_name("") is False
    assert template_manager.validate_category_name("   ") is False
    assert template_manager.validate_category_name("Invalid/Name") is False
    assert template_manager.validate_category_name("Invalid\\Name") is False
    assert template_manager.validate_category_name("INVALID") is False
    assert template_manager.validate_category_name("Invalid Name") is False
    assert template_manager.validate_category_name(None) is False  # type: ignore


def test_template_manager_save_template_with_special_chars(template_manager):
    """Test saving template with special characters in name."""
    template = Template("Test/Template\\With:Special*Chars", "test")
    path = template_manager.save_template(template)
    assert path.exists()
    assert path.name == "Test_Template_With_Special_Chars.json"


def test_template_manager_save_template_with_unicode(template_manager):
    """Test saving template with unicode characters in name."""
    template = Template("Test Template 测试模板", "test")
    path = template_manager.save_template(template)
    assert path.exists()
    assert path.name == "Test_Template_测试模板.json"


def test_template_manager_save_template_with_spaces(template_manager):
    """Test saving template with spaces in name."""
    template = Template("  Test   Template  ", "test")
    path = template_manager.save_template(template)
    assert path.exists()
    assert path.name == "Test_Template.json"


def test_template_manager_save_template_with_case(template_manager):
    """Test saving template with different case in name."""
    template1 = Template("Test Template", "test")
    template2 = Template("TEST TEMPLATE", "test")
    path1 = template_manager.save_template(template1)
    path2 = template_manager.save_template(template2)
    assert path1 != path2
    assert path1.exists()
    assert path2.exists()


def test_template_manager_save_template_with_long_name(template_manager):
    """Test saving template with a very long name."""
    long_name = "A" * 255
    template = Template(long_name, "test")
    path = template_manager.save_template(template)
    assert path.exists()
    assert len(path.name) < 255  # File system limit


def test_template_manager_save_template_with_invalid_chars(template_manager):
    """Test saving template with invalid characters in name."""
    template = Template("Test\0Template\nWith\tInvalid\rChars", "test")
    path = template_manager.save_template(template)
    assert path.exists()
    assert path.name == "Test_Template_With_Invalid_Chars.json"


def test_template_manager_save_template_with_dots(template_manager):
    """Test saving template with dots in name."""
    template = Template("Test.Template.With.Dots", "test")
    path = template_manager.save_template(template)
    assert path.exists()
    assert path.name == "Test_Template_With_Dots.json"


def test_template_manager_save_template_with_leading_dots(template_manager):
    """Test saving template with leading dots in name."""
    template = Template("...Test Template", "test")
    path = template_manager.save_template(template)
    assert path.exists()
    assert path.name == "Test_Template.json"


def test_template_manager_save_template_with_trailing_dots(template_manager):
    """Test saving template with trailing dots in name."""
    template = Template("Test Template...", "test")
    path = template_manager.save_template(template)
    assert path.exists()
    assert path.name == "Test_Template.json"


def test_template_manager_save_template_with_only_dots(template_manager):
    """Test saving template with only dots in name."""
    template = Template("...", "test")
    with pytest.raises(ValueError, match="Invalid template name"):
        template_manager.save_template(template)


def test_template_manager_save_template_with_reserved_names(template_manager):
    """Test saving template with reserved file names."""
    reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
    for name in reserved_names:
        template = Template(name, "test")
        path = template_manager.save_template(template)
        assert path.exists()
        assert path.name == f"{name}_.json" 
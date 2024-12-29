"""Standalone tests for the template module."""

import pytest
from datetime import datetime
from pathlib import Path

from src.book_editor.core.template import Template, VALID_FORMATS


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


def test_template_creation():
    """Test template creation with valid data."""
    template = Template(name="Test Template", category="test")
    assert template.name == "Test Template"
    assert template.category == "test"
    assert isinstance(template.metadata, dict)
    assert isinstance(template.styles, dict)
    assert isinstance(template.layouts, list)


def test_template_creation_validation():
    """Test template creation validation."""
    with pytest.raises(ValueError):
        Template(name="", category="test")
    
    with pytest.raises(ValueError):
        Template(name="Test", category="")


def test_template_validate():
    """Test template validation."""
    template = Template(name="Test", category="test")
    template.metadata["format"] = "markdown"
    assert template.validate() is True

    # Test invalid format
    template.metadata["format"] = "invalid"
    with pytest.raises(ValueError):
        template.validate()


def test_template_add_style():
    """Test adding styles."""
    template = Template(name="Test", category="test")
    style_data = {"font-family": "Arial", "font-size": "12pt"}
    
    template.add_style("fonts", "custom", style_data)
    assert "fonts" in template.styles
    assert "custom" in template.styles["fonts"]
    assert template.styles["fonts"]["custom"] == style_data

    # Test invalid style data
    with pytest.raises(ValueError):
        template.add_style("fonts", "", {})
    with pytest.raises(ValueError):
        template.add_style("", "custom", {})
    with pytest.raises(ValueError):
        template.add_style("fonts", "custom", "invalid")


def test_template_add_layout():
    """Test adding layouts."""
    template = Template(name="Test", category="test")
    layout = {"margin": "2cm", "padding": "1cm"}
    
    template.add_layout(layout)
    assert layout in template.layouts

    # Test invalid layout
    with pytest.raises(ValueError):
        template.add_layout({})
    with pytest.raises(ValueError):
        template.add_layout("invalid")


def test_template_render_formats():
    """Test content rendering with different formats."""
    template = Template(name="Test", category="test")
    
    # Test markdown format
    template.metadata["format"] = "markdown"
    rendered = template.render("# Test Content")
    assert "<h1>Test Content</h1>" in rendered
    
    # Test HTML format
    template.metadata["format"] = "html"
    rendered = template.render("<h1>Test Content</h1>")
    assert "<h1>Test Content</h1>" in rendered
    
    # Test text format
    template.metadata["format"] = "text"
    rendered = template.render("Test Content")
    assert "<pre>Test Content</pre>" in rendered


def test_template_render_with_styles():
    """Test rendering with styles."""
    template = Template(name="Test", category="test")
    template.metadata["format"] = "markdown"
    
    # Add border style
    template.add_style("borders", "custom", {
        "border": "1px solid black",
        "border-radius": "5px"
    })
    
    # Add font style
    template.add_style("fonts", "custom", {
        "font-family": "Arial",
        "font-size": "14pt"
    })
    
    # Add text style
    template.add_style("text", "custom", {
        "color": "blue",
        "text-align": "center"
    })
    
    # Add background style
    template.add_style("background", "custom", {
        "background-color": "#f0f0f0",
        "opacity": "0.9"
    })
    
    rendered = template.render("Test Content")
    assert "border: 1px solid black" in rendered
    assert "border-radius: 5px" in rendered
    assert "font-family: Arial" in rendered
    assert "font-size: 14pt" in rendered
    assert "color: blue" in rendered
    assert "text-align: center" in rendered
    assert "background-color: #f0f0f0" in rendered
    assert "opacity: 0.9" in rendered


def test_template_render_with_layouts():
    """Test rendering with layouts."""
    template = Template(name="Test", category="test")
    template.metadata["format"] = "markdown"
    
    template.add_layout({
        "margin": "2cm",
        "padding": "1cm",
        "line-height": "1.5"
    })
    
    rendered = template.render("Test Content")
    assert "margin: 2cm" in rendered
    assert "padding: 1cm" in rendered
    assert "line-height: 1.5" in rendered


def test_template_render_invalid_format():
    """Test rendering with invalid format."""
    template = Template(name="Test", category="test")
    template.metadata["format"] = "invalid"
    
    with pytest.raises(ValueError):
        template.render("Test content")


def test_template_save_load(tmp_path):
    """Test template saving and loading."""
    template = Template(name="Test Template", category="test")
    template.metadata["format"] = "markdown"
    template.add_style("fonts", "custom", {"font-family": "Arial"})
    template.add_layout({"margin": "2cm"})
    
    # Save template
    save_path = tmp_path / "test_template.json"
    template.save(save_path)
    assert save_path.exists()
    
    # Load template
    loaded = Template.load(save_path)
    assert loaded is not None
    assert loaded.name == template.name
    assert loaded.category == template.category
    assert loaded.metadata["format"] == template.metadata["format"]
    assert loaded.styles["fonts"]["custom"] == {"font-family": "Arial"}
    # Check if our custom layout was added (should be second since first is default)
    assert {"margin": "2cm"} in loaded.layouts


def test_template_load_nonexistent(tmp_path):
    """Test loading nonexistent template."""
    result = Template.load(tmp_path / "nonexistent.json")
    assert result is None


def test_template_load_invalid(tmp_path):
    """Test loading invalid template file."""
    invalid_path = tmp_path / "invalid.json"
    with invalid_path.open('w') as f:
        f.write("invalid json")
    
    result = Template.load(invalid_path)
    assert result is None


def test_template_to_dict():
    """Test template conversion to dictionary."""
    template = Template(name="Test Template", category="test")
    template.metadata["format"] = "markdown"
    template.add_style("fonts", "custom", {"font-family": "Arial"})
    template.add_layout({"margin": "2cm"})
    
    data = template.to_dict()
    assert data["name"] == "Test Template"
    assert data["category"] == "test"
    assert data["metadata"]["format"] == "markdown"
    assert data["styles"]["fonts"]["custom"] == {"font-family": "Arial"}
    # Check if our custom layout is in the layouts list
    assert {"margin": "2cm"} in data["layouts"]


def test_template_from_dict():
    """Test template creation from dictionary."""
    data = {
        "name": "Test Template",
        "category": "test",
        "metadata": {
            "format": "markdown",
            "tags": ["test"],
            "description": "Test template"
        },
        "styles": {
            "fonts": {
                "custom": {"font-family": "Arial"}
            }
        },
        "layouts": [
            {"margin": "2cm"}
        ]
    }
    template = Template.from_dict(data)
    assert template.name == "Test Template"
    assert template.category == "test"
    assert template.metadata["format"] == "markdown"
    assert template.styles["fonts"]["custom"] == {"font-family": "Arial"}
    assert template.layouts[0] == {"margin": "2cm"}


def test_template_from_dict_invalid():
    """Test template creation from invalid dictionary."""
    with pytest.raises(ValueError):
        Template.from_dict({"invalid": "data"})
    with pytest.raises(ValueError):
        Template.from_dict({})
    with pytest.raises(ValueError):
        Template.from_dict(None)


def test_template_merge():
    """Test template merging."""
    template1 = Template(name="Template 1", category="test")
    template1.add_style("fonts", "custom", {"font-family": "Arial"})
    template1.add_layout({"margin": "2cm"})
    
    template2 = Template(name="Template 2", category="test")
    template2.add_style("fonts", "custom2", {"font-family": "Times"})
    template2.add_layout({"padding": "1cm"})
    
    template1.merge(template2)
    assert "custom" in template1.styles["fonts"]
    assert "custom2" in template1.styles["fonts"]
    assert {"margin": "2cm"} in template1.layouts
    assert {"padding": "1cm"} in template1.layouts

    # Test merging with None
    with pytest.raises(ValueError):
        template1.merge(None)


def test_template_merge_styles():
    """Test merging styles."""
    template1 = Template(name="Template 1", category="test")
    template1.add_style("fonts", "custom", {"font-family": "Arial"})
    
    template2 = Template(name="Template 2", category="test")
    template2.add_style("fonts", "custom2", {"font-family": "Times"})
    template2.add_style("borders", "custom", {"border": "1px solid black"})
    
    template1.merge_styles(template2)
    assert "custom" in template1.styles["fonts"]
    assert "custom2" in template1.styles["fonts"]
    assert "custom" in template1.styles["borders"]

    # Test merging with None
    with pytest.raises(ValueError):
        template1.merge_styles(None)
    
    # Test merging with invalid styles
    template2.styles = "invalid"  # type: ignore
    with pytest.raises(ValueError):
        template1.merge_styles(template2)


def test_template_merge_layouts():
    """Test merging layouts."""
    template1 = Template(name="Template 1", category="test")
    template1.add_layout({"margin": "2cm"})
    
    template2 = Template(name="Template 2", category="test")
    template2.add_layout({"padding": "1cm"})
    
    template1.merge_layouts(template2)
    assert {"margin": "2cm"} in template1.layouts
    assert {"padding": "1cm"} in template1.layouts

    # Test merging with None
    with pytest.raises(ValueError):
        template1.merge_layouts(None)
    
    # Test merging with invalid layouts
    template2.layouts = "invalid"  # type: ignore
    with pytest.raises(ValueError):
        template1.merge_layouts(template2)


def test_template_copy():
    """Test template copying."""
    template = Template(name="Original", category="test")
    template.metadata["format"] = "markdown"
    template.add_style("fonts", "custom", {"font-family": "Arial"})
    template.add_layout({"margin": "2cm"})
    
    copy = template.copy()
    assert copy.name == template.name
    assert copy.category == template.category
    assert copy.metadata == template.metadata
    assert copy.styles == template.styles
    assert copy.layouts == template.layouts
    
    # Verify deep copy
    template.metadata["format"] = "html"
    assert copy.metadata["format"] == "markdown"


def test_template_validate_metadata():
    """Test metadata validation."""
    template = Template(name="Test", category="test")
    template.metadata.update({
        "format": "markdown",
        "tags": ["test"],
        "description": "Test template"
    })
    assert template.validate_metadata() is True

    # Test invalid format
    template.metadata["format"] = "invalid"
    with pytest.raises(ValueError):
        template.validate_metadata()
    
    # Test invalid tags
    template.metadata["format"] = "markdown"
    template.metadata["tags"] = "invalid"  # type: ignore
    with pytest.raises(ValueError):
        template.validate_metadata()
    
    # Test invalid tag type
    template.metadata["tags"] = [1, 2, 3]  # type: ignore
    with pytest.raises(ValueError):
        template.validate_metadata()
    
    # Test invalid description
    template.metadata["tags"] = ["test"]
    template.metadata["description"] = 123  # type: ignore
    with pytest.raises(ValueError):
        template.validate_metadata()


def test_template_validate_styles():
    """Test styles validation."""
    template = Template(name="Test", category="test")
    template.add_style("fonts", "custom", {"font-family": "Arial"})
    assert template.validate_styles() is True

    # Test invalid styles
    template.styles = "invalid"  # type: ignore
    with pytest.raises(ValueError):
        template.validate_styles()
    
    # Test invalid style category
    template = Template(name="Test", category="test")
    template.styles["fonts"] = "invalid"  # type: ignore
    with pytest.raises(ValueError):
        template.validate_styles()
    
    # Test invalid style properties
    template = Template(name="Test", category="test")
    template.styles["fonts"] = {"custom": "invalid"}  # type: ignore
    with pytest.raises(ValueError):
        template.validate_styles()


def test_template_validate_layouts():
    """Test layouts validation."""
    template = Template(name="Test", category="test")
    template.add_layout({"margin": "2cm"})
    assert template.validate_layouts() is True

    # Test invalid layouts
    template.layouts = "invalid"  # type: ignore
    with pytest.raises(ValueError):
        template.validate_layouts()
    
    # Test invalid layout type
    template = Template(name="Test", category="test")
    template.layouts.append("invalid")  # type: ignore
    with pytest.raises(ValueError):
        template.validate_layouts()
    
    # Test empty layout
    template = Template(name="Test", category="test")
    template.layouts.append({})
    with pytest.raises(ValueError):
        template.validate_layouts()

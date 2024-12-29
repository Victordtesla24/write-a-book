"""Tests for the template module."""

from pathlib import Path

import pytest

from src.book_editor.core.template import Template, TemplateManager


def test_template_initialization():
    """Test template initialization."""
    template = Template("Test Template", "test")
    assert template.name == "Test Template"
    assert template.category == "test"
    assert isinstance(template.metadata, dict)
    assert isinstance(template.styles, dict)
    assert isinstance(template.layouts, list)


def test_template_initialization_validation():
    """Test template initialization validation."""
    with pytest.raises(ValueError):
        Template("", "test")  # Empty name
    with pytest.raises(ValueError):
        Template("Test", "")  # Empty category


def test_template_validate_metadata():
    """Test template metadata validation."""
    template = Template("Test", "test")
    assert template.validate_metadata() is True

    # Test missing format
    del template.metadata["format"]
    with pytest.raises(ValueError):
        template.validate_metadata()

    # Test invalid format
    template.metadata["format"] = "invalid"
    with pytest.raises(ValueError):
        template.validate_metadata()

    # Test invalid tags type
    template.metadata["format"] = "markdown"
    template.metadata["tags"] = "not a list"
    with pytest.raises(ValueError):
        template.validate_metadata()

    # Test invalid tag type
    template.metadata["tags"] = ["valid", 123]  # Non-string tag
    with pytest.raises(ValueError):
        template.validate_metadata()

    # Test invalid description type
    template.metadata["tags"] = ["valid"]
    template.metadata["description"] = 123  # Non-string description
    with pytest.raises(ValueError):
        template.validate_metadata()


def test_template_validate_styles():
    """Test template styles validation."""
    template = Template("Test", "test")
    assert template.validate_styles() is True

    # Test invalid styles type
    template.styles = "not a dict"  # type: ignore
    with pytest.raises(ValueError):
        template.validate_styles()

    # Test invalid category type
    template.styles = {"fonts": "not a dict"}  # type: ignore
    with pytest.raises(ValueError):
        template.validate_styles()

    # Test invalid style properties type
    template.styles = {"fonts": {"default": "not a dict"}}  # type: ignore
    with pytest.raises(ValueError):
        template.validate_styles()


def test_template_validate_layouts():
    """Test template layouts validation."""
    template = Template("Test", "test")
    assert template.validate_layouts() is True

    # Test invalid layouts type
    template.layouts = "not a list"  # type: ignore
    with pytest.raises(ValueError):
        template.validate_layouts()

    # Test invalid layout type
    template.layouts = ["not a dict"]  # type: ignore
    with pytest.raises(ValueError):
        template.validate_layouts()

    # Test empty layout
    template.layouts = [{}]
    with pytest.raises(ValueError):
        template.validate_layouts()


def test_template_validation():
    """Test template validation."""
    template = Template("Test", "test")
    assert template.validate() is True

    # Test invalid metadata format
    template.metadata["format"] = "invalid"
    with pytest.raises(ValueError):
        template.validate()

    # Test invalid metadata tags
    template.metadata["format"] = "markdown"
    template.metadata["tags"] = "not a list"
    with pytest.raises(ValueError):
        template.validate()

    # Test invalid styles
    template.metadata["tags"] = []
    template.styles = "not a dict"  # type: ignore
    with pytest.raises(ValueError):
        template.validate()

    # Test invalid layouts
    template.styles = {}
    template.layouts = "not a list"  # type: ignore
    with pytest.raises(ValueError):
        template.validate()


def test_template_add_style():
    """Test adding styles to template."""
    template = Template("Test", "test")
    style_data = {"font-family": "Arial", "font-size": "12pt"}
    
    template.add_style("borders", "custom", style_data)  # Use borders instead of fonts to avoid defaults
    assert "borders" in template.styles
    assert "custom" in template.styles["borders"]
    assert template.styles["borders"]["custom"] == style_data

    # Test invalid style data
    with pytest.raises(ValueError):
        template.add_style("", "default", style_data)  # Empty style type
    with pytest.raises(ValueError):
        template.add_style("fonts", "", style_data)  # Empty style name
    with pytest.raises(ValueError):
        template.add_style("fonts", "default", "not a dict")  # type: ignore


def test_template_add_layout():
    """Test adding layouts to template."""
    template = Template("Test", "test")
    layout = {"margin": "2cm", "padding": "1cm"}
    
    template.add_layout(layout)
    assert layout in template.layouts

    # Test invalid layout
    with pytest.raises(ValueError):
        template.add_layout({})  # Empty layout
    with pytest.raises(ValueError):
        template.add_layout("not a dict")  # type: ignore


def test_template_to_dict():
    """Test converting template to dictionary."""
    template = Template("Test", "test")
    template.metadata["description"] = "Test template"
    template.metadata["tags"] = ["test"]
    
    data = template.to_dict()
    assert data["name"] == "Test"
    assert data["category"] == "test"
    assert data["metadata"]["description"] == "Test template"
    assert data["metadata"]["tags"] == ["test"]
    assert isinstance(data["styles"], dict)
    assert isinstance(data["layouts"], list)


def test_template_from_dict():
    """Test creating template from dictionary."""
    data = {
        "name": "Test",
        "category": "test",
        "metadata": {
            "description": "Test template",
            "tags": ["test"],
            "format": "markdown"
        },
        "styles": {
            "fonts": {
                "default": {
                    "font-family": "Arial",
                    "font-size": "12pt"
                }
            }
        },
        "layouts": [
            {
                "margin": "2cm",
                "padding": "1cm"
            }
        ]
    }
    
    template = Template.from_dict(data)
    assert template.name == "Test"
    assert template.category == "test"
    assert template.metadata["description"] == "Test template"
    assert template.metadata["tags"] == ["test"]
    assert template.styles["fonts"]["default"]["font-family"] == "Arial"
    assert template.layouts[0]["margin"] == "2cm"

    # Test invalid data
    with pytest.raises(ValueError):
        Template.from_dict({})  # Empty dict
    with pytest.raises(ValueError):
        Template.from_dict({"name": "Test"})  # Missing category
    with pytest.raises(ValueError):
        Template.from_dict("not a dict")  # type: ignore


def test_template_save_load(tmp_path: Path):
    """Test saving and loading template."""
    template = Template("Test", "test")
    template.metadata["description"] = "Test template"
    path = tmp_path / "test_template.json"
    
    template.save(path)
    assert path.exists()
    
    loaded = Template.load(path)
    assert loaded is not None
    assert loaded.name == template.name
    assert loaded.category == template.category
    assert loaded.metadata["description"] == template.metadata["description"]

    # Test loading invalid file
    invalid_path = tmp_path / "nonexistent.json"
    assert Template.load(invalid_path) is None


def test_template_render():
    """Test rendering template content."""
    template = Template("Test", "test")
    
    # Test markdown rendering
    template.metadata["format"] = "markdown"
    rendered = template.render("# Test\n\nTest content")
    assert "<h1>Test</h1>" in rendered
    assert "<p>Test content</p>" in rendered

    # Test HTML rendering
    template.metadata["format"] = "html"
    rendered = template.render("<h1>Test</h1><p>Test content</p>")
    assert "<h1>Test</h1>" in rendered
    assert "<p>Test content</p>" in rendered

    # Test text rendering
    template.metadata["format"] = "text"
    rendered = template.render("Test content")
    assert "<pre>Test content</pre>" in rendered

    # Test invalid format
    template.metadata["format"] = "invalid"
    with pytest.raises(ValueError):
        template.render("Test content")

    # Test empty content
    template.metadata["format"] = "markdown"
    with pytest.raises(ValueError):
        template.render("")


def test_template_build_styles():
    """Test template style building."""
    template = Template("Test", "test")
    
    # Test border style building
    template.add_style("borders", "test", {
        "border": "1px solid black",
        "border-radius": "5px"
    })
    border_style = template._build_border_style()
    assert "border: 1px solid black" in border_style
    assert "border-radius: 5px" in border_style

    # Test content style building
    template.add_style("fonts", "test", {
        "font-family": "Arial",
        "font-size": "12pt"
    })
    template.add_style("text", "test", {
        "color": "#000000",
        "line-height": "1.5"
    })
    template.add_style("background", "test", {
        "background-color": "#FFFFFF"
    })
    content_style = template._build_content_style()
    assert "font-family: Arial" in content_style
    assert "font-size: 12pt" in content_style
    assert "color: #000000" in content_style
    assert "line-height: 1.5" in content_style
    assert "background-color: #FFFFFF" in content_style


def test_template_merge():
    """Test merging templates."""
    template1 = Template("Test1", "test")
    template1.metadata["description"] = "Template 1"
    # Clear default layouts
    template1.layouts = []
    template1.add_style("borders", "default", {"border": "1px solid black"})
    template1.add_layout({"margin": "2cm"})

    template2 = Template("Test2", "test")
    template2.layouts = []  # Clear default layouts
    template2.metadata["description"] = "Template 2"
    template2.add_style("borders", "custom", {"border": "2px solid black"})
    template2.add_layout({"padding": "1cm"})

    template1.merge(template2)
    assert template1.metadata["description"] == "Template 2"
    assert "default" in template1.styles["borders"]
    assert "custom" in template1.styles["borders"]
    assert len(template1.layouts) == 2  # template1 layout + template2 layout

    # Test invalid merge
    with pytest.raises(ValueError):
        template1.merge(None)  # type: ignore


def test_template_merge_styles():
    """Test merging template styles."""
    template1 = Template("Test1", "test")
    template1.add_style("fonts", "default", {"font-family": "Arial"})
    template1.add_style("colors", "primary", {"color": "#000000"})

    template2 = Template("Test2", "test")
    template2.add_style("fonts", "custom", {"font-family": "Times"})
    template2.add_style("colors", "secondary", {"color": "#FFFFFF"})

    template1.merge_styles(template2)
    assert "default" in template1.styles["fonts"]
    assert "custom" in template1.styles["fonts"]
    assert "primary" in template1.styles["colors"]
    assert "secondary" in template1.styles["colors"]

    # Test invalid merge
    with pytest.raises(ValueError):
        template1.merge_styles(None)  # type: ignore
    with pytest.raises(ValueError):
        template2.styles = "not a dict"  # type: ignore
        template1.merge_styles(template2)


def test_template_merge_layouts():
    """Test merging template layouts."""
    template1 = Template("Test1", "test")
    template1.layouts = []  # Clear default layouts
    template1.add_layout({"margin": "2cm"})
    template1.add_layout({"padding": "1cm"})

    template2 = Template("Test2", "test")
    template2.layouts = []  # Clear default layouts
    template2.add_layout({"width": "100%"})
    template2.add_layout({"height": "100%"})

    template1.merge_layouts(template2)
    assert len(template1.layouts) == 4
    assert {"margin": "2cm"} in template1.layouts
    assert {"padding": "1cm"} in template1.layouts
    assert {"width": "100%"} in template1.layouts
    assert {"height": "100%"} in template1.layouts

    # Test invalid merge
    with pytest.raises(ValueError):
        template1.merge_layouts(None)  # type: ignore
    with pytest.raises(ValueError):
        template2.layouts = "not a list"  # type: ignore
        template1.merge_layouts(template2)


def test_template_copy():
    """Test copying template."""
    template = Template("Test", "test")
    template.metadata["description"] = "Test template"
    template.add_style("fonts", "default", {"font-family": "Arial"})
    template.add_layout({"margin": "2cm"})

    copy = template.copy()
    assert copy.name == template.name
    assert copy.category == template.category
    assert copy.metadata == template.metadata
    assert copy.styles == template.styles
    assert copy.layouts == template.layouts

    # Verify deep copy
    copy.metadata["description"] = "Modified"
    assert template.metadata["description"] == "Test template"


def test_template_manager_initialization(tmp_path: Path):
    """Test template manager initialization."""
    manager = TemplateManager(tmp_path)
    assert manager.template_dir == tmp_path
    assert "general" in manager.categories


def test_template_manager_categories():
    """Test template manager category operations."""
    manager = TemplateManager(Path())
    
    assert manager.add_category("test", "Test category")
    assert "test" in manager.get_categories()
    
    # Test adding duplicate category
    assert not manager.add_category("test", "Test category")
    
    # Test adding empty category
    assert not manager.add_category("", "Empty category")


def test_template_manager_save_load(tmp_path: Path):
    """Test template manager save and load operations."""
    manager = TemplateManager(tmp_path)
    manager.add_category("test")

    template = Template("Test", "test")
    template.metadata["description"] = "Test template"
    
    assert manager.save_template(template)
    loaded = manager.get_template("Test")
    assert loaded is not None
    assert loaded.name == template.name
    assert loaded.metadata["description"] == template.metadata["description"]

    # Test invalid template
    template.category = "invalid"
    assert not manager.save_template(template)


def test_template_manager_list_search(tmp_path: Path):
    """Test template manager list and search operations."""
    manager = TemplateManager(tmp_path)
    manager.add_category("test")

    template1 = Template("Test1", "test")
    template1.metadata["description"] = "First test template"
    template1.metadata["tags"] = ["test", "first"]
    
    template2 = Template("Test2", "test")
    template2.metadata["description"] = "Second test template"
    template2.metadata["tags"] = ["test", "second"]

    manager.save_template(template1)
    manager.save_template(template2)

    # Test listing
    templates = manager.list_templates()
    assert "Test1" in templates
    assert "Test2" in templates

    # Test listing by category
    templates = manager.list_templates("test")
    assert "Test1" in templates
    assert "Test2" in templates

    # Test search
    results = manager.search_templates("first")
    assert len(results) == 1
    assert results[0].name == "Test1"

    results = manager.search_templates("test")
    assert len(results) == 2

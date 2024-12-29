"""Tests for the types module."""

from datetime import datetime

from src.book_editor.types import (
    BookData,
    BookMetadata,
    DocumentData,
    DocumentMetadata,
    StyleCategory,
    TemplateData,
    TemplateMetadata,
    TemplateStyles,
)


def test_document_metadata_required():
    """Test DocumentMetadata with required fields."""
    # DocumentMetadata is total=False, so all fields are optional
    metadata: DocumentMetadata = {}
    assert isinstance(metadata, dict)
    assert len(metadata) == 0


def test_document_metadata_optional():
    """Test DocumentMetadata with optional fields."""
    metadata: DocumentMetadata = {
        "title": "Test Document",
        "author": "Test Author",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": "1.0.0",
    }
    assert isinstance(metadata, dict)
    assert metadata["title"] == "Test Document"
    assert metadata["author"] == "Test Author"
    assert "created_at" in metadata
    assert "updated_at" in metadata
    assert metadata["version"] == "1.0.0"


def test_document_metadata_partial():
    """Test DocumentMetadata with partial fields."""
    metadata: DocumentMetadata = {
        "title": "Test Document",
        "author": "Test Author",
    }
    assert isinstance(metadata, dict)
    assert metadata["title"] == "Test Document"
    assert metadata["author"] == "Test Author"
    assert "created_at" not in metadata
    assert "updated_at" not in metadata
    assert "version" not in metadata


def validate_document_data(data: dict) -> bool:
    """Validate DocumentData structure."""
    required_fields = {"title", "content", "metadata", "created_at", "updated_at", "version"}
    return all(field in data for field in required_fields)


def test_document_data_required():
    """Test DocumentData with required fields."""
    assert not validate_document_data({})
    assert not validate_document_data({"title": "Test"})

    metadata: DocumentMetadata = {}
    data: DocumentData = {
        "title": "Test Document",
        "content": "Test content",
        "metadata": metadata,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": "1.0.0",
    }
    assert isinstance(data, dict)
    assert data["title"] == "Test Document"
    assert data["content"] == "Test content"
    assert data["metadata"] == metadata
    assert "created_at" in data
    assert "updated_at" in data
    assert data["version"] == "1.0.0"


def test_template_metadata_required():
    """Test TemplateMetadata with required fields."""
    # TemplateMetadata is total=False, so all fields are optional
    metadata: TemplateMetadata = {}
    assert isinstance(metadata, dict)
    assert len(metadata) == 0


def test_template_metadata_optional():
    """Test TemplateMetadata with optional fields."""
    metadata: TemplateMetadata = {
        "name": "Test Template",
        "category": "Test Category",
        "description": "Test description",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": "1.0.0",
    }
    assert isinstance(metadata, dict)
    assert metadata["name"] == "Test Template"
    assert metadata["category"] == "Test Category"
    assert metadata["description"] == "Test description"
    assert "created_at" in metadata
    assert "updated_at" in metadata
    assert metadata["version"] == "1.0.0"


def test_template_metadata_partial():
    """Test TemplateMetadata with partial fields."""
    metadata: TemplateMetadata = {
        "name": "Test Template",
        "category": "Test Category",
    }
    assert isinstance(metadata, dict)
    assert metadata["name"] == "Test Template"
    assert metadata["category"] == "Test Category"
    assert "description" not in metadata
    assert "created_at" not in metadata
    assert "updated_at" not in metadata
    assert "version" not in metadata


def validate_template_data(data: dict) -> bool:
    """Validate TemplateData structure."""
    required_fields = {"name", "category", "content", "metadata"}
    return all(field in data for field in required_fields)


def test_template_data_required():
    """Test TemplateData with required fields."""
    assert not validate_template_data({})
    assert not validate_template_data({"name": "Test"})

    metadata: TemplateMetadata = {}
    data: TemplateData = {
        "name": "Test Template",
        "category": "Test Category",
        "content": "Test content",
        "metadata": metadata,
    }
    assert isinstance(data, dict)
    assert data["name"] == "Test Template"
    assert data["category"] == "Test Category"
    assert data["content"] == "Test content"
    assert data["metadata"] == metadata


def test_book_metadata_required():
    """Test BookMetadata with required fields."""
    # BookMetadata is total=False, so all fields are optional
    metadata: BookMetadata = {}
    assert isinstance(metadata, dict)
    assert len(metadata) == 0


def test_book_metadata_optional():
    """Test BookMetadata with optional fields."""
    metadata: BookMetadata = {
        "title": "Test Book",
        "author": "Test Author",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": "1.0.0",
        "chapters": ["Chapter 1", "Chapter 2"],
    }
    assert isinstance(metadata, dict)
    assert metadata["title"] == "Test Book"
    assert metadata["author"] == "Test Author"
    assert "created_at" in metadata
    assert "updated_at" in metadata
    assert metadata["version"] == "1.0.0"
    assert metadata["chapters"] == ["Chapter 1", "Chapter 2"]


def test_book_metadata_partial():
    """Test BookMetadata with partial fields."""
    metadata: BookMetadata = {
        "title": "Test Book",
        "chapters": ["Chapter 1"],
    }
    assert isinstance(metadata, dict)
    assert metadata["title"] == "Test Book"
    assert metadata["chapters"] == ["Chapter 1"]
    assert "author" not in metadata
    assert "created_at" not in metadata
    assert "updated_at" not in metadata
    assert "version" not in metadata


def validate_book_data(data: dict) -> bool:
    """Validate BookData structure."""
    required_fields = {"title", "content", "metadata", "chapters"}
    return all(field in data for field in required_fields)


def test_book_data_required():
    """Test BookData with required fields."""
    assert not validate_book_data({})
    assert not validate_book_data({"title": "Test"})

    metadata: BookMetadata = {}
    data: BookData = {
        "title": "Test Book",
        "content": "Test content",
        "metadata": metadata,
        "chapters": [
            {"title": "Chapter 1", "content": "Chapter 1 content"},
            {"title": "Chapter 2", "content": "Chapter 2 content"},
        ],
    }
    assert isinstance(data, dict)
    assert data["title"] == "Test Book"
    assert data["content"] == "Test content"
    assert data["metadata"] == metadata
    assert len(data["chapters"]) == 2
    assert data["chapters"][0]["title"] == "Chapter 1"
    assert data["chapters"][1]["title"] == "Chapter 2"


def test_book_data_empty_chapters():
    """Test BookData with empty chapters list."""
    metadata: BookMetadata = {}
    data: BookData = {
        "title": "Test Book",
        "content": "Test content",
        "metadata": metadata,
        "chapters": [],
    }
    assert isinstance(data, dict)
    assert data["chapters"] == []


def test_style_category_required():
    """Test StyleCategory with required fields."""
    # StyleCategory is total=False, so all fields are optional
    style: StyleCategory = {}
    assert isinstance(style, dict)
    assert len(style) == 0


def test_style_category_optional():
    """Test StyleCategory with optional fields."""
    style: StyleCategory = {
        "font_family": "Arial",
        "font_size": "16px",
        "color": "#000000",
        "background_color": "#FFFFFF",
        "border": "1px solid black",
        "margin": "10px",
        "padding": "5px",
    }
    assert isinstance(style, dict)
    assert style["font_family"] == "Arial"
    assert style["font_size"] == "16px"
    assert style["color"] == "#000000"
    assert style["background_color"] == "#FFFFFF"
    assert style["border"] == "1px solid black"
    assert style["margin"] == "10px"
    assert style["padding"] == "5px"


def test_style_category_partial():
    """Test StyleCategory with partial fields."""
    style: StyleCategory = {
        "font_family": "Arial",
        "font_size": "16px",
    }
    assert isinstance(style, dict)
    assert style["font_family"] == "Arial"
    assert style["font_size"] == "16px"
    assert "color" not in style
    assert "background_color" not in style
    assert "border" not in style
    assert "margin" not in style
    assert "padding" not in style


def validate_template_styles(data: dict) -> bool:
    """Validate TemplateStyles structure."""
    required_fields = {"borders", "colors", "fonts"}
    return all(field in data for field in required_fields)


def test_template_styles_required():
    """Test TemplateStyles with required fields."""
    assert not validate_template_styles({})
    assert not validate_template_styles({"borders": {}})

    styles: TemplateStyles = {
        "borders": {},
        "colors": {},
        "fonts": {},
    }
    assert isinstance(styles, dict)
    assert len(styles["borders"]) == 0
    assert len(styles["colors"]) == 0
    assert len(styles["fonts"]) == 0


def test_template_styles_with_data():
    """Test TemplateStyles with data."""
    styles: TemplateStyles = {
        "borders": {
            "thin": "1px solid black",
            "medium": "2px solid black",
            "thick": "3px solid black",
        },
        "colors": {
            "primary": "#0066cc",
            "secondary": "#666666",
            "background": "#FFFFFF",
        },
        "fonts": {
            "heading": "Arial",
            "body": "Times New Roman",
            "code": "Courier New",
        },
    }
    assert isinstance(styles, dict)
    assert len(styles["borders"]) == 3
    assert len(styles["colors"]) == 3
    assert len(styles["fonts"]) == 3
    assert styles["borders"]["thin"] == "1px solid black"
    assert styles["colors"]["primary"] == "#0066cc"
    assert styles["fonts"]["heading"] == "Arial"


def test_template_styles_empty_dicts():
    """Test TemplateStyles with empty dictionaries."""
    styles: TemplateStyles = {
        "borders": {},
        "colors": {},
        "fonts": {},
    }
    assert isinstance(styles, dict)
    assert isinstance(styles["borders"], dict)
    assert isinstance(styles["colors"], dict)
    assert isinstance(styles["fonts"], dict)
    assert len(styles["borders"]) == 0
    assert len(styles["colors"]) == 0
    assert len(styles["fonts"]) == 0

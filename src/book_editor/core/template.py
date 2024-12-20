"""Template management module for Book Editor.

This module provides functionality for managing document templates, including
template creation, storage, and metadata management.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.book_editor.types import (
    TemplateData,
    TemplateMetadata,
    TemplateStyles,
)

logger = logging.getLogger(__name__)

PAGE_LAYOUTS = {
    "standard": {"margins": "1in", "font_size": "12pt", "line_spacing": "1.5"},
    "manuscript": {
        "margins": "1.5in",
        "font_size": "12pt",
        "line_spacing": "2",
    },
}

VINTAGE_BORDERS = {
    "classic": "single-line",
    "ornate": "floral",
    "art_deco": "geometric",
}


class Template:
    """Template class representing a document template.

    Handles template content, metadata, and styling information.
    """

    def __init__(self, name: str, category: str = "general"):
        self.name = name
        self.category = category
        self.metadata: TemplateMetadata = {
            "description": "",
            "tags": [],
            "format": "markdown",
            "created_at": "",
            "updated_at": "",
            "word_count": 0,
        }
        self.styles: TemplateStyles = {
            "borders": {},
            "colors": {},
            "fonts": {},
        }
        self.layouts: List[Dict[str, str]] = []

    def add_style(self, style_type: str, name: str, value: str) -> None:
        """Add a style to the template."""
        if style_type in self.styles:
            self.styles[style_type][name] = value

    def add_layout(self, layout: Dict[str, str]) -> None:
        """Add a layout configuration to the template."""
        self.layouts.append(layout)

    def to_dict(self) -> TemplateData:
        """Convert template to dictionary for serialization."""
        return {
            "name": self.name,
            "category": self.category,
            "metadata": self.metadata,
            "styles": self.styles,
            "layouts": self.layouts,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Create template from dictionary."""
        # Extract or generate name and category
        name = data.get("name", data.get("title", "Untitled"))
        category = data.get("category", "general")
        template = cls(str(name), str(category))

        # Handle metadata
        if "metadata" in data:
            template.metadata.update(data["metadata"])

        # Handle styles
        if "styles" in data:
            template.styles = {
                "borders": data["styles"].get("borders", {}),
                "colors": data["styles"].get("colors", {}),
                "fonts": data["styles"].get("fonts", {}),
            }

        # Handle layouts
        if "layouts" in data:
            template.layouts = data["layouts"]
        return template


class TemplateManager:
    """Template manager class for handling template operations.

    Manages template storage, loading, and searching functionality.
    """

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.ensure_storage()
        self._categories = self._load_categories()
        # Ensure default category exists
        if not any(c["name"] == "general" for c in self._categories):
            self.add_category("general", "Default template category")

    def ensure_storage(self) -> None:
        """Ensure storage directory exists."""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        categories_file = self.templates_dir / "categories.json"
        if not categories_file.exists():
            with open(categories_file, "w", encoding="utf-8") as f:
                json.dump({"categories": []}, f)

    def _load_categories(self) -> List[Dict[str, str]]:
        """Load template categories from storage."""
        categories_file = self.templates_dir / "categories.json"
        with open(categories_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("categories", [])

    def _save_categories(self) -> None:
        """Save template categories to storage."""
        categories_file = self.templates_dir / "categories.json"
        with open(categories_file, "w", encoding="utf-8") as f:
            json.dump({"categories": self._categories}, f, indent=2)

    def add_category(self, name: str, description: str = "") -> bool:
        """Add a new template category."""
        if any(c["name"] == name for c in self._categories):
            return False
        self._categories.append({"name": name, "description": description})
        self._save_categories()
        return True

    def get_categories(self) -> List[str]:
        """Get list of template categories."""
        return [c["name"] for c in self._categories]

    def save_template(self, template: Template) -> bool:
        """Save template to storage."""
        # Check if category exists
        if template.category not in self.get_categories():
            return False
        file_path = self.templates_dir / f"{template.name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(template.to_dict(), f, indent=2)
        return True

    def _sanitize_json_content(self, content: str) -> str:
        """Remove invalid control characters from JSON content."""
        # Remove control characters except for \n, \r, \t
        return "".join(
            char for char in content if ord(char) >= 32 or char in "\n\r\t"
        )

    def load_template(self, name: str) -> Optional[Template]:
        """Load template from storage."""
        file_path = self.templates_dir / f"{name}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                sanitized = self._sanitize_json_content(content)
                data = json.loads(sanitized)
                return Template.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Error loading template %s: %s", file_path, e)
            return Template(name=name, category="general")

    def list_templates(self, category: Optional[str] = None) -> List[str]:
        """List available templates, optionally filtered by category."""
        templates = []
        for file_path in self.templates_dir.glob("*.json"):
            if file_path.stem == "categories":
                continue
            template = self.load_template(file_path.stem)
            if template and (not category or template.category == category):
                templates.append(template.name)
        return templates

    def search_templates(self, query: str) -> List[TemplateData]:
        """Search templates by name, description, or tags."""
        results = []
        query = query.lower()
        for file_path in self.templates_dir.glob("*.json"):
            if file_path.stem == "categories":
                continue
            template = self.load_template(file_path.stem)
            if template:
                template_dict = template.to_dict()
                if (
                    query in template_dict["name"].lower()
                    or query
                    in (
                        template_dict["metadata"]
                        .get("description", "")
                        .lower()
                    )
                    or any(
                        query in tag.lower()
                        for tag in template_dict["metadata"].get("tags", [])
                    )
                ):
                    results.append(template_dict)
        return results

"""Template management module for Book Editor.

This module provides functionality for managing document templates, including
template creation, storage, and metadata management.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class Template:
    """Template class representing a document template.

    Handles template content, metadata, and styling information.
    """

    def __init__(self, name: str, category: str = "general"):
        self.name = name
        self.category = category
        self.metadata = {
            "description": "",
            "tags": [],
            "format": "markdown",
        }
        self.styles = {
            "borders": {},
            "colors": {},
            "fonts": {},
        }
        self.layouts = []

    def add_style(self, style_type: str, name: str, value: str) -> None:
        """Add a style to the template."""
        if style_type in self.styles:
            self.styles[style_type][name] = value

    def add_layout(self, layout: Dict) -> None:
        """Add a layout configuration to the template."""
        self.layouts.append(layout)

    def to_dict(self) -> Dict:
        """Convert template to dictionary for serialization."""
        return {
            "name": self.name,
            "category": self.category,
            "metadata": self.metadata,
            "styles": self.styles,
            "layouts": self.layouts,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Template":
        """Create template from dictionary."""
        template = cls(data["name"], data["category"])
        template.metadata = data["metadata"]
        template.styles = data["styles"]
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

    def ensure_storage(self) -> None:
        """Ensure storage directory exists."""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        categories_file = self.templates_dir / "categories.json"
        if not categories_file.exists():
            with open(categories_file, "w", encoding="utf-8") as f:
                json.dump({"categories": []}, f)

    def _load_categories(self) -> List[Dict]:
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
        file_path = self.templates_dir / f"{template.name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(template.to_dict(), f, indent=2)
        return True

    def load_template(self, name: str) -> Optional[Template]:
        """Load template from storage."""
        file_path = self.templates_dir / f"{name}.json"
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Template.from_dict(data)

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

    def search_templates(self, query: str) -> List[Dict]:
        """Search templates by name, description, or tags."""
        results = []
        query = query.lower()
        for file_path in self.templates_dir.glob("*.json"):
            if file_path.stem == "categories":
                continue
            template = self.load_template(file_path.stem)
            if template:
                if (
                    query in template.name.lower()
                    or query in template.metadata["description"].lower()
                    or any(
                        query in tag.lower()
                        for tag in template.metadata["tags"]
                    )
                ):
                    results.append(template.to_dict())
        return results

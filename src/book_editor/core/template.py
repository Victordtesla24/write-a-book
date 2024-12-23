"""Template module for handling book templates."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import markdown

PAGE_LAYOUTS = {
    "manuscript": {
        "font-family": "Courier New",
        "font-size": "12pt",
        "line-height": "2",
        "margin": "2.54cm",
    }
}


VINTAGE_BORDERS = {
    "classic": {
        "border": "2px solid #8B4513",
        "border-radius": "8px",
        "background-color": "#FFF8DC",
    }
}


class Template:
    """Class representing a book template."""

    def __init__(self, name: str, category: str = "general"):
        """Initialize template.

        Args:
            name: Template name
            category: Template category
        """
        self.name = name
        self.category = category
        self.metadata: Dict[str, Any] = {
            "description": "",
            "tags": [],
            "format": "markdown",
        }
        self.styles: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.layouts: List[Dict[str, str]] = []

        # Add default styles and layouts
        self.add_style("borders", "classic", VINTAGE_BORDERS["classic"])
        self.add_layout(PAGE_LAYOUTS["manuscript"])

    def add_style(self, style_type: str, style_name: str, style_data: Dict[str, str]) -> None:
        """Add a style to the template.

        Args:
            style_type: Type of style (e.g. 'borders', 'fonts')
            style_name: Name of the style
            style_data: Style data
        """
        if style_type not in self.styles:
            self.styles[style_type] = {}
        if style_name not in self.styles[style_type]:
            self.styles[style_type][style_name] = {}
        self.styles[style_type][style_name].update(style_data)

    def add_layout(self, layout: Dict[str, str]) -> None:
        """Add a layout to the template.

        Args:
            layout: Layout data
        """
        self.layouts.append(layout.copy())

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary.

        Returns:
            Dictionary representation of template
        """
        return {
            "name": self.name,
            "category": self.category,
            "metadata": self.metadata.copy(),
            "styles": {k: {sk: sv.copy() for sk, sv in v.items()} for k, v in self.styles.items()},
            "layouts": [layout.copy() for layout in self.layouts],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Create template from dictionary.

        Args:
            data: Dictionary representation of template

        Returns:
            New template instance
        """
        template = cls(data["name"], data["category"])
        template.metadata = data["metadata"].copy()
        template.styles = {
            k: {sk: sv.copy() for sk, sv in v.items()} for k, v in data["styles"].items()
        }
        template.layouts = [layout.copy() for layout in data["layouts"]]
        return template

    def save(self, path: Path) -> None:
        """Save template to file.

        Args:
            path: Path to save template to
        """
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> Optional["Template"]:
        """Load template from file.

        Args:
            path: Path to load template from

        Returns:
            Loaded template or None if loading fails
        """
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (OSError, json.JSONDecodeError):
            return None

    def __getitem__(self, key: str) -> Any:
        """Get template attribute by key.

        Args:
            key: Attribute key

        Returns:
            Attribute value
        """
        if key == "name":
            return self.name
        elif key == "category":
            return self.category
        elif key == "metadata":
            return self.metadata
        elif key == "styles":
            return self.styles
        elif key == "layouts":
            return self.layouts
        raise KeyError(f"Invalid key: {key}")

    def render(self, content: str) -> str:
        """Render content using this template.

        Args:
            content: Content to render

        Returns:
            Rendered content
        """
        # Convert markdown to HTML
        html = markdown.markdown(content)

        # Apply template styling
        styled_html = f"""
<div style='border: 2px solid #8B4513; border-radius: 8px; background-color: #FFF8DC'>
<div style='font-family: Courier New; font-size: 12pt; line-height: 2; margin: 2.54cm'>
{html}
</div>
</div>"""

        return styled_html.strip()


class TemplateManager:
    """Class for managing book templates."""

    def __init__(self, template_dir: Union[str, Path]):
        """Initialize template manager.

        Args:
            template_dir: Directory for storing templates
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.categories: Set[str] = {"general"}

    def add_category(self, category: str, description: Optional[str] = None) -> bool:
        """Add a new template category.

        Args:
            category: Category name
            description: Category description

        Returns:
            True if category was added successfully
        """
        if not category:
            return False
        if category in self.categories:
            return False
        self.categories.add(category)
        return True

    def get_categories(self) -> Set[str]:
        """Get all template categories.

        Returns:
            Set of category names
        """
        return self.categories.copy()

    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name.

        Args:
            name: Template name

        Returns:
            Template instance or None if not found
        """
        template_path = self.template_dir / f"{name}.json"
        if not template_path.exists():
            return None
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                template = Template(data["name"], data["category"])
                template.metadata = data["metadata"]
                template.styles = data.get("styles", {})
                template.layouts = data.get("layouts", [])
                return template
        except (OSError, json.JSONDecodeError, KeyError) as e:
            logging.error(f"Failed to load template: {str(e)}")
            return None

    def save_template(self, template: Template) -> bool:
        """Save a template.

        Args:
            template: Template to save

        Returns:
            True if save was successful
        """
        if not template.name or not template.category:
            return False
        if template.category not in self.categories:
            return False
        template_path = self.template_dir / f"{template.name}.json"
        try:
            with open(template_path, "w", encoding="utf-8") as f:
                json.dump(template.to_dict(), f, indent=2)
            return True
        except (OSError, json.JSONDecodeError) as e:
            logging.error(f"Failed to save template: {str(e)}")
            return False

    def list_templates(self, category: Optional[str] = None) -> List[str]:
        """List all templates.

        Args:
            category: Optional category to filter by

        Returns:
            List of template names
        """
        templates = []
        for template_path in self.template_dir.glob("*.json"):
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if category is None or data["category"] == category:
                        templates.append(data["name"])
            except (OSError, json.JSONDecodeError, KeyError) as e:
                logging.error(f"Failed to load template during listing: {str(e)}")
                continue
        return templates

    def search_templates(self, query: str) -> List[Template]:
        """Search for templates.

        Args:
            query: Search query

        Returns:
            List of matching templates
        """
        query = query.lower()
        results = []
        for template_path in self.template_dir.glob("*.json"):
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metadata = data.get("metadata", {})
                    description = metadata.get("description", "").lower()
                    tags = metadata.get("tags", [])
                    if (
                        query in data["name"].lower()
                        or query in description
                        or any(query in tag.lower() for tag in tags)
                    ):
                        template = Template(data["name"], data["category"])
                        template.metadata = metadata
                        template.styles = data.get("styles", {})
                        template.layouts = data.get("layouts", [])
                        results.append(template)
            except (OSError, json.JSONDecodeError, KeyError) as e:
                logging.error(f"Failed to load template during search: {str(e)}")
                continue
        return results

    def load_template(self, name: str) -> Optional[Template]:
        """Load a template by name.

        Args:
            name: Template name

        Returns:
            Template if found, None otherwise
        """
        return self.get_template(name)

"""Template module for handling book templates."""

import copy
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

VALID_FORMATS = {"markdown", "html", "text"}


class Template:
    """Class representing a book template."""

    def __init__(self, name: str, category: str):
        """Initialize template.

        Args:
            name: Template name
            category: Template category

        Raises:
            ValueError: If name or category is empty
        """
        if not name:
            raise ValueError("Template name cannot be empty")
        if not category:
            raise ValueError("Template category cannot be empty")

        self.name = name
        self.category = category
        self.metadata = {
            "description": "",
            "tags": [],
            "format": "markdown"
        }
        self.styles = {
            "borders": {
                "classic": {
                    "border": "2px solid #8B4513",
                    "border-radius": "8px",
                    "background-color": "#FFF8DC"
                }
            },
            "fonts": {
                "default": {
                    "font-family": "Courier New",
                    "font-size": "12pt",
                    "line-height": "2",
                    "margin": "2.54cm"
                }
            }
        }
        self.layouts = [
            {
                "font-family": "Courier New",
                "font-size": "12pt",
                "line-height": "2",
                "margin": "2.54cm"
            }
        ]

    def validate(self) -> bool:
        """Validate template data.

        Returns:
            True if template is valid

        Raises:
            ValueError: If template data is invalid
        """
        if not self.name:
            raise ValueError("Template name cannot be empty")
        if not self.category:
            raise ValueError("Template category cannot be empty")
        if not isinstance(self.metadata, dict):
            raise ValueError("Template metadata must be a dictionary")
        if "format" not in self.metadata:
            raise ValueError("Template metadata must include format")
        if self.metadata["format"] not in VALID_FORMATS:
            raise ValueError(f"Invalid format: {self.metadata['format']}")
        if not isinstance(self.metadata.get("tags", []), list):
            raise ValueError("Template tags must be a list")
        if not isinstance(self.styles, dict):
            raise ValueError("Template styles must be a dictionary")
        if not isinstance(self.layouts, list):
            raise ValueError("Template layouts must be a list")
        return True

    def add_style(
        self, style_type: str, style_name: str, style_data: Dict[str, str]
    ) -> None:
        """Add a style to the template.

        Args:
            style_type: Type of style (e.g. 'borders', 'fonts')
            style_name: Name of the style
            style_data: Style data

        Raises:
            ValueError: If style data is invalid
        """
        if not style_type:
            raise ValueError("Style type cannot be empty")
        if not style_name:
            raise ValueError("Style name cannot be empty")
        if not isinstance(style_data, dict):
            raise ValueError("Style data must be a dictionary")

        if style_type not in self.styles:
            self.styles[style_type] = {}
        if style_name not in self.styles[style_type]:
            self.styles[style_type][style_name] = {}
        self.styles[style_type][style_name].update(style_data)

    def add_layout(self, layout: Dict[str, str]) -> None:
        """Add a layout to the template.

        Args:
            layout: Layout data

        Raises:
            ValueError: If layout data is invalid
        """
        if not isinstance(layout, dict):
            raise ValueError("Layout must be a dictionary")
        if not layout:
            raise ValueError("Layout cannot be empty")
        self.layouts.append(layout.copy())

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary.

        Returns:
            Dictionary representation of template

        Raises:
            ValueError: If template data is invalid
        """
        self.validate()
        return {
            "name": self.name,
            "category": self.category,
            "metadata": self.metadata.copy(),
            "styles": {
                k: {sk: sv.copy() for sk, sv in v.items()}
                for k, v in self.styles.items()
            },
            "layouts": [layout.copy() for layout in self.layouts],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Create template from dictionary.

        Args:
            data: Dictionary representation of template

        Returns:
            New template instance

        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Template data must be a dictionary")
        if "name" not in data:
            raise ValueError("Template data must include name")
        if "category" not in data:
            raise ValueError("Template data must include category")

        template = cls(data["name"], data["category"])
        if "metadata" in data:
            template.metadata = data["metadata"].copy()
        if "styles" in data:
            template.styles = {
                k: {sk: sv.copy() for sk, sv in v.items()}
                for k, v in data["styles"].items()
            }
        if "layouts" in data:
            template.layouts = [layout.copy() for layout in data["layouts"]]

        template.validate()
        return template

    def save(self, path: Path) -> None:
        """Save template to file.

        Args:
            path: Path to save template to

        Raises:
            ValueError: If template data is invalid
            OSError: If file cannot be written
        """
        self.validate()
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> Optional["Template"]:
        """Load template from file.

        Args:
            path: Path to load template from

        Returns:
            Loaded template or None if loading fails

        Raises:
            OSError: If file cannot be read
            ValueError: If template data is invalid
        """
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            template = cls.from_dict(data)
            template.validate()
            return template
        except (OSError, json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to load template: {str(e)}")
            return None

    def __getitem__(self, key: str) -> Any:
        """Get template attribute by key.

        Args:
            key: Attribute key

        Returns:
            Attribute value

        Raises:
            KeyError: If key is invalid
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
        """Render content with template.

        Args:
            content: Content to render

        Returns:
            Rendered content

        Raises:
            ValueError: If content is empty or format is invalid
        """
        if not content:
            raise ValueError("Content cannot be empty")

        # Convert content based on format
        if self.metadata["format"] == "markdown":
            html_content = markdown.markdown(content)
        elif self.metadata["format"] == "html":
            html_content = content
        elif self.metadata["format"] == "text":
            html_content = f"<pre>{content}</pre>"
        else:
            raise ValueError(f"Invalid format: {self.metadata['format']}")

        # Build style strings
        border_style = self._build_border_style()
        content_style = self._build_content_style()

        # Build final HTML
        return (
            f"<div style='{border_style}'>\n"
            f"<div style='{content_style}'>\n"
            f"{html_content}\n"
            "</div>\n"
            "</div>"
        )

    def _build_border_style(self) -> str:
        """Build border style string.

        Returns:
            Style string
        """
        styles = []
        if "borders" in self.styles:
            for style_name, style_data in self.styles["borders"].items():
                styles.extend(f"{k}: {v}" for k, v in style_data.items())
        return "; ".join(styles)

    def _build_content_style(self) -> str:
        """Build content style string.

        Returns:
            Style string
        """
        styles = []
        # Add font styles
        if "fonts" in self.styles:
            for style_name, style_data in self.styles["fonts"].items():
                styles.extend(f"{k}: {v}" for k, v in style_data.items())
        # Add text styles
        if "text" in self.styles:
            for style_name, style_data in self.styles["text"].items():
                styles.extend(f"{k}: {v}" for k, v in style_data.items())
        # Add background styles
        if "background" in self.styles:
            for style_name, style_data in self.styles["background"].items():
                styles.extend(f"{k}: {v}" for k, v in style_data.items())
        # Add layout styles
        for layout in self.layouts:
            styles.extend(f"{k}: {v}" for k, v in layout.items())
        return "; ".join(styles)

    def merge_styles(self, source: "Template") -> None:
        """Merge styles from source template.

        Args:
            source: Source template

        Raises:
            ValueError: If source is invalid
        """
        if source is None:
            raise ValueError("Source template cannot be None")
        if not isinstance(source.styles, dict):
            raise ValueError("Source template styles must be a dictionary")

        for style_type, styles in source.styles.items():
            if style_type not in self.styles:
                self.styles[style_type] = {}
            self.styles[style_type].update(styles)

    def merge_layouts(self, source: "Template") -> None:
        """Merge layouts from source template.

        Args:
            source: Source template

        Raises:
            ValueError: If source is invalid
        """
        if source is None:
            raise ValueError("Source template cannot be None")
        if not isinstance(source.layouts, list):
            raise ValueError("Source template layouts must be a list")

        # Keep existing layouts and add source layouts
        self.layouts.extend(copy.deepcopy(source.layouts))

    def merge(self, source: "Template") -> None:
        """Merge source template into this template.

        Args:
            source: Source template

        Raises:
            ValueError: If source is invalid
        """
        if source is None:
            raise ValueError("Source template cannot be None")

        self.metadata.update(source.metadata)
        self.merge_styles(source)
        self.merge_layouts(source)

    def copy(self) -> "Template":
        """Create a deep copy of the template.

        Returns:
            Copy of template
        """
        template = Template(self.name, self.category)
        template.metadata = copy.deepcopy(self.metadata)
        template.styles = copy.deepcopy(self.styles)
        template.layouts = copy.deepcopy(self.layouts)
        return template

    def validate_metadata(self) -> bool:
        """Validate template metadata.

        Returns:
            True if metadata is valid

        Raises:
            ValueError: If metadata is invalid
        """
        if "format" not in self.metadata:
            raise ValueError("Template metadata must include format")
        if self.metadata["format"] not in VALID_FORMATS:
            raise ValueError(f"Invalid format: {self.metadata['format']}")
        if not isinstance(self.metadata["tags"], list):
            raise ValueError("Template tags must be a list")
        if not all(isinstance(tag, str) for tag in self.metadata["tags"]):
            raise ValueError("Template tags must be strings")
        if not isinstance(self.metadata["description"], str):
            raise ValueError("Template description must be a string")
        return True

    def validate_styles(self) -> bool:
        """Validate template styles.

        Returns:
            True if styles are valid

        Raises:
            ValueError: If styles are invalid
        """
        if not isinstance(self.styles, dict):
            raise ValueError("Template styles must be a dictionary")
        for category in self.styles.values():
            if not isinstance(category, dict):
                raise ValueError("Style category must be a dictionary")
            for style in category.values():
                if not isinstance(style, dict):
                    raise ValueError("Style properties must be a dictionary")
        return True

    def validate_layouts(self) -> bool:
        """Validate template layouts.

        Returns:
            True if layouts are valid

        Raises:
            ValueError: If layouts are invalid
        """
        if not isinstance(self.layouts, list):
            raise ValueError("Template layouts must be a list")
        for layout in self.layouts:
            if not isinstance(layout, dict):
                raise ValueError("Layout must be a dictionary")
            if not layout:
                raise ValueError("Layout cannot be empty")
        return True


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

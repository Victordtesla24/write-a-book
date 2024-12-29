"""# Template Manager Module

Provides functionality for managing book templates, including saving, loading,
and validating templates."""

import json
import re
from pathlib import Path
from typing import List, Optional, Union

from .template import Template

# Windows reserved filenames
RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
}

# Maximum filename length (common filesystem limit)
MAX_FILENAME_LENGTH = 255


class TemplateManager:
    """Manages templates for the book editor."""

    def __init__(self, template_dir: Union[str, Path]):
        """Initialize template manager.

        Args:
            template_dir: Path to template directory

        Raises:
            ValueError: If template directory path is empty
        """
        if not template_dir:
            raise ValueError("Template directory path cannot be empty")

        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename to be safe for filesystem.

        Args:
            name: Original filename

        Returns:
            Sanitized filename

        Raises:
            ValueError: If filename is invalid or empty
        """
        if not name or name.isspace():
            raise ValueError("Template name cannot be empty")

        # Handle dots-only names
        if name.strip('.') == '':
            raise ValueError("Invalid template name")

        # Remove leading/trailing whitespace
        name = name.strip()

        # Replace invalid characters with underscore
        sanitized = re.sub(r'[\x00-\x1f\x7f/\\:*?"<>|]', '_', name)

        # Handle special characters and spaces
        parts = re.split(r'[/\\:*\s]+', sanitized)
        sanitized = '_'.join(part.strip() for part in parts if part.strip())

        # Replace dots with underscores (except extension)
        sanitized = re.sub(r'\.(?!json$)', '_', sanitized)

        # Replace multiple underscores with single underscore
        sanitized = re.sub(r'_+', '_', sanitized)

        # Remove leading/trailing dots and underscores
        sanitized = sanitized.strip('._')

        # Handle reserved names
        if sanitized.upper() in RESERVED_NAMES:
            sanitized = f"{sanitized}_"

        # Truncate if too long (leaving room for .json extension)
        max_base_length = MAX_FILENAME_LENGTH - 6  # 5 for ".json" + 1 for safety
        if len(sanitized) > max_base_length:
            # First try truncating at a word boundary
            sanitized = sanitized[:max_base_length]
            last_underscore = sanitized.rfind('_')
            if last_underscore > max_base_length // 2:  # Only truncate at underscore if reasonable
                sanitized = sanitized[:last_underscore]
            else:  # Otherwise just truncate to ensure we're under the limit
                sanitized = sanitized[:max_base_length - 10]  # Extra safety margin

        if not sanitized:
            raise ValueError("Invalid template name")

        return sanitized

    def save_template(self, template: Template) -> Path:
        """Save template to file.

        Args:
            template: Template to save

        Returns:
            Path to saved template file

        Raises:
            ValueError: If template is invalid
        """
        template.validate()

        sanitized_name = self._sanitize_filename(template.name)
        path = self.template_dir / f"{sanitized_name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w") as f:
            json.dump(template.to_dict(), f, indent=2)

        return path

    def load_template(self, path: Union[str, Path]) -> Optional[Template]:
        """Load template from file.

        Args:
            path: Path to template file

        Returns:
            Loaded template or None if file doesn't exist or is invalid
        """
        path = Path(path)
        if not path.exists():
            return None

        try:
            with path.open() as f:
                data = json.load(f)
            return Template.from_dict(data)
        except (json.JSONDecodeError, ValueError):
            return None

    def get_template(self, name: str) -> Optional[Template]:
        """Get template by name.

        Args:
            name: Template name

        Returns:
            Template or None if not found
        """
        if not name:
            return None

        path = self.template_dir / f"{name.replace(' ', '_')}.json"
        return self.load_template(path)

    def list_templates(self, category: Optional[str] = None) -> List[Template]:
        """List all templates.

        Args:
            category: Optional category to filter by

        Returns:
            List of templates
        """
        templates = []
        for path in self.template_dir.glob("*.json"):
            template = self.load_template(path)
            if template is not None:
                if category is None or template.category == category:
                    templates.append(template)
        return templates

    def delete_template(self, name: str) -> bool:
        """Delete template.

        Args:
            name: Template name

        Returns:
            True if template was deleted, False otherwise
        """
        if not name:
            return False

        path = self.template_dir / f"{name.replace(' ', '_')}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def list_categories(self) -> List[str]:
        """List all template categories.

        Returns:
            List of category names
        """
        categories = set()
        for template in self.list_templates():
            categories.add(template.category)
        return sorted(list(categories))

    def validate_template_name(self, name: str) -> bool:
        """Validate template name.

        Args:
            name: Template name

        Returns:
            True if name is valid, False otherwise
        """
        if not name or name.isspace():
            return False

        # Check for invalid characters
        if re.search(r'[/\\:*?"<>|]', name):
            return False

        # Check for dots-only names
        if name.strip('.') == '':
            return False

        return True

    def validate_category_name(self, name: str) -> bool:
        """Validate category name.

        Args:
            name: Category name

        Returns:
            True if name is valid, False otherwise
        """
        if not name or name.isspace():
            return False
        return True

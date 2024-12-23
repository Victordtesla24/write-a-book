"""Template manager module."""

from pathlib import Path
from typing import Dict, List, Optional, Union

from src.book_editor.core.template import Template


class TemplateManager:
    """Manages template storage and retrieval."""

    def __init__(self, template_dir: Union[str, Path]):
        """Initialize template manager.

        Args:
            template_dir: Directory for storing templates
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def save_template(self, template: Template, path: Optional[Union[str, Path]] = None) -> bool:
        """Save a template to storage.

        Args:
            template: Template to save
            path: Path to save template to. If None, uses template name

        Returns:
            True if save was successful
        """
        try:
            if not template.name:
                return False

            if path is None:
                path = self.template_dir / f"{template.name}.json"
            elif isinstance(path, str):
                path = self.template_dir / path
            else:
                path = Path(path)

            path.parent.mkdir(parents=True, exist_ok=True)
            template.save(path)
            return True
        except (OSError, ValueError) as e:
            print(f"Error saving template: {e}")
            return False

    def load_template(self, path: Union[str, Path]) -> Optional[Template]:
        """Load a template from storage.

        Args:
            path: Path to load template from

        Returns:
            Loaded template or None if loading fails
        """
        try:
            if isinstance(path, str):
                path = self.template_dir / path
            else:
                path = Path(path)

            return Template.load(path)
        except (OSError, ValueError) as e:
            print(f"Error loading template: {e}")
            return None

    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name.

        Args:
            name: Template name

        Returns:
            Template instance or None if not found
        """
        path = self.template_dir / f"{name}.json"
        return self.load_template(path)

    def list_templates(self) -> List[Dict[str, str]]:
        """List all templates in storage.

        Returns:
            List of template metadata dictionaries
        """
        templates = []
        for path in self.template_dir.glob("*.json"):
            try:
                template = Template.load(path)
                if template:
                    metadata = {
                        "name": template.name,
                        "category": template.category,
                        "path": str(path.relative_to(self.template_dir)),
                    }
                    templates.append(metadata)
            except (OSError, ValueError) as e:
                print(f"Error loading template {path}: {e}")
        return templates

    def delete_template(self, path: Union[str, Path]) -> bool:
        """Delete a template from storage.

        Args:
            path: Path to template to delete

        Returns:
            True if deletion was successful
        """
        try:
            if isinstance(path, str):
                path = self.template_dir / path
            else:
                path = Path(path)

            if path.exists():
                path.unlink()
                return True
            return False
        except (OSError, ValueError) as e:
            print(f"Error deleting template: {e}")
            return False

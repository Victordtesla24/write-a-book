"""Core editor functionality for the application."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import markdown
import streamlit as st

from src.book_editor.app.config.settings import STORAGE_DIR, TEMPLATE_DIR
from src.book_editor.core.editor import Document
from src.book_editor.core.template import Template
from src.book_editor.types import TemplateData, TemplateStyles
from src.data.storage import StorageManager

logger = logging.getLogger(__name__)


def is_template_data(data: Any) -> bool:
    """Check if data matches template data structure."""
    return (
        isinstance(data, dict)
        and isinstance(data.get("name"), str)
        and isinstance(data.get("category"), str)
        and isinstance(data.get("metadata"), dict)
        and isinstance(data.get("styles"), dict)
        and isinstance(data.get("layouts"), list)
        and all(isinstance(x, dict) for x in data.get("layouts", []))
    )


def merge_style_dicts(styles: TemplateStyles) -> Dict[str, str]:
    """Merge style category dictionaries into a flat dictionary."""
    result: Dict[str, str] = {}
    for category in ["borders", "colors", "fonts"]:
        category_dict = styles.get(category, {})
        if isinstance(category_dict, dict):
            result.update(category_dict)
    return result


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, o: Any) -> str:
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(o)


class DocumentManager:
    """Document manager for handling document operations."""

    def __init__(self):
        self.storage_dir = Path(STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.documents: Dict[str, Document] = {}

    def create_document(self, title: str, content: str = "") -> Document:
        """Create a new document."""
        if title is None:
            raise ValueError("Document title cannot be None")
        if not title:
            raise ValueError("Document title cannot be empty")

        document = Document(title=title, content=content)
        self.documents[title] = document
        return document

    def save_document(self, doc: Document) -> bool:
        """Save document to storage."""
        try:
            self.documents[doc.title] = doc
            file_path = self.storage_dir / f"{doc.title}.json"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(doc.to_dict(), f, indent=2, cls=DateTimeEncoder)
            return True
        except (IOError, json.JSONDecodeError) as e:
            logger.error("Failed to save document: %s", e)
            return False

    def get_document(self, title: str) -> Optional[Document]:
        """Get document by title."""
        return self.documents.get(title)

    def delete_document(self, title: str) -> bool:
        """Delete document by title."""
        if title in self.documents:
            del self.documents[title]
            file_path = self.storage_dir / f"{title}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        return False

    def list_documents(self) -> List[Document]:
        """List all documents."""
        return list(self.documents.values())


class TemplateRenderer:
    """Handles template rendering and management."""

    def __init__(self, storage_dir: str):
        """Initialize template renderer."""
        self.storage = StorageManager(Path(storage_dir))
        self.storage.root_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, TemplateData] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load templates from storage."""
        try:
            template_files = self.storage.list_directory()
            for file_name in template_files:
                if not file_name.endswith(".json"):
                    continue

                file_data = self.storage.load_file(file_name, as_json=True)
                if not isinstance(file_data, dict):
                    continue

                data = cast(Dict[str, Any], file_data)
                if is_template_data(data):
                    self.templates[data["name"]] = cast(TemplateData, data)

        except (IOError, json.JSONDecodeError) as e:
            logger.error("Failed to load templates: %s", e)

    def create_template(
        self, name: str, template_type: str = "general"
    ) -> Template:
        """Create a new template."""
        template = Template(name, template_type)
        self.save_template(template)
        return template

    def save_template(self, template: Template) -> None:
        """Save template to storage."""
        try:
            template_path = self.storage.root_dir / f"{template.name}.json"
            template_data = template.to_dict()
            with open(template_path, "w", encoding="utf-8") as f:
                json.dump(template_data, f, indent=2)
            if is_template_data(template_data):
                self.templates[template.name] = cast(
                    TemplateData, template_data
                )
        except (IOError, json.JSONDecodeError) as e:
            logger.error("Failed to save template: %s", e)
            raise

    def load_template(self, name: str) -> Optional[Template]:
        """Load template from storage."""
        try:
            template_path = self.storage.root_dir / f"{name}.json"
            if not template_path.exists():
                msg = f"Failed to load template: File not found: {name}.json"
                logger.error(msg)
                return None

            with open(template_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not is_template_data(data):
                return None

            template = Template(data["name"], data["category"])
            template.metadata = data.get("metadata", template.metadata)
            template.styles = cast(
                TemplateStyles, data.get("styles", template.styles)
            )
            template.layouts = data.get("layouts", template.layouts)
            return template

        except (IOError, json.JSONDecodeError) as e:
            logger.error("Failed to load template: %s", e)
            return None

    def delete_template(self, name: str) -> bool:
        """Delete template from storage."""
        try:
            self.storage.delete_file(f"{name}.json")
            if name in self.templates:
                del self.templates[name]
            return True
        except IOError as e:
            logger.error("Failed to delete template: %s", e)
            return False

    def list_templates(self) -> List[str]:
        """List available templates."""
        return list(self.templates.keys())

    def customize_template(self, name: str, styles: Dict[str, str]) -> bool:
        """Customize template styles."""
        if not name:
            raise ValueError("Template name cannot be empty")
        if styles is None:
            raise ValueError("Styles cannot be None")

        template = self.load_template(name)
        if not template:
            return False

        template.metadata = template.metadata or {}
        template.styles = template.styles or {
            "borders": {},
            "colors": {},
            "fonts": {},
        }

        # Add styles to appropriate category
        for key, value in styles.items():
            category = "fonts"  # Default category
            if "color" in key:
                category = "colors"
            elif "border" in key:
                category = "borders"
            if category in template.styles:
                template.styles[category][key] = value

        try:
            self.save_template(template)
            return True
        except (IOError, json.JSONDecodeError) as e:
            logger.error("Failed to customize template: %s", e)
            return False

    def render_content(self, content: str) -> str:
        """Render content using markdown."""
        html = markdown.markdown(content, extensions=["fenced_code", "tables"])
        return html

    def render_template(self, template_name: str, content: str) -> str:
        """Render content using template."""
        template = self.load_template(template_name)
        if not template:
            return content

        try:
            html_content = markdown.markdown(content)
            flat_styles = merge_style_dicts(template.styles)
            style_str = "; ".join(f"{k}: {v}" for k, v in flat_styles.items())
            return f'<div style="{style_str}">{html_content}</div>'
        except (ValueError, TypeError) as e:
            logger.error("Failed to render template: %s", e)
            return content


class PreviewManager:
    """Preview manager for handling document previews."""

    def __init__(self, template_renderer: Optional[TemplateRenderer] = None):
        """Initialize preview manager.

        Args:
            template_renderer: Optional TemplateRenderer instance. If not provided,
                             creates a new instance using TEMPLATE_DIR.
        """
        self.cache: Dict[str, str] = {}
        self.template_renderer = template_renderer or TemplateRenderer(
            TEMPLATE_DIR
        )

    def generate_preview(self, content: str) -> str:
        """Generate preview for content."""
        if content is None:
            raise ValueError("Content cannot be None")
        if content in self.cache:
            return self.cache[content]

        preview = self.template_renderer.render_content(content)
        self.cache_preview(content, preview)
        return preview

    def apply_styles(self, preview: str, styles: Dict[str, str]) -> str:
        """Apply styles to preview."""
        if not styles:
            raise ValueError("Styles cannot be empty")
        style_str = "; ".join(f"{k}: {v}" for k, v in styles.items())
        return f'<div style="{style_str}">{preview}</div>'

    def cache_preview(self, content: str, preview: str) -> None:
        """Cache preview for content."""
        if not content or not preview:
            raise ValueError("Content and preview cannot be empty")
        self.cache[content] = preview

    def get_cached_preview(self, content: str) -> Optional[str]:
        """Get cached preview for content."""
        return self.cache.get(content)


class AppEditor:
    """Main editor class for the application."""

    def __init__(self):
        self.document_manager = DocumentManager()
        self.template_renderer = TemplateRenderer(TEMPLATE_DIR)
        self.preview_manager = PreviewManager(self.template_renderer)
        self.current_document: Optional[Document] = None
        self.current_template: Optional[str] = None

    def create_document(self, title: str) -> Document:
        """Create a new document."""
        if title is None:
            raise ValueError("Document title cannot be None")
        if not title:
            raise ValueError("Document title cannot be empty")

        document = Document(title=title)
        self.current_document = document
        return document

    def update_content(self, content: str) -> None:
        """Update current document content."""
        if content is None:
            raise ValueError("Content cannot be None")
        if self.current_document:
            self.current_document.update_content(content)

    def save_document(self) -> bool:
        """Save current document."""
        if self.current_document:
            return self.document_manager.save_document(self.current_document)
        return False

    def select_template(self, name: str) -> None:
        """Select template by name."""
        if not name:
            raise ValueError("Template name cannot be empty")
        self.current_template = name

    def customize_template(self, styles: Dict[str, str]) -> None:
        """Customize current template."""
        if styles is None:
            raise ValueError("Styles cannot be None")
        if self.current_template:
            self.template_renderer.customize_template(
                self.current_template, styles
            )

    def update_preview(self) -> str:
        """Update and return preview for current document."""
        if self.current_document:
            content = self.current_document.content
            st.markdown(content)
            return content
        return ""

    def preview_template(self, name: str) -> Optional[Template]:
        """Preview template by name."""
        return self.template_renderer.load_template(name)

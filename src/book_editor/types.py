"""Type definitions for the book editor."""

from typing import Dict, List, TypedDict


class TemplateMetadata(TypedDict, total=False):
    """Template metadata type definition."""

    description: str
    tags: List[str]
    format: str
    created_at: str
    updated_at: str
    word_count: int


class StyleCategory(TypedDict, total=False):
    """Style category type definition."""

    font_family: str
    font_size: str
    color: str
    background_color: str
    border: str
    margin: str
    padding: str


class TemplateStyles(TypedDict):
    """Template styles type definition."""

    borders: Dict[str, str]
    colors: Dict[str, str]
    fonts: Dict[str, str]


class TemplateData(TypedDict):
    """Template data definition."""

    name: str  # Required
    category: str  # Required
    metadata: TemplateMetadata  # Required but fields within are optional
    styles: TemplateStyles  # Required
    layouts: List[Dict[str, str]]  # Required


class DocumentData(TypedDict):
    """Document data type definition."""

    title: str
    content: str
    metadata: Dict[str, str]
    created_at: str
    updated_at: str
    version: str

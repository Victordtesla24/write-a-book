"""Type definitions for the book editor."""

from typing import Any, Dict, List, TypedDict


class DocumentMetadata(TypedDict, total=False):
    """Document metadata type."""

    title: str
    author: str
    created_at: str
    updated_at: str
    version: str


class DocumentData(TypedDict):
    """Document data type."""

    title: str
    content: str
    metadata: DocumentMetadata
    created_at: str
    updated_at: str
    version: str


class TemplateMetadata(TypedDict, total=False):
    """Template metadata type."""

    name: str
    category: str
    description: str
    created_at: str
    updated_at: str
    version: str


class TemplateData(TypedDict):
    """Template data type."""

    name: str
    category: str
    content: str
    metadata: TemplateMetadata


class BookMetadata(TypedDict, total=False):
    """Book metadata type."""

    title: str
    author: str
    created_at: str
    updated_at: str
    version: str
    chapters: List[str]


class BookData(TypedDict):
    """Book data type."""

    title: str
    content: str
    metadata: BookMetadata
    chapters: List[Dict[str, Any]]


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

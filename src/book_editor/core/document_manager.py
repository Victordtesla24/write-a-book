"""Document manager module."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from src.book_editor.core.document import Document


class DocumentManager:
    """Manages document storage and retrieval."""

    def __init__(self, storage_dir: Union[str, Path]):
        """Initialize document manager.

        Args:
            storage_dir: Directory for storing documents
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_document(self, document: Document) -> str:
        """Save a document to storage.

        Args:
            document: Document to save

        Returns:
            Document ID (filename without extension)

        Raises:
            ValueError: If document is invalid
        """
        try:
            # Generate document ID from title
            doc_id = document.metadata["title"].lower().replace(" ", "-")
            path = self.storage_dir / f"{doc_id}.json"
            
            # Save the document
            document.save(path)
            return doc_id
        except Exception as e:
            raise ValueError(f"Failed to save document: {e}")

    def load_document(self, doc_id: str) -> Document:
        """Load a document from storage.

        Args:
            doc_id: Document ID to load

        Returns:
            Loaded document

        Raises:
            ValueError: If document doesn't exist
        """
        try:
            path = self.storage_dir / f"{doc_id}.json"
            if not path.exists():
                raise ValueError(f"Document {doc_id} does not exist")
            
            doc = Document.load(path)
            if doc is None:
                raise ValueError(f"Failed to load document {doc_id}")
            return doc
        except Exception as e:
            raise ValueError(f"Failed to load document: {e}")

    def delete_document(self, doc_id: str) -> None:
        """Delete a document from storage.

        Args:
            doc_id: Document ID to delete

        Raises:
            ValueError: If document doesn't exist
        """
        path = self.storage_dir / f"{doc_id}.json"
        if not path.exists():
            raise ValueError(f"Document {doc_id} does not exist")
        path.unlink()

    def list_documents(self) -> List[Dict[str, str]]:
        """List all documents in storage.

        Returns:
            List of document metadata dictionaries
        """
        documents = []
        for path in self.storage_dir.glob("*.json"):
            try:
                doc = Document.load(path)
                if doc:
                    metadata = doc.metadata.copy()
                    metadata["id"] = path.stem
                    metadata["content"] = doc.content
                    documents.append(metadata)
            except Exception:
                continue
        return documents

    def update_document(self, doc_id: str, document: Document) -> None:
        """Update an existing document.

        Args:
            doc_id: Document ID to update
            document: New document content

        Raises:
            ValueError: If document doesn't exist
        """
        path = self.storage_dir / f"{doc_id}.json"
        if not path.exists():
            raise ValueError(f"Document {doc_id} does not exist")
        document.save(path)

    def search_documents(self, query: str) -> List[Dict[str, str]]:
        """Search documents by title or content.

        Args:
            query: Search query

        Returns:
            List of matching document metadata
        """
        results = []
        query = query.lower()
        for doc_info in self.list_documents():
            if (query in doc_info["title"].lower() or
                    query in doc_info["content"].lower()):
                results.append(doc_info)
        return results

    def get_document_metadata(self, doc_id: str) -> Dict[str, str]:
        """Get document metadata.

        Args:
            doc_id: Document ID

        Returns:
            Document metadata

        Raises:
            ValueError: If document doesn't exist
        """
        doc = self.load_document(doc_id)
        metadata = doc.metadata.copy()
        metadata["id"] = doc_id
        return metadata

    def _validate_document_id(self, doc_id: str) -> bool:
        """Validate document ID format.

        Args:
            doc_id: Document ID to validate

        Returns:
            True if valid, False otherwise
        """
        return bool(re.match(r'^[a-z0-9-]+$', doc_id))

    def backup_document(self, doc_id: str) -> Path:
        """Create a backup of a document.

        Args:
            doc_id: Document ID to backup

        Returns:
            Path to backup file

        Raises:
            ValueError: If document doesn't exist
        """
        doc = self.load_document(doc_id)
        backup_path = self.storage_dir / f"{doc_id}.backup.json"
        doc.save(backup_path)
        return backup_path

    def restore_document(self, doc_id: str, backup_path: Path) -> Document:
        """Restore a document from backup.

        Args:
            doc_id: Document ID to restore
            backup_path: Path to backup file

        Returns:
            Restored document

        Raises:
            ValueError: If backup is invalid
        """
        try:
            doc = Document.load(backup_path)
            if doc is None:
                raise ValueError("Invalid backup file")
            self.update_document(doc_id, doc)
            return doc
        except Exception as e:
            raise ValueError(f"Failed to restore document: {e}")

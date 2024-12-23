"""Document manager module."""

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

    def save_document(self, document: Document, path: Optional[Union[str, Path]] = None) -> bool:
        """Save a document to storage.

        Args:
            document: Document to save
            path: Path to save document to. If None, uses document title

        Returns:
            True if save was successful
        """
        try:
            if path is None:
                title = document.get_metadata()["title"]
                path = self.storage_dir / f"{title}.json"
            elif isinstance(path, str):
                path = self.storage_dir / path
            else:
                path = Path(path)

            path.parent.mkdir(parents=True, exist_ok=True)
            document.save(path)
            return True
        except (OSError, ValueError) as e:
            print(f"Error saving document: {e}")
            return False

    def load_document(self, path: Union[str, Path]) -> Optional[Document]:
        """Load a document from storage.

        Args:
            path: Path to load document from

        Returns:
            Loaded document or None if loading fails
        """
        try:
            if isinstance(path, str):
                path = self.storage_dir / path
            else:
                path = Path(path)

            return Document.load(path)
        except (OSError, ValueError) as e:
            print(f"Error loading document: {e}")
            return None

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
                    metadata = doc.get_metadata()
                    metadata["path"] = str(path.relative_to(self.storage_dir))
                    documents.append(metadata)
            except (OSError, ValueError) as e:
                print(f"Error loading document {path}: {e}")
        return documents

    def delete_document(self, path: Union[str, Path]) -> bool:
        """Delete a document from storage.

        Args:
            path: Path to document to delete

        Returns:
            True if deletion was successful
        """
        try:
            if isinstance(path, str):
                path = self.storage_dir / path
            else:
                path = Path(path)

            if path.exists():
                path.unlink()
                return True
            return False
        except (OSError, ValueError) as e:
            print(f"Error deleting document: {e}")
            return False

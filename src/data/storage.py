"""Storage management module for handling file operations."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union


class StorageManager:
    """Manages file storage operations."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def save_file(
        self, relative_path: str, content: Union[str, Dict[str, Any]]
    ) -> None:
        """Save content to a file."""
        file_path = self.root_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, dict):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def load_file(
        self, relative_path: str, as_json: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """Load content from a file."""
        file_path = self.root_dir / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            if as_json:
                return json.load(f)
            return f.read()

    def delete_file(self, relative_path: str) -> None:
        """Delete a file."""
        file_path = self.root_dir / relative_path
        if file_path.exists():
            file_path.unlink()

    def create_directory(self, relative_path: str) -> None:
        """Create a directory."""
        dir_path = self.root_dir / relative_path
        if "/" in relative_path and not dir_path.parent.exists():
            raise ValueError("Parent directory does not exist")
        dir_path.mkdir(parents=False, exist_ok=True)

    def list_directory(self, relative_path: str = "") -> List[str]:
        """List contents of a directory."""
        dir_path = self.root_dir / relative_path
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        return [item.name for item in dir_path.iterdir()]

    def create_backup(self, relative_path: str) -> str:
        """Create a backup of a file."""
        source_path = self.root_dir / relative_path
        if not source_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source_path.name}.backup_{timestamp}"
        backup_path = source_path.parent / backup_name
        shutil.copy2(source_path, backup_path)

        return backup_path.name

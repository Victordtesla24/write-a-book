# pylint: disable=redefined-outer-name
"""Test module for storage functionality."""

import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest  # pylint: disable=import-error

from src.data.storage import StorageManager


@pytest.fixture
def temp_storage() -> Generator[StorageManager, None, None]:
    """Create a temporary storage directory for testing."""
    temp_dir = tempfile.mkdtemp()
    storage = StorageManager(Path(temp_dir))
    yield storage
    shutil.rmtree(temp_dir)


def test_storage_initialization(temp_storage: StorageManager) -> None:
    """Test storage manager initialization."""
    assert temp_storage.root_dir.exists()
    assert temp_storage.root_dir.is_dir()


def test_file_operations(temp_storage: StorageManager) -> None:
    """Test basic file operations."""
    # Test save
    content = "Test content"
    temp_storage.save_file("test.txt", content)
    assert (temp_storage.root_dir / "test.txt").exists()

    # Test save with JSON content
    json_content = {"key": "value"}
    temp_storage.save_file("test.json", json_content)
    assert (temp_storage.root_dir / "test.json").exists()

    # Test load
    loaded_content = temp_storage.load_file("test.txt")
    assert loaded_content == content

    # Test load JSON
    loaded_json = temp_storage.load_file("test.json", as_json=True)
    assert loaded_json == json_content

    # Test delete
    temp_storage.delete_file("test.txt")
    assert not (temp_storage.root_dir / "test.txt").exists()

    # Test delete non-existent file
    temp_storage.delete_file("nonexistent.txt")  # Should not raise error


def test_directory_operations(temp_storage: StorageManager) -> None:
    """Test directory operations."""
    # Create directory
    temp_storage.create_directory("test_dir")
    dir_path = temp_storage.root_dir / "test_dir"
    assert dir_path.exists()
    assert dir_path.is_dir()

    # Create nested file
    content = "Nested content"
    temp_storage.save_file("test_dir/nested.txt", content)
    assert (dir_path / "nested.txt").exists()

    # List directory
    files = temp_storage.list_directory("test_dir")
    assert "nested.txt" in files

    # List non-existent directory
    files = temp_storage.list_directory("nonexistent")
    assert files == []

    # List file as directory
    files = temp_storage.list_directory("test_dir/nested.txt")
    assert files == []


def test_backup_operations(temp_storage: StorageManager) -> None:
    """Test backup functionality."""
    # Create original file
    content = "Original content"
    temp_storage.save_file("important.txt", content)

    # Create backup
    temp_storage.create_backup("important.txt")
    backup_files = list(temp_storage.root_dir.glob("important.txt.backup*"))
    assert len(backup_files) == 1

    # Verify backup content
    backup_content = temp_storage.load_file(backup_files[0].name)
    assert backup_content == content


def test_error_handling(temp_storage: StorageManager) -> None:
    """Test error handling for storage operations."""
    # Test loading non-existent file
    with pytest.raises(FileNotFoundError):
        temp_storage.load_file("nonexistent.txt")

    # Test loading non-existent file as JSON
    with pytest.raises(FileNotFoundError):
        temp_storage.load_file("nonexistent.json", as_json=True)

    # Test invalid directory operations
    with pytest.raises(ValueError):
        temp_storage.create_directory("invalid/nested/path")

    # Test backup of non-existent file
    with pytest.raises(FileNotFoundError):
        temp_storage.create_backup("nonexistent.txt")

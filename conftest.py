"""Pytest configuration file."""

import pytest
from pathlib import Path
from contextlib import contextmanager
from typing import List

from cursor_config import CURSOR_CONFIG


@pytest.fixture(autouse=True)
def attach_test_files(request):
    """Automatically attach relevant files for tests."""
    test_file = Path(request.module.__file__)
    source_file = test_file.parent.parent / test_file.stem.replace('test_', '')
    
    if source_file.exists():
        CURSOR_CONFIG.attach_files([str(source_file), str(test_file)])


@contextmanager
def attached_files(files: List[str]):
    """Context manager to ensure files are attached."""
    CURSOR_CONFIG.attach_files(files)
    try:
        yield
    finally:
        pass  # Cleanup if needed 
import os
import tempfile

import pandas as pd
import pytest

from metrics_header import write_header


def test_write_header_creates_directory():
    """Test that write_header creates the metrics directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "metrics", "test.csv")
        write_header(metrics_file)
        assert os.path.exists(os.path.dirname(metrics_file))


def test_write_header_creates_file():
    """Test that write_header creates the metrics file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")
        write_header(metrics_file)
        assert os.path.exists(metrics_file)


def test_write_header_correct_columns():
    """Test that write_header creates a file with the correct columns."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")
        write_header(metrics_file)

        # Read the created file
        df = pd.read_csv(metrics_file)

        # Check columns
        expected_columns = [
            "timestamp",
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "io_wait",
            "load_avg",
        ]
        assert list(df.columns) == expected_columns
        assert len(df) == 0  # Should be empty except for headers


def test_write_header_overwrites_existing():
    """Test that write_header overwrites existing file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")

        # Create a file with different content
        with open(metrics_file, "w") as f:
            f.write("old,content\n1,2\n")

        write_header(metrics_file)

        # Read the file and verify it's been overwritten
        df = pd.read_csv(metrics_file)
        expected_columns = [
            "timestamp",
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "io_wait",
            "load_avg",
        ]
        assert list(df.columns) == expected_columns
        assert len(df) == 0

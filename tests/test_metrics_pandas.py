import os
import tempfile

import pandas as pd

from metrics_pandas import write_metrics


def test_write_metrics_creates_directory():
    """Test that write_metrics creates the metrics directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "metrics", "test.csv")
        write_metrics(metrics_file, "2024-01-01", 50.0, 1024.0, 75.0, 0.5, 1.5)
        assert os.path.exists(os.path.dirname(metrics_file))


def test_write_metrics_creates_file():
    """Test that write_metrics creates the metrics file with correct data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")
        write_metrics(metrics_file, "2024-01-01", 50.0, 1024.0, 75.0, 0.5, 1.5)

        # Read and verify the file
        df = pd.read_csv(metrics_file)
        assert len(df) == 1
        row = df.iloc[0]
        assert row["timestamp"] == "2024-01-01"
        assert row["cpu_usage"] == 50.0
        assert row["memory_usage"] == 1024.0
        assert row["disk_usage"] == 75.0
        assert row["io_wait"] == 0.5
        assert row["load_avg"] == 1.5


def test_write_metrics_appends_data():
    """Test that write_metrics appends data to existing file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")

        # Write first record
        write_metrics(metrics_file, "2024-01-01", 50.0, 1024.0, 75.0, 0.5, 1.5)

        # Write second record
        write_metrics(metrics_file, "2024-01-02", 60.0, 2048.0, 80.0, 0.6, 1.6)

        # Read and verify both records
        df = pd.read_csv(metrics_file)
        assert len(df) == 2

        row1 = df.iloc[0]
        assert row1["timestamp"] == "2024-01-01"
        assert row1["cpu_usage"] == 50.0

        row2 = df.iloc[1]
        assert row2["timestamp"] == "2024-01-02"
        assert row2["cpu_usage"] == 60.0


def test_write_metrics_handles_float_conversion():
    """Test that write_metrics correctly handles string inputs for numeric fields."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")
        write_metrics(metrics_file, "2024-01-01", "50", "1024", "75", "0.5", "1.5")

        # Read and verify the file
        df = pd.read_csv(metrics_file)
        assert len(df) == 1
        row = df.iloc[0]
        assert row["cpu_usage"] == 50.0
        assert row["memory_usage"] == 1024.0
        assert row["disk_usage"] == 75.0
        assert row["io_wait"] == 0.5
        assert row["load_avg"] == 1.5

import os
import tempfile

import pandas as pd

from metrics.metrics_writer import write_metric_row


def test_write_metric_row_creates_directory():
    """Test that write_metric_row creates the metrics directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "metrics", "test.csv")
        write_metric_row(metrics_file, "test_metric", 42.0)
        assert os.path.exists(os.path.dirname(metrics_file))


def test_write_metric_row_creates_file():
    """Test that write_metric_row creates the metrics file with correct data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")
        timestamp = 1704067200  # 2024-01-01 00:00:00
        write_metric_row(metrics_file, "test_metric", 42.0, timestamp)

        # Read and verify the file
        df = pd.read_csv(metrics_file)
        assert len(df) == 1
        assert "timestamp" in df.columns
        assert "test_metric" in df.columns
        row = df.iloc[0]
        assert row["timestamp"] == timestamp
        assert row["test_metric"] == 42.0


def test_write_metric_row_appends_data():
    """Test that write_metric_row appends data to existing file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")

        # Write first record
        write_metric_row(metrics_file, "test_metric", 42.0, 1704067200)

        # Write second record
        write_metric_row(metrics_file, "test_metric", 43.0, 1704153600)

        # Read and verify both records
        df = pd.read_csv(metrics_file)
        assert len(df) == 2
        assert list(df.columns) == ["timestamp", "test_metric"]

        assert df.iloc[0]["test_metric"] == 42.0
        assert df.iloc[1]["test_metric"] == 43.0


def test_write_metric_row_adds_new_column():
    """Test that write_metric_row adds new column to existing file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")

        # Write first metric
        write_metric_row(metrics_file, "metric1", 42.0, 1704067200)

        # Write second metric with different name
        write_metric_row(metrics_file, "metric2", 43.0, 1704067200)

        # Read and verify file
        df = pd.read_csv(metrics_file)
        assert len(df) == 2
        assert set(df.columns) == {"timestamp", "metric1", "metric2"}


def test_write_metric_row_handles_float_conversion():
    """Test that write_metric_row correctly handles string input for value."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")
        write_metric_row(metrics_file, "test_metric", "42.5", 1704067200)

        # Read and verify the file
        df = pd.read_csv(metrics_file)
        assert len(df) == 1
        assert df.iloc[0]["test_metric"] == 42.5


def test_write_metric_row_uses_current_timestamp():
    """Test that write_metric_row uses current timestamp when none provided."""
    with tempfile.TemporaryDirectory() as temp_dir:
        metrics_file = os.path.join(temp_dir, "test.csv")
        write_metric_row(metrics_file, "test_metric", 42.0)

        # Read and verify the file
        df = pd.read_csv(metrics_file)
        assert len(df) == 1
        assert pd.notnull(df.iloc[0]["timestamp"])

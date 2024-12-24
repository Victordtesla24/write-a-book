import json
import os
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest

from metrics.metrics_collector import MetricsCollector


@pytest.fixture
def metrics_collector():
    """Create a metrics collector instance."""
    with patch("core_scripts.config_manager.CONFIG") as mock_config:
        mock_config.get.side_effect = lambda key, default=None: {
            "project_root": "/tmp",
            "metrics_retention_days": 7,
            "github_token": "test_token",
            "github_username": "test_user",
            "github_repo": "test_repo",
        }.get(key, default)
        yield MetricsCollector()


@pytest.fixture
def mock_psutil():
    """Mock psutil functions."""
    with patch("psutil.cpu_percent") as mock_cpu, patch("psutil.virtual_memory") as mock_mem, patch(
        "psutil.disk_usage"
    ) as mock_disk:

        mock_cpu.return_value = 10.5
        mock_mem.return_value = MagicMock(percent=75.0)
        mock_disk.return_value = MagicMock(percent=50.0)

        yield {"cpu": mock_cpu, "memory": mock_mem, "disk": mock_disk}


def test_collect_system_metrics(metrics_collector, mock_psutil):
    """Test collection of system metrics."""
    metrics = metrics_collector.collect_system_metrics()

    assert metrics["cpu_usage"] == 10.5
    assert metrics["memory_usage"] == 75.0
    assert metrics["disk_usage"] == 50.0
    assert "timestamp" in metrics


def test_collect_github_metrics_success(metrics_collector):
    """Test successful collection of GitHub metrics."""
    mock_response = MagicMock()
    mock_response.json.side_effect = [
        {"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10},
        ["commit1", "commit2", "commit3"],  # 3 commits today
    ]
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response) as mock_get:
        metrics = metrics_collector.collect_github_metrics()

    assert metrics is not None
    assert metrics["stars"] == 100
    assert metrics["forks"] == 50
    assert metrics["open_issues"] == 10
    assert metrics["commits_today"] == 3
    assert "timestamp" in metrics

    # Verify API calls
    assert mock_get.call_count == 2
    calls = mock_get.call_args_list
    assert "repos/test_user/test_repo" in calls[0][0][0]
    assert "commits" in calls[1][0][0]


def test_collect_github_metrics_no_config(metrics_collector):
    """Test GitHub metrics collection with missing configuration."""
    with patch("core_scripts.config_manager.CONFIG") as mock_config:
        mock_config.get.return_value = None
        metrics = metrics_collector.collect_github_metrics()

    assert metrics is None


def test_collect_test_metrics_no_coverage(metrics_collector):
    """Test collection of test metrics when coverage file doesn't exist."""
    metrics = metrics_collector.collect_test_metrics()

    assert metrics["coverage"] == 0.0
    assert "timestamp" in metrics


def test_save_metrics(metrics_collector):
    """Test saving metrics to file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Update metrics_collector's project root
        with patch.object(metrics_collector, "metrics_dir", os.path.join(temp_dir, "metrics")):
            # Create metrics directory
            os.makedirs(metrics_collector.metrics_dir)

            test_data = {"value": 42.0, "timestamp": time.time()}

            metrics_collector.save_metrics("test", test_data)

            # Check that file was created
            files = os.listdir(metrics_collector.metrics_dir)
            assert len(files) == 1
            assert files[0].startswith("test_")

            # Verify file contents
            with open(os.path.join(metrics_collector.metrics_dir, files[0])) as f:
                saved_data = json.load(f)
            assert saved_data == test_data


def test_collect_all(metrics_collector, mock_psutil):
    """Test collection of all metrics."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Update metrics_collector's project root
        with patch.object(metrics_collector, "metrics_dir", os.path.join(temp_dir, "metrics")):
            # Create metrics directory
            os.makedirs(metrics_collector.metrics_dir)

            # Mock GitHub API responses
            mock_response = MagicMock()
            mock_response.json.side_effect = [
                {"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10},
                ["commit1", "commit2", "commit3"],
            ]
            mock_response.status_code = 200

            with patch("requests.get", return_value=mock_response):
                metrics_collector.collect_all()

            # Check that files were created
            files = os.listdir(metrics_collector.metrics_dir)
            assert len(files) == 3  # system, github, and test metrics

            # Verify each file exists
            file_prefixes = {"system_", "github_", "test_"}
            saved_prefixes = {f.split("_")[0] + "_" for f in files}
            assert file_prefixes == saved_prefixes

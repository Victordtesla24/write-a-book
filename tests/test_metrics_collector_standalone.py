"""Standalone tests for the metrics collector module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from core_scripts.metrics_collector import MetricsCollector, EnforcementMetrics


@pytest.fixture
def mock_psutil():
    """Mock psutil functions."""
    with patch('psutil.cpu_percent', return_value=50.0), \
         patch('psutil.virtual_memory', return_value=MagicMock(percent=60.0)), \
         patch('psutil.disk_usage', return_value=MagicMock(percent=70.0)):
        yield


@pytest.fixture
def metrics_dir(tmp_path):
    """Create a temporary metrics directory."""
    metrics_path = tmp_path / "metrics"
    metrics_path.mkdir(exist_ok=True)
    return metrics_path


@pytest.fixture
def collector(metrics_dir):
    """Create MetricsCollector instance with temporary directory."""
    collector = MetricsCollector()
    collector.metrics_dir = metrics_dir
    return collector


def test_collect_system_metrics(collector, mock_psutil):
    """Test system metrics collection."""
    metrics = collector.collect_system_metrics()
    
    assert "timestamp" in metrics
    assert metrics["cpu_usage"] == 50.0
    assert metrics["memory_usage"] == 60.0
    assert metrics["disk_usage"] == 70.0


def test_collect_test_metrics_without_coverage(collector):
    """Test test metrics collection without coverage data."""
    metrics = collector.collect_test_metrics()
    
    assert "timestamp" in metrics
    assert metrics["coverage_total"] == 0.0
    assert metrics["tests_passed"] == 0
    assert metrics["tests_failed"] == 0
    assert "last_run" in metrics


def test_collect_test_metrics_with_coverage(collector):
    """Test test metrics collection with coverage data."""
    coverage_data = {
        "totals": {
            "percent_covered": 85.5
        }
    }
    coverage_file = collector.metrics_dir / "coverage.json"
    with coverage_file.open("w") as f:
        json.dump(coverage_data, f)
    
    metrics = collector.collect_test_metrics()
    assert metrics["coverage_total"] == 85.5


def test_collect_enforcement_metrics(collector):
    """Test enforcement metrics collection."""
    metrics = collector.collect_enforcement_metrics()
    
    assert "timestamp" in metrics
    assert metrics["compliant"] is True
    assert "metrics" in metrics
    assert metrics["metrics"]["token_reduction"] == 0.40
    assert metrics["metrics"]["response_time"] == 0.30
    assert metrics["metrics"]["cost_reduction"] == 0.45
    assert metrics["metrics"]["resource_efficiency"] == 0.40


def test_save_metrics(collector):
    """Test metrics saving."""
    test_metrics = {"test": "data"}
    collector._save_metrics("test", test_metrics)
    
    metrics_file = collector.metrics_dir / "test.json"
    assert metrics_file.exists()
    
    with metrics_file.open() as f:
        saved_metrics = json.load(f)
    assert saved_metrics == test_metrics


def test_collect_all(collector, mock_psutil):
    """Test collecting all metrics."""
    metrics = collector.collect_all()
    
    assert "system" in metrics
    assert "test" in metrics
    assert "enforcement" in metrics
    
    assert metrics["system"]["cpu_usage"] == 50.0
    assert metrics["test"]["coverage_total"] == 0.0
    assert metrics["enforcement"]["compliant"] is True


def test_system_metrics_error_handling(collector):
    """Test system metrics error handling."""
    with patch('psutil.cpu_percent', side_effect=Exception("Test error")):
        metrics = collector.collect_system_metrics()
        assert metrics == {}


def test_test_metrics_error_handling(collector):
    """Test test metrics error handling."""
    with patch('pathlib.Path.open', side_effect=Exception("Test error")):
        metrics = collector.collect_test_metrics()
        assert metrics["coverage_total"] == 0.0


def test_enforcement_metrics_error_handling(collector):
    """Test enforcement metrics error handling."""
    with patch.object(
        collector.enforcement_strategy,
        'get_status',
        side_effect=Exception("Test error")
    ):
        metrics = collector.collect_enforcement_metrics()
        assert metrics == {}


def test_save_metrics_error_handling(collector):
    """Test metrics saving error handling."""
    with patch('pathlib.Path.open', side_effect=Exception("Test error")):
        # Should not raise exception
        collector._save_metrics("test", {"test": "data"})


def test_enforcement_metrics_calculation(collector):
    """Test enforcement metrics calculation."""
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    collector.enforcement_strategy.update_metrics(metrics)
    status = collector.enforcement_strategy.get_status()
    
    assert status["compliant"] is True
    assert status["metrics"]["token_reduction"] == 0.40
    assert status["metrics"]["response_time"] == 0.30
    assert status["metrics"]["cost_reduction"] == 0.45
    assert status["metrics"]["resource_efficiency"] == 0.40

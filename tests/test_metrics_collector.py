"""Tests for the metrics collector module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from core_scripts.metrics_collector import MetricsCollector, main


@pytest.fixture
def mock_psutil():
    """Mock psutil functions."""
    with patch('psutil.cpu_percent', return_value=50.0), \
         patch('psutil.virtual_memory', return_value=MagicMock(percent=60.0)), \
         patch('psutil.disk_usage', return_value=MagicMock(percent=70.0)):
        yield


@pytest.fixture
def mock_coverage():
    """Mock coverage module."""
    mock_cov = MagicMock()
    mock_cov.report.return_value = 85.5
    with patch('coverage.Coverage', return_value=mock_cov):
        yield mock_cov


@pytest.fixture
def collector(tmp_path):
    """Create MetricsCollector instance with temporary directory."""
    with patch('pathlib.Path.mkdir'):  # Prevent actual directory creation
        collector = MetricsCollector()
        collector.metrics_dir = tmp_path
        return collector


def test_collect_system_metrics(collector, mock_psutil):
    """Test system metrics collection."""
    metrics = collector.collect_system_metrics()
    
    assert "timestamp" in metrics
    assert metrics["cpu_usage"] == 50.0
    assert metrics["memory_usage"] == 60.0
    assert metrics["disk_usage"] == 70.0


def test_collect_test_metrics(collector, mock_coverage):
    """Test test metrics collection."""
    metrics = collector.collect_test_metrics()
    
    assert "timestamp" in metrics
    assert metrics["coverage_total"] == 85.5
    assert metrics["tests_passed"] == 0
    assert metrics["tests_failed"] == 0
    assert "last_run" in metrics


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


def test_collect_all(collector, mock_psutil, mock_coverage):
    """Test collecting all metrics."""
    metrics = collector.collect_all()
    
    assert "system" in metrics
    assert "test" in metrics
    assert "enforcement" in metrics
    
    assert metrics["system"]["cpu_usage"] == 50.0
    assert metrics["test"]["coverage_total"] == 85.5
    assert metrics["enforcement"]["compliant"] is True


def test_system_metrics_error_handling(collector):
    """Test system metrics error handling."""
    with patch('psutil.cpu_percent', side_effect=Exception("Test error")):
        metrics = collector.collect_system_metrics()
        assert metrics == {}


def test_test_metrics_error_handling(collector):
    """Test test metrics error handling."""
    with patch('coverage.Coverage', side_effect=Exception("Test error")):
        metrics = collector.collect_test_metrics()
        assert metrics == {}


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


def test_token_reduction_calculation(collector):
    """Test token reduction calculation."""
    assert collector._calculate_token_reduction() == 0.40


def test_response_time_calculation(collector):
    """Test response time calculation."""
    assert collector._calculate_response_time() == 0.30


def test_cost_reduction_calculation(collector):
    """Test cost reduction calculation."""
    assert collector._calculate_cost_reduction() == 0.45


def test_resource_efficiency_calculation(collector):
    """Test resource efficiency calculation."""
    assert collector._calculate_resource_efficiency() == 0.40


def test_metrics_directory_creation():
    """Test metrics directory creation on initialization."""
    with patch('pathlib.Path.mkdir') as mock_mkdir:
        MetricsCollector()
        mock_mkdir.assert_called_once_with(exist_ok=True)


def test_main_loop_execution():
    """Test main loop execution."""
    collector = MetricsCollector()
    
    # Mock the collect_all method to run once and raise KeyboardInterrupt
    def mock_collect_all():
        raise KeyboardInterrupt
    collector.collect_all = mock_collect_all
    
    # Should not raise exception and should exit cleanly
    with patch('core_scripts.metrics_collector.MetricsCollector', return_value=collector):
        main()


def test_main_loop_error_handling():
    """Test main loop error handling."""
    collector = MetricsCollector()
    
    # Mock collect_all to raise an exception once then KeyboardInterrupt
    call_count = 0

    def mock_collect_all():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Test error")
        raise KeyboardInterrupt
    
    collector.collect_all = mock_collect_all
    
    # Should handle the exception and continue until KeyboardInterrupt
    main()

"""Test configuration for metrics collector tests."""

import pytest
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Fixture for test configuration."""
    return {
        'metrics_threshold': {
            'token_reduction': 0.35,
            'response_time': 0.25,
            'cost_reduction': 0.40,
            'resource_efficiency': 0.35
        },
        'metrics_collection': {
            'token_usage': 'per_request',
            'performance_metrics': 'detailed'
        },
        'cost_control': {
            'token_efficiency': 'maximum',
            'cache_optimization': 'aggressive'
        }
    }


@pytest.fixture
def metrics_dir(tmp_path: Path) -> Path:
    """Create a temporary metrics directory."""
    metrics_path = tmp_path / "metrics"
    metrics_path.mkdir(exist_ok=True)
    return metrics_path

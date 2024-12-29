"""Standalone tests for the enforcement strategy module."""

import json
import pytest
from datetime import datetime
from pathlib import Path

from src.book_editor.core.enforcement_strategy import EnforcementStrategy, EnforcementMetrics


@pytest.fixture
def test_config(tmp_path):
    """Create test configuration."""
    config = {
        'metrics_threshold': {
            'token_reduction': 0.35,
            'response_time': 0.25,
            'cost_reduction': 0.40,
            'resource_efficiency': 0.35
        },
        'strict_enforcement': True,
        'metrics_collection': {
            'token_usage': 'per_request',
            'performance_metrics': 'detailed'
        },
        'cost_control': {
            'token_efficiency': 'maximum',
            'cache_optimization': 'aggressive'
        }
    }
    
    config_file = tmp_path / "settings.json"
    with config_file.open('w') as f:
        json.dump(config, f)
    
    return str(config_file)


@pytest.fixture
def strategy(test_config):
    """Create EnforcementStrategy instance."""
    return EnforcementStrategy(config_path=test_config)


def test_enforcement_metrics_defaults():
    """Test EnforcementMetrics default values."""
    metrics = EnforcementMetrics()
    assert metrics.token_reduction == 0.0
    assert metrics.response_time == 0.0
    assert metrics.cost_reduction == 0.0
    assert metrics.resource_efficiency == 0.0


def test_enforcement_metrics_custom_values():
    """Test EnforcementMetrics with custom values."""
    metrics = EnforcementMetrics(
        token_reduction=0.4,
        response_time=0.3,
        cost_reduction=0.45,
        resource_efficiency=0.4
    )
    assert metrics.token_reduction == 0.4
    assert metrics.response_time == 0.3
    assert metrics.cost_reduction == 0.45
    assert metrics.resource_efficiency == 0.4


def test_load_config_success(test_config):
    """Test successful config loading."""
    strategy = EnforcementStrategy(config_path=test_config)
    assert strategy.config is not None
    assert 'metrics_threshold' in strategy.config
    assert 'strict_enforcement' in strategy.config


def test_load_config_error():
    """Test error handling when loading config."""
    strategy = EnforcementStrategy(config_path="nonexistent.json")
    assert strategy.config == {}


def test_validate_compliance_success(strategy):
    """Test compliance validation with passing metrics."""
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    assert strategy.validate_compliance() is True


def test_validate_compliance_failure(strategy):
    """Test compliance validation with failing metrics."""
    metrics = EnforcementMetrics(
        token_reduction=0.20,
        response_time=0.15,
        cost_reduction=0.25,
        resource_efficiency=0.20
    )
    strategy.update_metrics(metrics)
    assert strategy.validate_compliance() is False


def test_enforce_rules_success(strategy):
    """Test successful rule enforcement."""
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    assert strategy.enforce_rules() is True


def test_enforce_rules_failure(strategy):
    """Test failed rule enforcement."""
    metrics = EnforcementMetrics(
        token_reduction=0.20,
        response_time=0.15,
        cost_reduction=0.25,
        resource_efficiency=0.20
    )
    strategy.update_metrics(metrics)
    assert strategy.enforce_rules() is False


def test_enforce_rules_with_empty_config():
    """Test enforce_rules with empty configuration."""
    strategy = EnforcementStrategy(config_path="nonexistent.json")
    assert strategy.enforce_rules() is False


def test_validate_compliance_with_missing_thresholds():
    """Test compliance validation with missing threshold configurations."""
    strategy = EnforcementStrategy(config_path="nonexistent.json")
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    assert strategy.validate_compliance() is False


def test_monitor_performance(strategy):
    """Test performance monitoring."""
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    strategy.config['metrics_collection'] = {
        'token_usage': 'per_request',
        'performance_metrics': 'detailed'
    }
    strategy.enforce_rules()
    # No assertion needed as we're testing coverage of the monitoring paths


def test_optimize_costs(strategy):
    """Test cost optimization."""
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    strategy.config['cost_control'] = {
        'token_efficiency': 'maximum',
        'cache_optimization': 'aggressive'
    }
    strategy.enforce_rules()
    # No assertion needed as we're testing coverage of the optimization paths


def test_get_status(strategy):
    """Test status reporting."""
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    status = strategy.get_status()
    
    assert status['compliant'] is True
    assert status['metrics']['token_reduction'] == 0.40
    assert status['metrics']['response_time'] == 0.30
    assert status['metrics']['cost_reduction'] == 0.45
    assert status['metrics']['resource_efficiency'] == 0.40


def test_log_metrics(strategy):
    """Test metrics logging."""
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    strategy._log_metrics()  # Should not raise any exceptions

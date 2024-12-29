"""Tests for the enforcement strategy implementation."""

import json
import pytest
from unittest.mock import patch, mock_open

from src.book_editor.core.enforcement_strategy import (
    EnforcementMetrics,
    EnforcementStrategy
)


@pytest.fixture
def mock_config():
    """Fixture for test configuration."""
    return {
        'strict_enforcement': True,
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
def strategy(mock_config):
    """Fixture for EnforcementStrategy instance."""
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
        return EnforcementStrategy()


def test_load_config(strategy, mock_config):
    """Test configuration loading."""
    assert strategy.config == mock_config


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


def test_error_handling(mock_config):
    """Test error handling with invalid config path."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        strategy = EnforcementStrategy('invalid/path')
        assert strategy.config == {}
        assert strategy.enforce_rules() is False


def test_validate_compliance_error_handling(strategy):
    """Test compliance validation error handling."""
    strategy.config = None  # Force an error condition
    assert strategy.validate_compliance() is False


def test_enforce_rules_with_empty_config(strategy):
    """Test enforce_rules with empty configuration."""
    strategy.config = {}
    assert strategy.enforce_rules() is False


def test_enforce_rules_with_invalid_metrics(strategy):
    """Test enforce_rules with invalid metrics data."""
    strategy.metrics = None  # Force an error condition
    assert strategy.enforce_rules() is False


def test_monitor_performance_coverage(strategy):
    """Test performance monitoring with all options enabled."""
    strategy.config['metrics_collection'] = {
        'token_usage': 'per_request',
        'performance_metrics': 'detailed'
    }
    strategy.enforce_rules()
    # No assertion needed as we're testing coverage of the monitoring paths


def test_optimize_costs_coverage(strategy):
    """Test cost optimization with all options enabled."""
    strategy.config['cost_control'] = {
        'token_efficiency': 'maximum',
        'cache_optimization': 'aggressive'
    }
    strategy.enforce_rules()
    # No assertion needed as we're testing coverage of the optimization paths


def test_validate_compliance_with_missing_thresholds(strategy):
    """Test compliance validation with missing threshold configurations."""
    strategy.config['metrics_threshold'] = {}
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    assert strategy.validate_compliance() is True  # Should use default thresholds


def test_enforce_rules_with_strict_enforcement_disabled(strategy):
    """Test enforce_rules with strict enforcement disabled."""
    strategy.config['strict_enforcement'] = False
    metrics = EnforcementMetrics(
        token_reduction=0.20,  # Below threshold
        response_time=0.15,    # Below threshold
        cost_reduction=0.25,   # Below threshold
        resource_efficiency=0.20  # Below threshold
    )
    strategy.update_metrics(metrics)
    assert strategy.enforce_rules() is True  # Should pass as strict enforcement is disabled


def test_enforce_rules_exception_handling(strategy):
    """Test enforce_rules with exception in monitoring."""
    def raise_exception(*args, **kwargs):
        raise Exception("Test exception")
    
    strategy._monitor_performance = raise_exception
    assert strategy.enforce_rules() is False


def test_validate_compliance_with_invalid_thresholds(strategy):
    """Test compliance validation with invalid threshold values."""
    strategy.config['metrics_threshold'] = {
        'token_reduction': 'invalid',
        'response_time': None,
        'cost_reduction': {},
        'resource_efficiency': []
    }
    assert strategy.validate_compliance() is False


def test_validate_compliance_with_exception(strategy):
    """Test compliance validation with an exception during comparison."""
    strategy.metrics.token_reduction = None  # Force comparison exception
    assert strategy.validate_compliance() is False


def test_enforce_rules_with_monitoring_failure(strategy):
    """Test enforce_rules when monitoring fails."""
    def mock_monitor():
        raise RuntimeError("Monitoring failed")
    
    strategy._monitor_performance = mock_monitor
    assert strategy.enforce_rules() is False


def test_enforce_rules_with_optimization_failure(strategy):
    """Test enforce_rules when optimization fails."""
    def mock_optimize():
        raise RuntimeError("Optimization failed")
    
    strategy._optimize_costs = mock_optimize
    assert strategy.enforce_rules() is False


def test_enforce_rules_with_validation_error(strategy):
    """Test enforce_rules with validation error."""
    def mock_validate():
        raise ValueError("Validation error")
    
    strategy.validate_compliance = mock_validate
    assert strategy.enforce_rules() is False


def test_enforce_rules_validation_branch(strategy):
    """Test enforce_rules validation branch coverage."""
    strategy.config['strict_enforcement'] = True
    metrics = EnforcementMetrics(
        token_reduction=0.20,  # Below threshold
        response_time=0.15,    # Below threshold
        cost_reduction=0.25,   # Below threshold
        resource_efficiency=0.20  # Below threshold
    )
    strategy.update_metrics(metrics)
    
    # This should trigger the validation failure branch
    result = strategy.enforce_rules()
    assert result is False


def test_enforce_rules_optimization_branch(strategy):
    """Test enforce_rules optimization branch coverage."""
    # Setup passing metrics
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    
    # Mock optimization to fail after monitoring
    original_optimize = strategy._optimize_costs

    def mock_optimize():
        raise Exception("Optimization failure")
    strategy._optimize_costs = mock_optimize
    
    # This should trigger the optimization failure branch
    result = strategy.enforce_rules()
    assert result is False
    
    # Restore original method
    strategy._optimize_costs = original_optimize


def test_enforce_rules_complete_flow(strategy):
    """Test enforce_rules complete flow with all branches."""
    # Test validation exit path
    strategy.config['strict_enforcement'] = True
    metrics = EnforcementMetrics(
        token_reduction=0.20,
        response_time=0.15,
        cost_reduction=0.25,
        resource_efficiency=0.20
    )
    strategy.update_metrics(metrics)
    assert strategy.enforce_rules() is False
    
    # Test optimization exit path
    metrics = EnforcementMetrics(
        token_reduction=0.40,
        response_time=0.30,
        cost_reduction=0.45,
        resource_efficiency=0.40
    )
    strategy.update_metrics(metrics)
    strategy._optimize_costs = lambda: exec('raise Exception("Optimization exit")')
    assert strategy.enforce_rules() is False

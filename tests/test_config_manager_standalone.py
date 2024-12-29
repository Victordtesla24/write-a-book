"""Standalone tests for the configuration manager."""

import json
import pytest
from unittest.mock import patch, mock_open

from core_scripts.config_manager import (
    load_config,
    save_config,
    update_config,
    validate_config,
    ConfigurationError,
    ensure_directory_exists,
    set_file_permissions
)


@pytest.fixture
def mock_config():
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


def test_load_config_success(mock_config):
    """Test successful configuration loading."""
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
        config = load_config('config.json')
        assert config == mock_config


def test_load_config_file_not_found():
    """Test configuration loading with missing file."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        with pytest.raises(ConfigurationError) as exc_info:
            load_config('nonexistent.json')
        assert "Configuration file not found" in str(exc_info.value)


def test_load_config_invalid_json():
    """Test configuration loading with invalid JSON."""
    with patch('builtins.open', mock_open(read_data='invalid json')):
        with pytest.raises(ConfigurationError) as exc_info:
            load_config('config.json')
        assert "Invalid JSON in configuration file" in str(exc_info.value)


def test_save_config_success(mock_config, tmp_path):
    """Test successful configuration saving."""
    config_file = tmp_path / "config.json"
    save_config(str(config_file), mock_config)
    
    assert config_file.exists()
    with config_file.open() as f:
        saved_config = json.load(f)
    assert saved_config == mock_config


def test_save_config_permission_error(mock_config):
    """Test configuration saving with permission error."""
    with patch('builtins.open', side_effect=PermissionError):
        with pytest.raises(ConfigurationError) as exc_info:
            save_config('config.json', mock_config)
        assert "Permission denied" in str(exc_info.value)


def test_update_config_success(mock_config):
    """Test successful configuration update."""
    updates = {'metrics_threshold': {'token_reduction': 0.40}}
    updated_config = update_config(mock_config, updates)
    assert updated_config['metrics_threshold']['token_reduction'] == 0.40
    assert updated_config['metrics_collection'] == mock_config['metrics_collection']


def test_update_config_invalid_structure():
    """Test configuration update with invalid structure."""
    with pytest.raises(ConfigurationError) as exc_info:
        update_config({}, {'key': 'value'})
    assert "Invalid configuration structure" in str(exc_info.value)


def test_validate_config_success(mock_config):
    """Test successful configuration validation."""
    assert validate_config(mock_config) is True


def test_validate_config_missing_required():
    """Test configuration validation with missing required fields."""
    invalid_config = {'metrics_collection': {}}
    with pytest.raises(ConfigurationError) as exc_info:
        validate_config(invalid_config)
    assert "Missing required configuration" in str(exc_info.value)


def test_validate_config_invalid_values(mock_config):
    """Test configuration validation with invalid values."""
    mock_config['metrics_threshold']['token_reduction'] = 'invalid'
    with pytest.raises(ConfigurationError) as exc_info:
        validate_config(mock_config)
    assert "Invalid value type" in str(exc_info.value)


def test_validate_config_invalid_type():
    """Test configuration validation with invalid type."""
    with pytest.raises(ConfigurationError) as exc_info:
        validate_config([])  # type: ignore
    assert "Configuration must be a dictionary" in str(exc_info.value)


def test_ensure_directory_exists(tmp_path):
    """Test directory creation."""
    test_dir = tmp_path / "test_dir"
    test_file = test_dir / "config.json"
    ensure_directory_exists(str(test_file))
    assert test_dir.exists()


def test_ensure_directory_exists_error():
    """Test directory creation error handling."""
    with patch('os.makedirs', side_effect=OSError("Permission denied")):
        with pytest.raises(ConfigurationError) as exc_info:
            ensure_directory_exists('test/config.json')
        assert "Failed to create directory" in str(exc_info.value)


def test_set_file_permissions():
    """Test file permission setting."""
    with patch('os.path.exists', return_value=True), \
         patch('os.chmod') as mock_chmod:
        set_file_permissions('test.json')
        mock_chmod.assert_called_once_with('test.json', 0o666)


def test_set_file_permissions_error():
    """Test file permission error handling."""
    with patch('os.chmod', side_effect=OSError("Permission denied")):
        with pytest.raises(ConfigurationError) as exc_info:
            set_file_permissions('test.json')
        assert "Failed to set file permissions" in str(exc_info.value)


def test_update_config_with_nested_dict():
    """Test update_config with nested dictionary updates."""
    current = {
        'nested': {'key1': 'value1', 'key2': 'value2'},
        'other': 'value'
    }
    updates = {
        'nested': {'key1': 'new_value', 'key3': 'value3'}
    }
    result = update_config(current, updates)
    assert result['nested']['key1'] == 'new_value'
    assert result['nested']['key2'] == 'value2'
    assert result['nested']['key3'] == 'value3'
    assert result['other'] == 'value'


def test_validate_config_with_invalid_threshold():
    """Test validate_config with invalid threshold value."""
    config = {
        'metrics_threshold': {'token_reduction': 1.5},
        'metrics_collection': {},
        'cost_control': {}
    }
    with pytest.raises(ConfigurationError) as exc_info:
        validate_config(config)
    assert "must be between 0 and 1" in str(exc_info.value)

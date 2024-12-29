"""Tests for the configuration manager."""

import json
import os
import pytest
from typing import Dict, Any
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


def test_load_config_success(mock_config: Dict[str, Any]) -> None:
    """Test successful configuration loading."""
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
        config = load_config('config.json')
        assert config == mock_config


def test_load_config_file_not_found() -> None:
    """Test configuration loading with missing file."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        with pytest.raises(ConfigurationError) as exc_info:
            load_config('nonexistent.json')
        assert "Configuration file not found" in str(exc_info.value)


def test_load_config_invalid_json() -> None:
    """Test configuration loading with invalid JSON."""
    with patch('builtins.open', mock_open(read_data='invalid json')):
        with pytest.raises(ConfigurationError) as exc_info:
            load_config('config.json')
        assert "Invalid JSON in configuration file" in str(exc_info.value)


def test_save_config_success(mock_config: Dict[str, Any]) -> None:
    """Test successful configuration saving."""
    mock_file = mock_open()
    with patch('builtins.open', mock_file), \
         patch('os.chmod'), \
         patch('os.path.exists', return_value=True):
        save_config('config.json', mock_config)
        mock_file().write.assert_called()


def test_save_config_permission_error(mock_config: Dict[str, Any]) -> None:
    """Test configuration saving with permission error."""
    with patch('builtins.open', side_effect=PermissionError):
        with pytest.raises(ConfigurationError) as exc_info:
            save_config('config.json', mock_config)
        assert "Permission denied" in str(exc_info.value)


def test_update_config_success(mock_config: Dict[str, Any]) -> None:
    """Test successful configuration update."""
    updates = {'metrics_threshold': {'token_reduction': 0.40}}
    updated_config = update_config(mock_config, updates)
    assert updated_config['metrics_threshold']['token_reduction'] == 0.40
    assert updated_config['metrics_collection'] == mock_config['metrics_collection']


def test_update_config_invalid_structure() -> None:
    """Test configuration update with invalid structure."""
    empty_dict: Dict[str, Any] = {}
    with pytest.raises(ConfigurationError) as exc_info:
        update_config(empty_dict, {'key': 'value'})
    assert "Invalid configuration structure" in str(exc_info.value)


def test_validate_config_success(mock_config: Dict[str, Any]) -> None:
    """Test successful configuration validation."""
    assert validate_config(mock_config) is True


def test_validate_config_missing_required() -> None:
    """Test configuration validation with missing required fields."""
    invalid_config: Dict[str, Any] = {'metrics_collection': {}}
    with pytest.raises(ConfigurationError) as exc_info:
        validate_config(invalid_config)
    assert "Missing required configuration" in str(exc_info.value)


def test_validate_config_invalid_values(mock_config: Dict[str, Any]) -> None:
    """Test configuration validation with invalid values."""
    mock_config['metrics_threshold']['token_reduction'] = 'invalid'
    with pytest.raises(ConfigurationError) as exc_info:
        validate_config(mock_config)
    assert "Invalid value type" in str(exc_info.value)


def test_validate_config_invalid_type() -> None:
    """Test configuration validation with invalid type."""
    invalid_config: Dict[str, Any] = []  # type: ignore
    with pytest.raises(ConfigurationError) as exc_info:
        validate_config(invalid_config)  # type: ignore
    assert "Configuration must be a dictionary" in str(exc_info.value)


def test_ensure_directory_exists() -> None:
    """Test directory creation with permissions."""
    test_dir = 'test_config_dir'
    test_file = os.path.join(test_dir, 'config.json')
    
    with patch('os.makedirs') as mock_makedirs:
        ensure_directory_exists(test_file)
        mock_makedirs.assert_called_once_with(test_dir, mode=0o777, exist_ok=True)


def test_ensure_directory_exists_error() -> None:
    """Test directory creation error handling."""
    with patch('os.makedirs', side_effect=OSError("Permission denied")):
        with pytest.raises(ConfigurationError) as exc_info:
            ensure_directory_exists('test/config.json')
        assert "Failed to create directory" in str(exc_info.value)


def test_set_file_permissions_error() -> None:
    """Test file permission error handling."""
    with patch('os.chmod', side_effect=OSError("Permission denied")):
        with pytest.raises(ConfigurationError) as exc_info:
            set_file_permissions('test.json')
        assert "Failed to set file permissions" in str(exc_info.value)


def test_save_config_with_error() -> None:
    """Test save_config with various errors."""
    config = {'test': 'data'}
    
    with patch('os.makedirs', side_effect=OSError("Directory error")):
        with pytest.raises(ConfigurationError) as exc_info:
            save_config('test/config.json', config)
        assert "Failed to save configuration" in str(exc_info.value)


def test_update_config_with_nested_dict() -> None:
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


def test_validate_config_with_invalid_threshold() -> None:
    """Test validate_config with invalid threshold value."""
    config = {
        'metrics_threshold': {'token_reduction': 1.5},
        'metrics_collection': {},
        'cost_control': {}
    }
    with pytest.raises(ConfigurationError) as exc_info:
        validate_config(config)
    assert "must be between 0 and 1" in str(exc_info.value)


def test_set_file_permissions() -> None:
    """Test file permission setting."""
    with patch('os.path.exists', side_effect=[True, False]), \
         patch('builtins.open', mock_open()) as mock_file, \
         patch('os.chmod') as mock_chmod:
        # Test with existing file
        set_file_permissions('test1.json')
        mock_file.assert_not_called()
        mock_chmod.assert_called_once_with('test1.json', 0o666)
        
        # Test with non-existing file
        mock_chmod.reset_mock()
        set_file_permissions('test2.json')
        mock_file.assert_called_once()
        mock_chmod.assert_called_once_with('test2.json', 0o666)


def test_update_config_complex_merge() -> None:
    """Test update_config with complex dictionary merging."""
    current = {
        'dict': {'a': 1, 'b': {'x': 1}},
        'list': [1, 2],
        'str': 'old'
    }
    updates = {
        'dict': {'b': {'y': 2}, 'c': 3},  # Merge nested dict
        'list': {'new': 'dict'},  # Replace list with dict
        'str': {'new': 'dict'}    # Replace str with dict
    }
    result = update_config(current, updates)
    assert result['dict'] == {'a': 1, 'b': {'y': 2}, 'c': 3}
    assert result['list'] == {'new': 'dict'}
    assert result['str'] == {'new': 'dict'}


def test_load_config_permission_error() -> None:
    """Test load_config with permission error."""
    with patch('builtins.open', side_effect=PermissionError):
        with pytest.raises(ConfigurationError) as exc_info:
            load_config('config.json')
        assert "Permission denied reading configuration" in str(exc_info.value)


def test_update_config_non_dict_value() -> None:
    """Test update_config with non-dictionary value."""
    current = {
        'key1': {'nested': 'value'},
        'key2': 'string'
    }
    updates = {
        'key1': 'new_string',  # Replacing dict with string
        'key2': {'new': 'dict'}  # Replacing string with dict
    }
    result = update_config(current, updates)
    assert result['key1'] == 'new_string'
    assert result['key2'] == {'new': 'dict'}

"""Configuration management module."""

import json
import os
from typing import Dict, Any


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


def ensure_directory_exists(filepath: str) -> None:
    """Ensure the directory exists with correct permissions.
    
    Args:
        filepath: Path to the file.
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        try:
            # Create directory with universal write permissions
            os.makedirs(directory, mode=0o777, exist_ok=True)
        except OSError as e:
            msg = f"Failed to create directory: {str(e)}"
            raise ConfigurationError(msg)


def set_file_permissions(filepath: str) -> None:
    """Set appropriate file permissions.
    
    Args:
        filepath: Path to the file.
    """
    try:
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write('{}')
        os.chmod(filepath, 0o666)
    except OSError as e:
        msg = f"Failed to set file permissions: {str(e)}"
        raise ConfigurationError(msg)


def load_config(filepath: str) -> Dict[str, Any]:
    """Load and validate a JSON configuration file.

    Args:
        filepath: Path to the configuration file.

    Returns:
        Dict containing the configuration.

    Raises:
        ConfigurationError: For file, JSON, or permission errors.
    """
    try:
        with open(filepath, 'r') as f:
            config = json.load(f)
            if not isinstance(config, dict):
                raise ConfigurationError("Configuration must be a dictionary")
            return config
    except FileNotFoundError:
        raise ConfigurationError("Configuration file not found")
    except json.JSONDecodeError:
        raise ConfigurationError("Invalid JSON in configuration file")
    except PermissionError:
        msg = "Permission denied reading configuration"
        raise ConfigurationError(msg)


def save_config(filepath: str, config: Dict[str, Any]) -> None:
    """Save configuration to a JSON file.

    Write configuration data to a JSON file with proper permissions.

    Args:
        filepath: Output path.
        config: Data to save.

    Raises:
        ConfigurationError: If save fails.
    """
    try:
        ensure_directory_exists(filepath)
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        set_file_permissions(filepath)
    except PermissionError:
        msg = "Permission denied saving configuration"
        raise ConfigurationError(msg)
    except Exception as e:
        msg = f"Failed to save configuration: {str(e)}"
        raise ConfigurationError(msg)


def update_config(current_config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update configuration with new values.
    
    Args:
        current_config: Current configuration dictionary.
        updates: Dictionary containing updates to apply.
        
    Returns:
        Updated configuration dictionary.
        
    Raises:
        ConfigurationError: If current_config is invalid.
    """
    if not isinstance(current_config, dict) or not current_config:
        raise ConfigurationError("Invalid configuration structure")
    
    updated = current_config.copy()
    for key, value in updates.items():
        is_dict = isinstance(value, dict)
        has_key = key in updated
        target_is_dict = has_key and isinstance(updated[key], dict)
        if is_dict and target_is_dict:
            updated[key].update(value)
        else:
            updated[key] = value
    
    return updated


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration structure and values.
    
    Args:
        config: Configuration dictionary to validate.
        
    Returns:
        True if configuration is valid.
        
    Raises:
        ConfigurationError: If configuration is invalid.
    """
    if not isinstance(config, dict):
        raise ConfigurationError("Configuration must be a dictionary")

    required = ['metrics_threshold', 'metrics_collection', 'cost_control']
    missing = [section for section in required if section not in config]
    if missing:
        sections = ', '.join(missing)
        msg = f"Missing required configuration sections: {sections}"
        raise ConfigurationError(msg)

    # Validate metrics_threshold values
    if 'metrics_threshold' in config:
        thresholds = config['metrics_threshold']
        for key, value in thresholds.items():
            if not isinstance(value, (int, float)):
                msg = f"Invalid value type for threshold {key}: must be numeric"
                raise ConfigurationError(msg)
            if value < 0 or value > 1:
                msg = f"Invalid value for threshold {key}: must be between 0 and 1"
                raise ConfigurationError(msg)

    return True


# Default configuration
CONFIG = {
    'project_root': os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'metrics_threshold': {
        'token_reduction': 0.35,
        'response_time': 0.25,
        'cost_reduction': 0.40,
        'resource_efficiency': 0.35
    },
    'metrics_collection': {
        'token_usage': 'per_request',
        'cost_tracking': 'real_time',
        'performance_metrics': 'detailed',
        'optimization_effectiveness': 'tracked',
        'resource_utilization': 'monitored',
        'cache_hit_ratio': 'tracked',
        'response_latency': 'measured',
        'model_efficiency': 'analyzed'
    },
    'cost_control': {
        'token_efficiency': 'maximum',
        'model_selection': 'cost_aware',
        'cache_optimization': 'aggressive',
        'request_batching': True,
        'response_optimization': 'minimal',
        'smart_retry_strategy': 'exponential',
        'context_compression': True
    },
    'metrics_retention_days': 7,
    'github_token': os.getenv('GITHUB_TOKEN', ''),
    'github_username': os.getenv('GITHUB_USERNAME', ''),
    'github_repo': os.getenv('GITHUB_REPO', '')
}

# Export all public functions and CONFIG
__all__ = [
    'CONFIG',
    'load_config',
    'save_config',
    'update_config',
    'validate_config',
    'ConfigurationError',
    'ensure_directory_exists',
    'set_file_permissions'
]

"""Configuration management module."""

import os
from typing import Any, Dict


class ConfigManager:
    """Configuration manager class."""

    def __init__(self):
        """Initialize configuration manager."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.config: Dict[str, Any] = {
            "project_root": project_root,
            "log_level": "INFO",
            "max_parallel_jobs": 4,
            "disk_space_threshold": 90,
            "memory_threshold": 80,
            "cache_ttl": 86400,
            "cache_max_size": 1048576,
            "allow_file_creation": True,
            "allow_file_deletion": False,
            "backup_enabled": False,
            "github_repo": "",
            "github_branch": "main",
            "github_auto_sync": True,
            "github_sync_interval": 300,
        }
        self.load_env()
        self.load_config()

    def load_env(self) -> None:
        """Load configuration from .env file."""
        env_path = os.path.join(self.config["project_root"], ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip("\"'")
                        if key == "GITHUB_TOKEN":
                            self.config["github_token"] = value
                        elif key == "GITHUB_USERNAME":
                            self.config["github_username"] = value
                        elif key == "GITHUB_REPO":
                            self.config["github_repo"] = value

    def load_config(self) -> None:
        """Load configuration from settings.conf."""
        config_path = os.path.join(
            self.config["project_root"], "config", "settings.conf"
        )
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        try:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            # Convert string values to appropriate types
                            if value.lower() in ("true", "false"):
                                value = value.lower() == "true"
                            elif value.isdigit():
                                value = int(value)
                            self.config[key] = value
                        except ValueError:
                            continue

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

    def save(self) -> None:
        """Save configuration to file."""
        config_dir = os.path.join(self.config["project_root"], "config")
        os.makedirs(config_dir, exist_ok=True)

        config_path = os.path.join(config_dir, "settings.conf")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("# Project configuration\n")
            timestamp = os.popen("date").read().strip()
            f.write(f"# Generated at: {timestamp}\n\n")
            for key, value in sorted(self.config.items()):
                # Don't save sensitive data
                if key not in ("github_token", "github_username"):
                    f.write(f"{key}={value}\n")


# Global configuration instance
CONFIG = ConfigManager()

"""Dashboard configuration module."""

from typing import Dict, Any
import os
import json


class DashboardConfig:
    """Dashboard configuration management."""
    
    def __init__(self):
        """Initialize dashboard configuration."""
        self.config: Dict[str, Any] = {
            # Core settings
            "port": 8502,
            "theme": "light",
            "refresh_interval": 1,
            "verification_interval": 120,
            
            # Feature flags
            "features": {
                "historical_metrics": True,
                "predictive_analytics": True,
                "code_complexity": True,
                "technical_debt": True,
                "test_timing": True,
                "github_webhooks": True,
                "collaboration": True,
                "dark_mode": True,
                "cookie_consent": True
            },
            
            # Performance settings
            "cache_enabled": True,
            "cache_ttl": 300,
            "compression_enabled": True,
            "lazy_loading": True,
            
            # Visualization settings
            "charts": {
                "coverage_heatmap": True,
                "resource_trends": True,
                "code_quality": True,
                "test_distribution": True,
                "interactive_metrics": True
            },
            
            # Component settings
            "components": {
                "data_editor": {
                    "enabled": True,
                    "auto_save": True
                },
                "metric_cards": {
                    "enabled": True,
                    "animation": True
                },
                "alerts": {
                    "enabled": True,
                    "sound": False
                },
                "code_viewer": {
                    "enabled": True,
                    "syntax_highlight": True
                }
            },
            
            # Monitoring thresholds
            "thresholds": {
                "cpu_warning": 70,
                "cpu_critical": 85,
                "memory_warning": 75,
                "memory_critical": 90,
                "disk_warning": 80,
                "disk_critical": 90,
                "coverage_minimum": 80,
                "test_success_rate": 95
            },
            
            # UI customization
            "ui": {
                "sidebar_width": 250,
                "chart_height": 400,
                "animation_duration": 200,
                "font_family": "Inter, sans-serif",
                "custom_css": True
            }
        }
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        config_path = os.path.join(os.path.dirname(__file__), "dashboard_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config.update(json.load(f))
    
    def save_config(self) -> None:
        """Save configuration to file."""
        config_path = os.path.join(os.path.dirname(__file__), "dashboard_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
        self.save_config()

    def enable_feature(self, feature_name: str) -> None:
        """Enable a feature."""
        if feature_name in self.config["features"]:
            self.config["features"][feature_name] = True
            self.save_config()
    
    def disable_feature(self, feature_name: str) -> None:
        """Disable a feature."""
        if feature_name in self.config["features"]:
            self.config["features"][feature_name] = False
            self.save_config()
    
    def update_thresholds(self, thresholds: Dict[str, float]) -> None:
        """Update monitoring thresholds."""
        self.config["thresholds"].update(thresholds)
        self.save_config()
    
    def customize_ui(self, ui_settings: Dict[str, Any]) -> None:
        """Update UI customization settings."""
        self.config["ui"].update(ui_settings)
        self.save_config()


# Global configuration instance
DASHBOARD_CONFIG = DashboardConfig()

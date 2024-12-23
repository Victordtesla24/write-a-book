#!/usr/bin/env python3
"""Basic setup tests for the project."""

import os
import sys
import unittest

import psutil

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core_scripts.config_manager import (  # pylint: disable=wrong-import-position # noqa: E402
    CONFIG,
)


class TestBasicSetup(unittest.TestCase):
    """Test class for basic project setup verification."""

    def test_environment(self):
        """Test that environment is properly set up."""
        self.assertTrue(os.path.exists(".env"), "Environment file exists")
        self.assertTrue(os.path.exists("dashboard"), "Dashboard directory exists")
        self.assertTrue(os.path.exists("metrics"), "Metrics directory exists")

    def test_configuration(self):
        """Test configuration loading."""
        self.assertIsNotNone(CONFIG.get("project_root"), "Project root is configured")
        self.assertIsNotNone(CONFIG.get("log_level"), "Log level is configured")

    def test_metrics_collection(self):
        """Test metrics collection functionality."""
        # Test system metrics
        metrics = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
        }
        self.assertIsInstance(metrics["cpu_usage"], (int, float))
        self.assertIsInstance(metrics["memory_usage"], (int, float))
        self.assertIsInstance(metrics["disk_usage"], (int, float))


if __name__ == "__main__":
    unittest.main()

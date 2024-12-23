"""Metrics collection module."""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

import psutil
import requests

from core_scripts.config_manager import CONFIG


class MetricsCollector:
    """Metrics collector class."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics_dir = os.path.join(CONFIG.get('project_root'), 'metrics')
        os.makedirs(self.metrics_dir, exist_ok=True)

    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system metrics."""
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': time.time()
        }

    def collect_github_metrics(self) -> Optional[Dict[str, Any]]:
        """Collect GitHub metrics."""
        token = CONFIG.get('github_token')
        username = CONFIG.get('github_username')
        repo = CONFIG.get('github_repo')

        if not all([token, username, repo]):
            return None

        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        base_url = 'https://api.github.com'

        try:
            # Get repository info
            repo_url = f'{base_url}/repos/{username}/{repo}'
            repo_response = requests.get(repo_url, headers=headers, timeout=10)
            repo_data = repo_response.json()

            # Get commit activity
            commits_url = f'{repo_url}/commits'
            commits_response = requests.get(
                commits_url,
                headers=headers,
                params={'since': datetime.now().strftime('%Y-%m-%d')},
                timeout=10
            )
            commits_data = commits_response.json()

            return {
                'stars': repo_data.get('stargazers_count', 0),
                'forks': repo_data.get('forks_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0),
                'commits_today': len(commits_data),
                'timestamp': time.time()
            }
        except (requests.RequestException, KeyError, json.JSONDecodeError):
            return None

    def collect_test_metrics(self) -> Dict[str, Any]:
        """Collect test metrics."""
        coverage_file = os.path.join(
            CONFIG.get('project_root'), 'coverage', '.coverage'
        )
        if os.path.exists(coverage_file):
            try:
                # Import coverage only when needed
                import coverage  # pylint: disable=import-outside-toplevel
                cov = coverage.Coverage()
                cov.load()
                total = cov.report()
                return {
                    'coverage': total,
                    'timestamp': time.time()
                }
            except (ImportError, coverage.CoverageException):  # type: ignore
                pass
        return {
            'coverage': 0.0,
            'timestamp': time.time()
        }

    def save_metrics(self, metric_type: str, data: Dict[str, Any]) -> None:
        """Save metrics to file."""
        if not data:
            return

        filename = os.path.join(
            self.metrics_dir, f'{metric_type}_{int(time.time())}.json'
        )
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        # Cleanup old files
        retention_days = CONFIG.get('metrics_retention_days', 7)
        cutoff_time = time.time() - (retention_days * 86400)

        for old_file in os.listdir(self.metrics_dir):
            if not old_file.startswith(metric_type):
                continue
            file_path = os.path.join(self.metrics_dir, old_file)
            if os.path.getctime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                except OSError:
                    continue

    def collect_all(self) -> None:
        """Collect all metrics."""
        system_metrics = self.collect_system_metrics()
        self.save_metrics('system', system_metrics)

        github_metrics = self.collect_github_metrics()
        if github_metrics:
            self.save_metrics('github', github_metrics)

        test_metrics = self.collect_test_metrics()
        self.save_metrics('test', test_metrics)


# Global metrics collector instance
METRICS = MetricsCollector()

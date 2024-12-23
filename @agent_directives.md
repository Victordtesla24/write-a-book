# Rules for AI

[... existing content remains unchanged ...]

## Project Status Dashboard Implementation

### Core Components

1. Dashboard Structure (`serve_dashboard.py`):
```python
# Required imports
import os
import json
import time
import subprocess
from typing import Dict, Any, Optional
import streamlit as st
import plotly.graph_objects as go

# Core functions needed:
- load_latest_metrics(metric_type: str) -> Optional[Dict[str, Any]]
- load_project_status() -> Dict[str, Any]
- run_verification_scripts() -> None
- create_test_coverage_chart(status: Dict[str, Any]) -> go.Figure
- create_test_distribution(status: Dict[str, Any]) -> go.Figure
```

2. Required Metrics Files:
```
metrics/
├── system.json  # System health metrics
├── test.json    # Test execution metrics
└── proj_status.md  # Overall project status
```

3. Metrics File Formats:

```json
# system.json
{
    "cpu_usage": 6.99,      # CPU usage percentage
    "memory_usage": 45.2,   # Memory usage percentage
    "disk_usage": 48,       # Disk usage percentage
    "timestamp": 1734955409 # Unix timestamp
}

# test.json
{
    "coverage": 0.00,
    "tests_passed": 85,
    "tests_failed": 0,
    "test_suites": {
        "unit": {
            "total": 85,
            "passed": 85,
            "failed": 0,
            "coverage": 0.00
        },
        "integration": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "coverage": 0
        },
        "e2e": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "coverage": 0
        }
    },
    "last_run": "2024-12-23T12:03:29Z",
    "execution_time": 0,
    "timestamp": 1734955409
}

# proj_status.md format
Code Coverage: 85%
Lint Score: 8.5/10
Total Python Files: 25
Total Test Files: 15
Implementation Progress: In Progress
Total Tests: 85
Tests Passed: 85
Tests Failed: 0
Unit Tests: 75%
Integration Tests: 60%
End-to-End Tests: 40%
```

### Dashboard Features

1. Project Implementation Status:
   - Code Coverage
   - Code Quality (Lint Score)
   - Implementation Progress

2. Test Health:
   - Tests Passed/Failed
   - Total Tests
   - Success Rate
   - Test Coverage by Type Chart
   - Test Status Distribution Chart

3. System Health:
   - CPU Usage
   - Memory Usage
   - Disk Usage

4. Continuous Monitoring:
   - Auto-refresh every second
   - Verification scripts run every 2 minutes
   - Data staleness warnings (>5 minutes old)
   - Script execution status and duration

### Required Scripts

1. `verify_and_fix.sh`:
   - Run all tests
   - Update coverage metrics
   - Run linting checks
   - Auto-fix code issues
   - Update proj_status.md

2. `auto_fix_code.sh`:
   - Apply automated code fixes
   - Update metrics after fixes

### Dependencies

```requirements.txt
streamlit>=1.29.0
plotly>=5.18.0
pytest>=7.4.3
pytest-cov>=4.1.0
pylint>=3.0.3
```

### Dashboard Configuration

```toml
# .streamlit/config.toml
[server]
port = 8502
enableCORS = true
enableXsrfProtection = false

[theme]
primaryColor = "#00cc96"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

### Implementation Steps

1. Create directory structure:
```bash
mkdir -p metrics .streamlit
touch metrics/system.json metrics/test.json proj_status.md
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create required scripts:
```bash
chmod +x scripts/verify_and_fix.sh scripts/auto_fix_code.sh
```

4. Run dashboard:
```bash
streamlit run serve_dashboard.py --server.port 8502
```

### Metrics Update Flow

1. Verification scripts run every 2 minutes:
   ```mermaid
   graph TD
   A[Dashboard] -->|Every 2 min| B[verify_and_fix.sh]
   B --> C[Run Tests]
   C --> D[Update Coverage]
   D --> E[Run Linting]
   E --> F[Update proj_status.md]
   F --> G[Update Metrics]
   G --> A
   ```

2. Real-time monitoring:
   - Dashboard checks metrics freshness
   - Warns if data is stale (>5 min)
   - Shows countdown to next verification
   - Displays script execution status

### Error Handling

1. Metrics Loading:
   - Default values if files missing
   - Type checking for all metrics
   - Graceful degradation of features

2. Script Execution:
   - Capture and display script output
   - Show execution duration
   - Error messages for failed runs

3. Data Validation:
   - Convert string values to appropriate types
   - Handle missing or invalid metrics
   - Fallback to default values when needed

[... rest of existing content remains unchanged ...] 
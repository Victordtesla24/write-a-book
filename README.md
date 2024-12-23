# Project Management Dashboard

A real-time project management dashboard with GitHub integration, system metrics monitoring, and test coverage tracking.

## Features

- Real-time system metrics monitoring (CPU, memory, disk usage)
- GitHub integration (stars, forks, issues, commits)
- Test coverage tracking
- Project health status
- Auto-refresh functionality

## Requirements

- Python 3.8 or higher
- GitHub account and personal access token
- Unix-like operating system (Linux, macOS)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/write-a-book.git
cd write-a-book
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Create a `.env` file in the project root with your GitHub credentials:
```bash
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username
GITHUB_REPO=write-a-book

# Project Configuration
PROJECT_NAME=write-a-book
PROJECT_VERSION=0.1.0

# System Configuration
LOG_LEVEL=INFO
MONITORING_INTERVAL=300
METRICS_RETENTION_DAYS=7

# Security Configuration
ALLOW_FILE_CREATION=true
ALLOW_FILE_DELETION=false
BACKUP_ENABLED=false

# Test Configuration
TEST_COVERAGE_THRESHOLD=80
TEST_PARALLEL_JOBS=4
```

## Usage

1. Start the dashboard:
```bash
streamlit run serve_dashboard.py
```

2. Open your browser and navigate to:
```
http://localhost:8501
```

The dashboard will automatically refresh every minute and display:
- System health metrics
- GitHub repository statistics
- Test coverage information
- Overall project status

## Development

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest
```

3. Run linters:
```bash
pylint core_scripts tests
black core_scripts tests
mypy core_scripts tests
```

## Project Structure

```
write-a-book/
├── core_scripts/           # Core functionality
│   ├── __init__.py
│   ├── config_manager.py   # Configuration management
│   └── metrics_collector.py # Metrics collection
├── tests/                  # Test suite
│   └── test_basic.py
├── metrics/                # Metrics storage
├── dashboard/             # Dashboard UI
├── .env                   # Environment configuration
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
├── setup.cfg             # Package configuration
├── setup.py              # Package setup
└── serve_dashboard.py    # Dashboard server
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
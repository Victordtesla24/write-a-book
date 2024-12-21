#!/bin/bash

# Set up logging
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/setup_env.log"
mkdir -p "$LOG_DIR"
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

# Exit on error
set -e
set -o pipefail

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Function to verify other scripts
verify_scripts() {
    local scripts=("verify_and_fix.sh" "auto_fix_code.sh")
    local missing=()
    
    for script in "${scripts[@]}"; do
        if [ ! -f "scripts/$script" ]; then
            missing+=("$script")
        elif [ ! -x "scripts/$script" ]; then
            chmod +x "scripts/$script"
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        error_log "Missing required scripts: ${missing[*]}"
        return 1
    fi
    return 0
}

# Function to setup Python environment
setup_python_env() {
    log "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/upgrade pip
    python -m pip install --upgrade pip
    
    # Install base requirements
    pip install -q streamlit python-dotenv pytest pytest-cov black isort pylint autoflake autopep8 flake8
    
    # Install project in development mode if setup.py exists
    if [ -f "setup.py" ]; then
        pip install -q -e ".[dev]"
    fi
}

# Function to setup git repository
setup_git() {
    log "Setting up git repository..."
    
    if [ ! -d ".git" ]; then
        git init
        
        # Create .gitignore if it doesn't exist
        if [ ! -f ".gitignore" ]; then
            cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
cursor_env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db
EOL
        fi
        
        # Initial commit
        git add .
        git commit -m "Initial commit" || true
    fi
}

# Function to create project structure
create_project_structure() {
    log "Creating project structure..."
    
    # Create directories
    mkdir -p src tests docs scripts logs
    mkdir -p .streamlit static/images static/css
    
    # Create __init__.py files
    touch src/__init__.py tests/__init__.py
    
    # Create basic setup.py if it doesn't exist
    if [ ! -f "setup.py" ]; then
        cat > setup.py << EOL
from setuptools import setup, find_packages

setup(
    name="book-editor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "python-dotenv",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "pylint",
        ],
    },
)
EOL
    fi
    
    # Create Streamlit config if it doesn't exist
    if [ ! -f ".streamlit/config.toml" ]; then
        mkdir -p .streamlit
        cat > .streamlit/config.toml << EOL
[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
enableCORS = false
headless = true
EOL
    fi
}

# Function to verify setup
verify_setup() {
    log "Verifying setup..."
    local errors=0
    
    # Check Python environment
    if [ ! -d "venv" ]; then
        error_log "Virtual environment not created"
        errors=$((errors + 1))
    fi
    
    # Check project structure
    for dir in src tests docs scripts logs .streamlit static/images static/css; do
        if [ ! -d "$dir" ]; then
            error_log "Directory $dir not created"
            errors=$((errors + 1))
        fi
    done
    
    # Check key files
    for file in setup.py .streamlit/config.toml .gitignore; do
        if [ ! -f "$file" ]; then
            error_log "File $file not created"
            errors=$((errors + 1))
        fi
    done
    
    if [ $errors -gt 0 ]; then
        error_log "Setup verification failed with $errors errors"
        return 1
    fi
    
    log "Setup verification completed successfully"
    return 0
}

# Main function
main() {
    log "Starting environment setup..."
    
    # Verify other scripts first
    if ! verify_scripts; then
        error_log "Required scripts missing. Please ensure all scripts are present."
        exit 1
    fi
    
    # Run setup steps
    create_project_structure
    setup_python_env
    setup_git
    
    # Verify setup
    if ! verify_setup; then
        error_log "Setup verification failed"
        exit 1
    fi
    
    log "Environment setup completed successfully"
    
    # Run verify_and_fix.sh if available
    if [ -x "scripts/verify_and_fix.sh" ]; then
        log "Running verification and fixes..."
        ./scripts/verify_and_fix.sh --init
    fi
}

# Run main function
main 
#!/bin/bash

# Setup test environment script
# Follows agent_directives.md for test environment setup

set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load core scripts
source "${PROJECT_ROOT}/core_scripts/config_manager.sh"
source "${PROJECT_ROOT}/core_scripts/resource_manager.sh"

# Initialize logging
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "${LOG_DIR}"
SETUP_LOG="${LOG_DIR}/setup_test_env.log"
ERROR_LOG="${LOG_DIR}/error.log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}"
    echo "[${timestamp}] [${level}] ${message}" >> "${SETUP_LOG}"
}

# Function to create test environment structure
create_test_env() {
    log "INFO" "Creating test environment structure..."
    
    # Create test directories
    mkdir -p "${PROJECT_ROOT}/tests/unit"
    mkdir -p "${PROJECT_ROOT}/tests/integration"
    mkdir -p "${PROJECT_ROOT}/tests/fixtures"
    
    # Create __init__.py files
    touch "${PROJECT_ROOT}/tests/__init__.py"
    touch "${PROJECT_ROOT}/tests/unit/__init__.py"
    touch "${PROJECT_ROOT}/tests/integration/__init__.py"
    
    # Create conftest.py if it doesn't exist
    if [[ ! -f "${PROJECT_ROOT}/tests/conftest.py" ]]; then
        cat > "${PROJECT_ROOT}/tests/conftest.py" << 'EOF'
"""Test configuration and fixtures."""

import pytest
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_data():
    """Provide test data."""
    return {
        'sample': 'data'
    }
EOF
    fi
}

# Function to set up Python virtual environment
setup_venv() {
    log "INFO" "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv "${PROJECT_ROOT}/venv" || {
        log "ERROR" "Failed to create virtual environment"
        return 1
    }
    
    # Activate virtual environment
    source "${PROJECT_ROOT}/venv/bin/activate" || {
        log "ERROR" "Failed to activate virtual environment"
        return 1
    }
    
    # Install test dependencies
    pip install pytest pytest-cov pytest-mock pylint mypy black isort || {
        log "ERROR" "Failed to install test dependencies"
        return 1
    }
    
    return 0
}

# Function to create sample test data
create_test_data() {
    log "INFO" "Creating sample test data..."
    
    # Create sample test file
    cat > "${PROJECT_ROOT}/tests/unit/test_sample.py" << 'EOF'
"""Sample test module."""

def test_sample():
    """Test sample function."""
    assert True, "Basic test should pass"

def test_import():
    """Test imports work correctly."""
    try:
        import pytest
        assert True
    except ImportError:
        pytest.fail("Failed to import pytest")
EOF
}

# Function to verify test environment
verify_test_env() {
    log "INFO" "Verifying test environment..."
    
    # Check virtual environment
    if [[ ! -d "${PROJECT_ROOT}/venv" ]]; then
        log "ERROR" "Virtual environment not found"
        return 1
    fi
    
    # Check test directories
    if [[ ! -d "${PROJECT_ROOT}/tests/unit" ]] || \
       [[ ! -d "${PROJECT_ROOT}/tests/integration" ]] || \
       [[ ! -d "${PROJECT_ROOT}/tests/fixtures" ]]; then
        log "ERROR" "Test directories not found"
        return 1
    fi
    
    # Run sample test
    pytest "${PROJECT_ROOT}/tests/unit/test_sample.py" -v >> "${ERROR_LOG}" || {
        log "ERROR" "Sample test failed"
        return 1
    }
    
    return 0
}

# Main execution
main() {
    log "INFO" "Starting test environment setup..."
    
    # Create iteration counter
    local iteration=1
    local max_iterations=3
    local errors_found=true
    
    while [[ ${errors_found} == true && ${iteration} -le ${max_iterations} ]]; do
        log "INFO" "Starting setup iteration ${iteration}"
        
        # Run all setup steps
        create_test_env
        setup_venv
        create_test_data
        verify_test_env
        
        # Check if any errors remain
        if [[ -f "${ERROR_LOG}" ]]; then
            error_count=$(grep -c "ERROR\|CRITICAL" "${ERROR_LOG}")
            if [[ ${error_count} -eq 0 ]]; then
                errors_found=false
                log "INFO" "Test environment setup completed successfully"
            else
                log "WARN" "Found ${error_count} errors after iteration ${iteration}"
                if [[ ${iteration} -eq ${max_iterations} ]]; then
                    log "ERROR" "Max iterations reached. Manual intervention required."
                    cat "${ERROR_LOG}"
                    exit 1
                fi
            fi
        else
            errors_found=false
            log "INFO" "No errors found"
        fi
        
        iteration=$((iteration + 1))
    done
    
    log "INFO" "Test environment setup completed successfully"
}

# Execute main function
main "$@" 

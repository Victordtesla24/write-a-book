#!/bin/sh

# Auto-fix script for code issues
# Automatically fixes common code issues and updates metrics

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Initialize logging
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "${LOG_DIR}"
AUTO_FIX_LOG="${LOG_DIR}/auto_fix.log"

log() {
    level="$1"
    message="$2"
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}"
    echo "[${timestamp}] [${level}] ${message}" >> "${AUTO_FIX_LOG}"
}

# Function to fix Python code style
fix_python_style() {
    log "INFO" "Fixing Python code style..."
    
    # Create a temporary file to store file hashes before formatting
    hash_before=$(find "${PROJECT_ROOT}/src" "${PROJECT_ROOT}/tests" -name "*.py" -type f -exec sha256sum {} \; | sort)
    
    # Run isort first (imports)
    if command -v isort > /dev/null; then
        isort --profile black --combine-as --combine-star --remove-redundant-aliases "${PROJECT_ROOT}/src" "${PROJECT_ROOT}/tests" 2>&1 || true
    fi
    
    # Then run black (formatting)
    if command -v black > /dev/null; then
        black --quiet --line-length 100 "${PROJECT_ROOT}/src" "${PROJECT_ROOT}/tests" 2>&1 || true
    fi
    
    # Run autopep8 for additional fixes
    if command -v autopep8 > /dev/null; then
        find "${PROJECT_ROOT}/src" "${PROJECT_ROOT}/tests" -name "*.py" -type f -exec autopep8 --in-place --aggressive --aggressive --max-line-length 100 {} + 2>&1 || true
    fi
    
    # Check if any files were actually changed
    hash_after=$(find "${PROJECT_ROOT}/src" "${PROJECT_ROOT}/tests" -name "*.py" -type f -exec sha256sum {} \; | sort)
    if [ "${hash_before}" = "${hash_after}" ]; then
        log "INFO" "No formatting changes needed"
    else
        log "INFO" "Formatting changes applied"
    fi
}

# Function to fix Python type hints
fix_type_hints() {
    log "INFO" "Fixing type hints..."
    
    # Run pytype for type checking and fixing
    if command -v pytype > /dev/null; then
        pytype --keep-going --output-errors-csv "${PROJECT_ROOT}/metrics/type_errors.csv" "${PROJECT_ROOT}/src" 2>&1 || true
        
        # Fix missing type hints using monkeytype
        if command -v monkeytype > /dev/null; then
            find "${PROJECT_ROOT}/src" -name "*.py" -type f -exec sh -c '
                module_path=$(echo "{}" | sed "s|${PROJECT_ROOT}/||" | sed "s|\.py$||" | tr "/" ".")
                monkeytype run "{}"
                monkeytype apply "${module_path}"
            ' \; 2>&1 || true
        fi
    fi
    
    # Run mypy to check remaining type issues
    if command -v mypy > /dev/null; then
        mypy --ignore-missing-imports --disallow-untyped-defs "${PROJECT_ROOT}/src" > "${LOG_DIR}/type_check.log" 2>&1 || true
    fi
}

# Function to fix linting issues
fix_lint_issues() {
    log "INFO" "Fixing linting issues..."
    
    # Run pylint and collect issues
    if command -v pylint > /dev/null; then
        pylint --output-format=json "${PROJECT_ROOT}/src" > "${LOG_DIR}/pylint.json" 2>&1 || true
        
        # Fix common issues using autopep8
        if command -v autopep8 > /dev/null; then
            find "${PROJECT_ROOT}/src" -name "*.py" -type f -exec autopep8 --in-place --aggressive --aggressive \
                --max-line-length 100 \
                --ignore E226,E302,E41 \
                {} + 2>&1 || true
        fi
        
        # Fix import issues using autoflake
        if command -v autoflake > /dev/null; then
            find "${PROJECT_ROOT}/src" -name "*.py" -type f -exec autoflake --in-place --remove-all-unused-imports {} + 2>&1 || true
        fi
        
        # Fix docstring issues using docformatter
        if command -v docformatter > /dev/null; then
            find "${PROJECT_ROOT}/src" -name "*.py" -type f -exec docformatter --in-place --wrap-summaries 100 --wrap-descriptions 100 {} + 2>&1 || true
        fi
    fi
}

# Function to update metrics after fixes
update_metrics() {
    log "INFO" "Updating metrics after fixes..."
    
    # Run update_status.sh to refresh metrics
    "${PROJECT_ROOT}/scripts/update_status.sh"
}

# Main execution
main() {
    log "INFO" "Starting auto-fix process..."
    
    # Run all fixes
    fix_python_style
    fix_type_hints
    fix_lint_issues
    
    # Update metrics after fixes
    update_metrics
    
    log "INFO" "Auto-fix process completed successfully"
}

# Execute main function
main "$@"
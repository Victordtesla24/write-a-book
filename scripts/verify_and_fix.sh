#!/bin/sh

# Verify and fix script
# Follows agent_directives.md for project verification and fixes

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Initialize logging
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "${LOG_DIR}"
VERIFY_LOG="${LOG_DIR}/verify_and_fix.log"
ERROR_LOG="${LOG_DIR}/error.log"

log() {
    level="$1"
    message="$2"
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}"
    echo "[${timestamp}] [${level}] ${message}" >> "${VERIFY_LOG}"
}

# Function to verify Python code
verify_python() {
    log "INFO" "Verifying Python code..."
    errors_found=false
    
    # Run pylint
    if command -v pylint > /dev/null; then
        pylint "${PROJECT_ROOT}/src" > "${ERROR_LOG}" 2>&1 || true
        
        if [ -f "${ERROR_LOG}" ]; then
            error_count=$(grep -c "ERROR\|CRITICAL" "${ERROR_LOG}" || echo "0")
            if [ "$error_count" -gt 0 ] 2>/dev/null; then
                log "ERROR" "Found ${error_count} Python errors"
                errors_found=true
                
                # Extract error messages for fixing
                grep "ERROR:\|CRITICAL:" "${ERROR_LOG}" > "${LOG_DIR}/python_errors.txt"
                
                # Run auto-fix for these specific errors
                "${PROJECT_ROOT}/scripts/auto_fix_code.sh"
                
                # Verify if errors were fixed
                pylint "${PROJECT_ROOT}/src" > "${ERROR_LOG}.new" 2>&1 || true
                new_error_count=$(grep -c "ERROR\|CRITICAL" "${ERROR_LOG}.new" || echo "0")
                
                if [ "$new_error_count" -lt "$error_count" ] 2>/dev/null; then
                    log "INFO" "Fixed $((error_count - new_error_count)) errors"
                else
                    log "WARN" "Could not fix all errors automatically"
                fi
            fi
        fi
    fi
    
    # Run mypy
    if command -v mypy > /dev/null; then
        mypy --ignore-missing-imports --disallow-untyped-defs "${PROJECT_ROOT}/src" > "${LOG_DIR}/type_check.log" 2>&1
        type_errors=$(grep -c "error:" "${LOG_DIR}/type_check.log" || echo "0")
        
        if [ "$type_errors" -gt 0 ] 2>/dev/null; then
            log "WARN" "Found ${type_errors} type errors"
            errors_found=true
            
            # Extract type errors for fixing
            grep "error:" "${LOG_DIR}/type_check.log" > "${LOG_DIR}/type_errors.txt"
            
            # Run type hint fixes
            "${PROJECT_ROOT}/scripts/auto_fix_code.sh"
            
            # Verify if errors were fixed
            mypy --ignore-missing-imports --disallow-untyped-defs "${PROJECT_ROOT}/src" > "${LOG_DIR}/type_check.log.new" 2>&1
            new_type_errors=$(grep -c "error:" "${LOG_DIR}/type_check.log.new" || echo "0")
            
            if [ "$new_type_errors" -lt "$type_errors" ] 2>/dev/null; then
                log "INFO" "Fixed $((type_errors - new_type_errors)) type errors"
            else
                log "WARN" "Could not fix all type errors automatically"
            fi
        fi
    fi
    
    if [ "${errors_found}" = true ]; then
        return 1
    fi
    return 0
}

# Function to verify tests
verify_tests() {
    log "INFO" "Verifying tests..."
    
    # Run pytest with coverage
    if command -v pytest > /dev/null; then
        # Clean up previous coverage data
        coverage erase
        
        # Set PYTHONPATH to include source directories
        export PYTHONPATH="${PROJECT_ROOT}/src:${PROJECT_ROOT}/core_scripts:${PROJECT_ROOT}/tests:${PYTHONPATH}"
        
        # Create metrics directory if it doesn't exist
        mkdir -p "${PROJECT_ROOT}/metrics"
        
        # Run tests with coverage
        coverage run --source="${PROJECT_ROOT}/src,${PROJECT_ROOT}/core_scripts" -m pytest "${PROJECT_ROOT}/tests" > "${ERROR_LOG}" 2>&1 || {
            log "ERROR" "Tests failed"
            
            # Extract test failures
            grep "FAILED" "${ERROR_LOG}" > "${LOG_DIR}/test_failures.txt"
            
            # Try to fix test failures
            if [ -s "${LOG_DIR}/test_failures.txt" ]; then
                log "INFO" "Attempting to fix test failures..."
                "${PROJECT_ROOT}/scripts/auto_fix_code.sh"
            fi
            
            return 1
        }
        
        # Combine coverage data if parallel mode is enabled
        coverage combine 2>/dev/null || true
        
        # Generate coverage reports
        coverage report --include="src/*,core_scripts/*" > "${PROJECT_ROOT}/metrics/coverage.txt" || {
            log "ERROR" "Failed to generate coverage report"
            cat "${ERROR_LOG}"
            return 1
        }
        coverage html || true
        
        # Check if coverage report exists and has content
        if [ ! -s "${PROJECT_ROOT}/metrics/coverage.txt" ]; then
            log "ERROR" "Coverage report is empty"
            return 1
        fi
        
        # Extract coverage data from the TOTAL line
        if ! total_line=$(grep "^TOTAL" "${PROJECT_ROOT}/metrics/coverage.txt"); then
            log "ERROR" "Could not find TOTAL line in coverage report"
            return 1
        fi
        
        # Parse coverage percentage from the last field (removing %)
        total_coverage=$(echo "${total_line}" | awk '{gsub(/%/, "", $NF); print $NF}')
        if [ -z "${total_coverage}" ]; then
            log "ERROR" "Could not parse coverage percentage"
            return 1
        fi
        
        # Validate coverage is a reasonable number
        if ! echo "${total_coverage}" | grep -q "^[0-9][0-9]*\(\.[0-9][0-9]*\)\?$" || [ "$(echo "${total_coverage}" | cut -d. -f1)" -gt 100 ]; then
            log "ERROR" "Invalid coverage percentage: ${total_coverage}%"
            return 1
        fi
        
        # Convert to integer by truncating decimal part
        coverage_int=${total_coverage%.*}
        if [ -n "${coverage_int}" ] && [ "${coverage_int:-0}" -lt 40 ] 2>/dev/null; then
            log "WARN" "Coverage below threshold: ${total_coverage}%"
            log "INFO" "Attempting to improve test coverage..."
            
            # Generate coverage report to see what needs testing
            coverage report --show-missing > "${LOG_DIR}/coverage_missing.txt"
            
            # Try to fix coverage issues
            "${PROJECT_ROOT}/scripts/auto_fix_code.sh"
        else
            log "INFO" "Coverage at ${total_coverage}%"
        fi
        
        # Extract detailed test metrics
        total_tests=$(grep -o "[0-9]* items" "${ERROR_LOG}" | head -1 | awk '{print $1}' || echo "0")
        passed_tests=$(grep -o "[0-9]* passed" "${ERROR_LOG}" | head -1 | awk '{print $1}' || echo "0")
        failed_tests=$(grep -o "[0-9]* failed" "${ERROR_LOG}" | head -1 | awk '{print $1}' || echo "0")
        skipped_tests=$(grep -o "[0-9]* skipped" "${ERROR_LOG}" | head -1 | awk '{print $1}' || echo "0")
        
        log "INFO" "Test Results:"
        log "INFO" "  Total Tests: ${total_tests}"
        log "INFO" "  Passed: ${passed_tests}"
        log "INFO" "  Failed: ${failed_tests}"
        log "INFO" "  Skipped: ${skipped_tests}"
        log "INFO" "  Coverage: ${total_coverage}%"
    else
        log "ERROR" "pytest not found"
        return 1
    fi
    
    return 0
}

# Function to update metrics
update_metrics() {
    log "INFO" "Updating metrics..."
    
    # Create metrics directory if it doesn't exist
    mkdir -p "${PROJECT_ROOT}/metrics"
    
    # Update test metrics
    if [ -f "${PROJECT_ROOT}/metrics/coverage.txt" ]; then
        # Parse coverage percentage from the TOTAL line
        total_line=$(grep "^TOTAL" "${PROJECT_ROOT}/metrics/coverage.txt")
        coverage=$(echo "${total_line}" | awk '{gsub(/%/, "", $NF); print $NF}')
        
        # Validate coverage is a reasonable number
        if ! echo "${coverage}" | grep -q "^[0-9][0-9]*\(\.[0-9][0-9]*\)\?$" || [ "$(echo "${coverage}" | cut -d. -f1)" -gt 100 ]; then
            log "ERROR" "Invalid coverage percentage: ${coverage}%"
            coverage=0
        fi
        
        # Parse test results
        passed=$(grep -o "[0-9]* passed" "${ERROR_LOG}" | head -1 | awk '{print $1}' || echo "0")
        failed=$(grep -o "[0-9]* failed" "${ERROR_LOG}" | head -1 | awk '{print $1}' || echo "0")
        
        cat > "${PROJECT_ROOT}/metrics/test.json" << EOF
{
    "coverage": ${coverage:-0},
    "tests_passed": ${passed:-0},
    "tests_failed": ${failed:-0},
    "test_suites": {
        "unit": {
            "total": ${passed:-0},
            "passed": ${passed:-0},
            "failed": ${failed:-0},
            "coverage": ${coverage:-0}
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
    "last_run": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "execution_time": 0,
    "timestamp": $(date +%s)
}
EOF
    fi
    
    # Update system metrics
    top -l 1 > /tmp/top.txt
    cpu=$(grep "CPU usage" /tmp/top.txt | awk '{print $3}' | tr -d '%')
    memory=$(grep "PhysMem" /tmp/top.txt | awk '{print $2}' | tr -d 'M')
    disk=$(df -h . | tail -1 | awk '{print $5}' | tr -d '%')
    
    cat > "${PROJECT_ROOT}/metrics/system.json" << EOF
{
    "cpu_usage": ${cpu:-0},
    "memory_usage": ${memory:-0},
    "disk_usage": ${disk:-0},
    "timestamp": $(date +%s)
}
EOF
    
    rm -f /tmp/top.txt
    
    # Update project status
    "${PROJECT_ROOT}/scripts/update_status.sh"
    
    # Sync with GitHub
    log "INFO" "Syncing with GitHub..."
    if ! "${PROJECT_ROOT}/scripts/github_sync.sh"; then
        log "ERROR" "Failed to sync with GitHub"
        return 1
    fi
    
    log "INFO" "Metrics updated successfully"
}

# Main execution
main() {
    log "INFO" "Starting verification and fix process..."
    
    # Create iteration counter
    iteration=1
    max_iterations=3
    errors_found=true
    
    while [ "${errors_found}" = true ] && [ "${iteration}" -le "${max_iterations}" ]; do
        log "INFO" "Starting verification iteration ${iteration}"
        
        # Run verifications
        verify_python
        verify_tests
        
        # Check if any errors remain
        if [ -f "${ERROR_LOG}" ]; then
            error_count=$(grep -c "ERROR\|CRITICAL" "${ERROR_LOG}" || echo "0")
            if [ "$error_count" -eq 0 ] 2>/dev/null; then
                errors_found=false
                log "INFO" "All verifications passed successfully"
            else
                log "WARN" "Found ${error_count} errors after iteration ${iteration}"
                if [ "${iteration}" -eq "${max_iterations}" ]; then
                    log "ERROR" "Max iterations reached. Manual intervention required."
                    cat "${ERROR_LOG}"
                    exit 1
                fi
                
                # Run auto-fix script
                "${PROJECT_ROOT}/scripts/auto_fix_code.sh"
            fi
        else
            errors_found=false
            log "INFO" "No errors found"
        fi
        
        iteration=$((iteration + 1))
    done
    
    # Update metrics after verification
    update_metrics
    
    log "INFO" "Verification and fix process completed successfully"
}

# Execute main function
main "$@"


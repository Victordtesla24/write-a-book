#!/bin/sh

# Update status script
# Updates project status metrics and generates status report

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Initialize logging
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "${LOG_DIR}"
STATUS_LOG="${LOG_DIR}/status.log"

log() {
    level="$1"
    message="$2"
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}"
    echo "[${timestamp}] [${level}] ${message}" >> "${STATUS_LOG}"
}

# Function to get test coverage
get_coverage() {
    if [ -f "${PROJECT_ROOT}/metrics/coverage.txt" ]; then
        coverage=$(grep "TOTAL" "${PROJECT_ROOT}/metrics/coverage.txt" | awk '{print $NF}' | tr -d '%')
        echo "${coverage:-0}"
    else
        echo "0"
    fi
}

# Function to get lint score
get_lint_score() {
    if command -v pylint > /dev/null; then
        score=$(pylint "${PROJECT_ROOT}/src" 2>/dev/null | grep "Your code has been rated at" | cut -d' ' -f7 | cut -d'/' -f1)
        echo "${score:-0}"
    else
        echo "0"
    fi
}

# Function to count Python files
count_python_files() {
    total=$(find "${PROJECT_ROOT}/src" -name "*.py" -type f | wc -l | tr -d ' ')
    echo "${total:-0}"
}

# Function to count test files
count_test_files() {
    total=$(find "${PROJECT_ROOT}/tests" -name "test_*.py" -type f | wc -l | tr -d ' ')
    echo "${total:-0}"
}

# Function to get test results
get_test_results() {
    if [ -f "${PROJECT_ROOT}/metrics/test.json" ]; then
        passed=$(jq -r '.tests_passed' "${PROJECT_ROOT}/metrics/test.json")
        failed=$(jq -r '.tests_failed' "${PROJECT_ROOT}/metrics/test.json")
        echo "${passed:-0} ${failed:-0}"
    else
        echo "0 0"
    fi
}

# Function to calculate test pass rate
calculate_pass_rate() {
    tests_passed=$1
    tests_failed=$2
    total_tests=$((tests_passed + tests_failed))
    
    if [ "${total_tests}" -eq 0 ]; then
        echo "0"
    else
        echo "$((tests_passed * 100 / total_tests))"
    fi
}

# Function to update project status
update_project_status() {
    log "INFO" "Starting status update process..."
    
    # Get test metrics
    if [ -f "${PROJECT_ROOT}/metrics/test.json" ]; then
        tests_passed=$(jq -r '.tests_passed' "${PROJECT_ROOT}/metrics/test.json")
        tests_failed=$(jq -r '.tests_failed' "${PROJECT_ROOT}/metrics/test.json")
        coverage=$(jq -r '.coverage' "${PROJECT_ROOT}/metrics/test.json")
    else
        tests_passed=0
        tests_failed=0
        coverage=0
    fi
    
    # Calculate pass rate
    pass_rate=$(calculate_pass_rate "${tests_passed}" "${tests_failed}")
    
    # Update proj_status.md
    cat > "${PROJECT_ROOT}/proj_status.md" << EOF
# Project Status

## Test Health
- Total Tests: $((tests_passed + tests_failed))
- Tests Passed: ${tests_passed}
- Tests Failed: ${tests_failed}
- Pass Rate: ${pass_rate}%
- Coverage: ${coverage}%

## Implementation Status
- Code Coverage: ${coverage}%
- Code Quality: ${pass_rate}%
- Implementation Progress: In Progress

Last Updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF
    
    log "INFO" "Project status markdown updated successfully"
}

# Main execution
main() {
    log "INFO" "Starting status update process..."
    
    # Update project status markdown
    update_project_status
    
    log "INFO" "Status update process completed successfully"
}

# Execute main function
main "$@" 
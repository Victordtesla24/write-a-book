#!/bin/zsh

# GitHub synchronization script
# Handles automated commits, pushes, and pulls

set -e

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Load configuration
source "${PROJECT_ROOT}/core_scripts/config_manager.sh"

# Initialize logging
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "${LOG_DIR}"
SYNC_LOG="${LOG_DIR}/github_sync.log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${SYNC_LOG}"
}

# Generate commit message from project status
generate_commit_message() {
    local message=""
    local proj_status="${PROJECT_ROOT}/docs/proj_status.md"
    local test_metrics="${PROJECT_ROOT}/metrics/test.json"
    
    # Get test results
    if [ -f "${test_metrics}" ]; then
        local tests_passed=$(jq -r '.tests_passed' "${test_metrics}")
        local tests_failed=$(jq -r '.tests_failed' "${test_metrics}")
        local coverage=$(jq -r '.coverage' "${test_metrics}")
        message="Test Results: ${tests_passed} passed, ${tests_failed} failed - Coverage: ${coverage}%"
    fi
    
    # Get implementation status
    if [ -f "${proj_status}" ]; then
        local python_files=$(grep "Python files updated:" "${proj_status}" | awk '{print $NF}')
        local test_files=$(grep "Test files updated:" "${proj_status}" | awk '{print $NF}')
        message="${message} - Files: ${python_files} Python, ${test_files} Tests"
    fi
    
    # Get lint score
    if [ -f "${proj_status}" ]; then
        local lint_score=$(grep "Pylint Score:" "${proj_status}" | awk '{print $NF}')
        message="${message} - Lint: ${lint_score}"
    fi
    
    echo "${message}"
}

# Check GitHub configuration
check_github_config() {
    local errors=0
    
    if [[ -z "${CONFIG[github_token]}" ]]; then
        log "ERROR" "GitHub token not configured"
        errors=$((errors + 1))
    fi
    
    if [[ -z "${CONFIG[github_username]}" ]]; then
        log "ERROR" "GitHub username not configured"
        errors=$((errors + 1))
    fi
    
    if [[ -z "${CONFIG[github_repo]}" ]]; then
        log "ERROR" "GitHub repository not configured"
        errors=$((errors + 1))
    fi
    
    return "${errors}"
}

# Sync with GitHub
sync_with_github() {
    log "INFO" "Starting GitHub sync"
    
    # Change to project root
    cd "${PROJECT_ROOT}"
    
    # Initialize git if needed
    if [ ! -d .git ]; then
        git init
        git remote add origin "https://github.com/${CONFIG[github_username]}/${CONFIG[github_repo]}.git"
    fi
    
    # Configure git credentials
    git config user.name "${CONFIG[github_username]}"
    git config user.email "${CONFIG[github_username]}@users.noreply.github.com"
    
    # Pull latest changes
    if ! git pull origin "${CONFIG[github_branch]}" | cat; then
        log "ERROR" "Failed to pull from GitHub"
        return 1
    fi
    
    # Check for changes
    if [[ -n "$(git status --porcelain)" ]]; then
        # Stage all changes
        git add -A
        
        # Generate commit message
        local commit_msg=$(generate_commit_message)
        if [[ -z "${commit_msg}" ]]; then
            commit_msg="Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"
        fi
        
        # Create commit
        git commit -m "${commit_msg}"
        
        # Push changes
        if ! git push origin "${CONFIG[github_branch]}" | cat; then
            log "ERROR" "Failed to push to GitHub"
            return 1
        fi
        
        log "INFO" "Changes committed with message: ${commit_msg}"
    else
        log "INFO" "No changes to sync"
    fi
    
    log "INFO" "GitHub sync completed"
    return 0
}

# Main execution
main() {
    if ! check_github_config; then
        log "ERROR" "GitHub configuration check failed"
        return 1
    fi
    
    if ! sync_with_github; then
        log "ERROR" "GitHub sync failed"
        return 1
    fi
    
    return 0
}

# Run if executed directly
if [[ "${(%):-%x}" == "${0}" ]]; then
    main
fi 
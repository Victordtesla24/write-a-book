#!/bin/zsh

# Progress reporter script
# Handles progress tracking and reporting

set -e

# Load configuration
source "$(dirname "$0")/config_manager.sh"

# Initialize logging
LOG_DIR="${CONFIG[project_root]}/logs"
mkdir -p "${LOG_DIR}"
REPORT_LOG="${LOG_DIR}/progress.log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${REPORT_LOG}"
}

# Generate GitHub metrics report
generate_github_report() {
    local report_file="${CONFIG[project_root]}/reports/github_metrics.md"
    mkdir -p "$(dirname "${report_file}")"
    
    # Read metrics files
    local github_metrics="${CONFIG[project_root]}/metrics/github.json"
    local commits_metrics="${CONFIG[project_root]}/metrics/commits.json"
    local pulls_metrics="${CONFIG[project_root]}/metrics/pulls.json"
    
    {
        echo "# GitHub Metrics Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo
        echo "## Repository Status"
        
        if [[ -f "${github_metrics}" ]]; then
            local repo_data=$(cat "${github_metrics}")
            echo "* Stars: $(echo "${repo_data}" | jq -r '.stargazers_count')"
            echo "* Forks: $(echo "${repo_data}" | jq -r '.forks_count')"
            echo "* Open Issues: $(echo "${repo_data}" | jq -r '.open_issues_count')"
        fi
        
        echo
        echo "## Recent Activity (24h)"
        
        if [[ -f "${commits_metrics}" ]]; then
            local commit_count=$(jq length "${commits_metrics}")
            echo "* Commits: ${commit_count}"
        fi
        
        if [[ -f "${pulls_metrics}" ]]; then
            local pr_count=$(jq length "${pulls_metrics}")
            echo "* Open PRs: ${pr_count}"
        fi
        
    } > "${report_file}"
    
    log "INFO" "GitHub metrics report generated: ${report_file}"
}

# Generate combined progress report
generate_progress_report() {
    local report_file="${CONFIG[project_root]}/reports/progress_report.md"
    
    {
        echo "# Project Progress Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo
        
        # Include system metrics
        echo "## System Status"
        echo "* CPU Usage: $(get_cpu_usage)%"
        echo "* Memory Usage: $(get_memory_usage)%"
        echo "* Disk Usage: $(get_disk_usage)%"
        echo
        
        # Include GitHub metrics
        echo "## GitHub Status"
        if [[ -f "${CONFIG[project_root]}/reports/github_metrics.md" ]]; then
            tail -n +2 "${CONFIG[project_root]}/reports/github_metrics.md"
        fi
        
    } > "${report_file}"
    
    log "INFO" "Progress report generated: ${report_file}"
}

# Main reporting loop
report() {
    while true; do
        # Generate GitHub report
        generate_github_report
        
        # Generate combined report
        generate_progress_report
        
        # Sleep for reporting interval
        sleep "${CONFIG[github_sync_interval]}"
    done
}

# Run if executed directly
if [[ "${(%):-%x}" == "${0}" ]]; then
    report
fi

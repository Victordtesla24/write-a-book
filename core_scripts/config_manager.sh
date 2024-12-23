#!/bin/sh

# Configuration manager script
# Handles environment-specific settings and configuration

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Load environment variables
load_env() {
    if [ -f "${PROJECT_ROOT}/.env" ]; then
        . "${PROJECT_ROOT}/.env"
    fi
}

# Set default configuration
set_defaults() {
    LOG_LEVEL="${LOG_LEVEL:-INFO}"
    MONITORING_INTERVAL="${MONITORING_INTERVAL:-300}"
    METRICS_RETENTION_DAYS="${METRICS_RETENTION_DAYS:-7}"
    
    # GitHub defaults
    GITHUB_TOKEN="${GITHUB_TOKEN:-}"
    GITHUB_USERNAME="${GITHUB_USERNAME:-}"
    GITHUB_REPO="${GITHUB_REPO:-write-a-book}"
    GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
}

# Initialize configuration
init_config() {
    load_env
    set_defaults
    
    # Export GitHub configuration
    CONFIG[github_token]="${GITHUB_TOKEN}"
    CONFIG[github_username]="${GITHUB_USERNAME}"
    CONFIG[github_repo]="${GITHUB_REPO}"
    CONFIG[github_branch]="${GITHUB_BRANCH}"
    CONFIG[project_root]="${PROJECT_ROOT}"
}

# Get configuration value
get_config() {
    case "$1" in
        "project_root") echo "${CONFIG[project_root]}" ;;
        "log_level") echo "$LOG_LEVEL" ;;
        "monitoring_interval") echo "$MONITORING_INTERVAL" ;;
        "metrics_retention_days") echo "$METRICS_RETENTION_DAYS" ;;
        "github_token") echo "${CONFIG[github_token]}" ;;
        "github_username") echo "${CONFIG[github_username]}" ;;
        "github_repo") echo "${CONFIG[github_repo]}" ;;
        "github_branch") echo "${CONFIG[github_branch]}" ;;
        *) echo "" ;;
    esac
}

# Set configuration value
set_config() {
    case "$1" in
        "project_root") CONFIG[project_root]="$2" ;;
        "log_level") LOG_LEVEL="$2" ;;
        "monitoring_interval") MONITORING_INTERVAL="$2" ;;
        "metrics_retention_days") METRICS_RETENTION_DAYS="$2" ;;
        "github_token") CONFIG[github_token]="$2" ;;
        "github_username") CONFIG[github_username]="$2" ;;
        "github_repo") CONFIG[github_repo]="$2" ;;
        "github_branch") CONFIG[github_branch]="$2" ;;
    esac
}

# Initialize configuration array
declare -A CONFIG

# Export configuration
init_config
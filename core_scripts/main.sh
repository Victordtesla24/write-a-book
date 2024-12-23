#!/bin/zsh

# Main orchestrator script
# Follows agent_directives.md for project management

set -e

# Load core scripts
SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
source "${SCRIPT_DIR}/config_manager.sh"
source "${SCRIPT_DIR}/resource_manager.sh"

# Initialize logging
LOG_DIR="${CONFIG[project_root]}/logs"
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/main.log"

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" >> "${LOG_FILE}"
    
    # Also print to stdout for INFO and ERROR
    if [[ "${level}" == "INFO" ]] || [[ "${level}" == "ERROR" ]]; then
        echo "[${level}] ${message}"
    fi
}

# Function to initialize project
init_project() {
    log "INFO" "Initializing project..."
    
    # Create project structure
    for dir in src tests docs config logs; do
        mkdir -p "${CONFIG[project_root]}/${dir}"
        log "INFO" "Created directory: ${dir}"
    done
    
    # Initialize configuration
    if init_config; then
        log "INFO" "Configuration initialized successfully"
    else
        log "ERROR" "Failed to initialize configuration"
        return 1
    fi
    
    # Start resource monitoring
    start_monitoring "${LOG_FILE}"
    
    # Set up file protection
    protect_files "${CONFIG[project_root]}/README.md" \
                 "${CONFIG[project_root]}/requirements.txt" \
                 "${CONFIG[project_root]}/.gitignore"
    
    log "INFO" "Project initialized successfully"
    return 0
}

# Function to monitor project resources
monitor_project() {
    log "INFO" "Starting project monitoring..."
    
    # Check disk space
    if ! monitor_disk_space "${CONFIG[disk_space_threshold]}" "${CONFIG[project_root]}"; then
        log "ERROR" "Disk space usage exceeds threshold"
        return 1
    fi
    
    # Check memory usage
    if ! monitor_memory "${CONFIG[memory_threshold]}"; then
        log "ERROR" "Memory usage exceeds threshold"
        return 1
    fi
    
    # Get resource metrics
    local disk_free
    disk_free=$(df -h "${CONFIG[project_root]}" | awk 'NR==2 {print $4}')
    
    log "INFO" "Project monitoring results:"
    log "INFO" "- Disk space available: ${disk_free}"
    log "INFO" "- Memory usage within limits"
    
    return 0
}

# Function to clean up project
cleanup_project() {
    log "INFO" "Starting project cleanup..."
    
    # Clean cache
    local cache_dir="${CONFIG[project_root]}/.cache"
    if [[ -d "${cache_dir}" ]]; then
        manage_cache "${cache_dir}" "${CONFIG[cache_ttl]}" "${CONFIG[cache_max_size]}"
        log "INFO" "Cache cleaned successfully"
    fi
    
    # Remove temporary files
    find "${CONFIG[project_root]}" -type f -name "*.tmp" -delete
    find "${CONFIG[project_root]}" -type f -name "*.pyc" -delete
    find "${CONFIG[project_root]}" -type d -name "__pycache__" -exec rm -rf {} +
    
    log "INFO" "Project cleanup completed successfully"
    return 0
}

# Function to handle file operations
handle_file() {
    local operation="$1"
    local file="$2"
    local target="$3"
    
    case "${operation}" in
        "protect")
            if [[ -f "${file}" ]]; then
                protect_files "${file}"
                log "INFO" "Protected file: ${file}"
                return 0
            else
                log "ERROR" "File does not exist: ${file}"
                return 1
            fi
            ;;
        *)
            log "ERROR" "Unknown file operation: ${operation}"
            return 1
            ;;
    esac
}

# Main execution
main() {
    local command="$1"
    shift
    
    case "${command}" in
        "init")
            init_project
            ;;
        "monitor")
            monitor_project
            ;;
        "cleanup")
            cleanup_project
            ;;
        "file")
            handle_file "$@"
            ;;
        *)
            echo "Usage: $0 {init|monitor|cleanup|file}"
            exit 1
            ;;
    esac
}

# Only run main if script is executed directly
if [[ "${(%):-%x}" == "${0}" ]]; then
    main "$@"
fi 
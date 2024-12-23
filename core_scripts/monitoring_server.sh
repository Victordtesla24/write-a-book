#!/bin/zsh

# Monitoring server script
# Handles system monitoring and metrics collection

set -e

# Load configuration
source "$(dirname "$0")/config_manager.sh"

# Initialize logging
LOG_DIR="${CONFIG[project_root]}/logs"
mkdir -p "${LOG_DIR}"
MONITOR_LOG="${LOG_DIR}/monitoring.log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${MONITOR_LOG}"
}

# Collect system metrics
collect_system_metrics() {
    metrics_file="${CONFIG[project_root]}/metrics/system.json"
    mkdir -p "$(dirname "${metrics_file}")"
    
    # Collect CPU, memory, and disk metrics
    cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | cut -d% -f1)
    memory_usage=$(top -l 1 | grep "PhysMem" | awk '{print $2}' | cut -d. -f1)
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | cut -d% -f1)
    
    # Write metrics to file
    cat > "${metrics_file}" << EOF
{
    "cpu_usage": ${cpu_usage:-0},
    "memory_usage": ${memory_usage:-0},
    "disk_usage": ${disk_usage:-0},
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
    
    log "INFO" "System metrics collected"
}

# Main monitoring loop
monitor() {
    log "INFO" "Starting monitoring server..."
    
    while true; do
        collect_system_metrics
        sleep "${CONFIG[github_sync_interval]:-300}"
    done
}

# Run if executed directly
if [[ "${(%):-%x}" == "${0}" ]]; then
    monitor
fi

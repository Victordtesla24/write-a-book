#!/bin/zsh

# Dashboard runner script
# Continuously runs verification and serves the dashboard

set -e

# Load configuration
source "$(dirname "$0")/../core_scripts/config_manager.sh"

# Initialize logging
LOG_DIR="${CONFIG[project_root]}/logs"
mkdir -p "${LOG_DIR}"
DASHBOARD_LOG="${LOG_DIR}/dashboard.log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${DASHBOARD_LOG}"
}

# Kill any existing dashboard processes
cleanup() {
    log "INFO" "Stopping dashboard processes..."
    pkill -f "monitoring_server.sh" || true
    pkill -f "serve_dashboard.py" || true
    pkill -f "github_sync.sh" || true
}

# Start monitoring processes
start_monitoring() {
    log "INFO" "Starting monitoring processes..."
    
    # Start GitHub sync in background
    "${CONFIG[project_root]}/scripts/github_sync.sh" &
    
    # Start monitoring server in background
    "${CONFIG[project_root]}/core_scripts/monitoring_server.sh" &
    
    # Start metrics collection
    while true; do
        # Collect system metrics
        {
            cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | cut -d% -f1)
            memory_usage=$(top -l 1 | grep "PhysMem" | awk '{print $2}' | cut -d. -f1)
            disk_usage=$(df -h . | awk 'NR==2 {print $5}' | cut -d% -f1)
            
            cat > "${CONFIG[project_root]}/metrics/system.json" << EOF
{
    "cpu_usage": ${cpu_usage:-0},
    "memory_usage": ${memory_usage:-0},
    "disk_usage": ${disk_usage:-0},
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
        } 2>/dev/null
        
        sleep 60
    done &
}

# Start dashboard server
start_dashboard() {
    log "INFO" "Starting dashboard server..."
    
    # Install required Python packages
    pip3 install psutil > /dev/null 2>&1 || true
    
    # Create dashboard directory if it doesn't exist
    mkdir -p "${CONFIG[project_root]}/dashboard"
    
    # Start the dashboard server
    python3 "${CONFIG[project_root]}/serve_dashboard.py" &
    
    log "INFO" "Dashboard server started"
}

# Main execution
main() {
    # Clean up any existing processes
    cleanup
    
    # Create necessary directories
    mkdir -p "${CONFIG[project_root]}/{metrics,reports}"
    
    # Start monitoring
    start_monitoring
    
    # Start dashboard
    start_dashboard
    
    log "INFO" "Dashboard is running at http://localhost:8080/dashboard/"
    log "INFO" "Press Ctrl+C to stop"
    
    # Wait for Ctrl+C
    trap cleanup EXIT
    wait
}

# Run if executed directly
if [[ "${(%):-%x}" == "${0}" ]]; then
    main
fi

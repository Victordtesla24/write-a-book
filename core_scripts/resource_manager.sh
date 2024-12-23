#!/bin/bash

# Enhanced resource manager script
CONFIG_DIR="config"
METRICS_DIR="metrics"
LOG_FILE="logs/resource.log"
THRESHOLDS_FILE="$CONFIG_DIR/thresholds.json"
RESOURCES_FILE="$METRICS_DIR/resources.json"

# Ensure required directories exist
mkdir -p "$CONFIG_DIR" "$METRICS_DIR" "logs"

# Initialize default thresholds
init_thresholds() {
    cat > "$THRESHOLDS_FILE" << EOF
{
    "cpu": {
        "warning": 70,
        "critical": 85
    },
    "memory": {
        "warning": 75,
        "critical": 90
    },
    "disk": {
        "warning": 80,
        "critical": 90
    },
    "ai": {
        "max_tokens": 4096,
        "cost_per_token": 0.000002,
        "daily_budget": 1.00
    }
}
EOF
    echo "Resource thresholds initialized" >> "$LOG_FILE"
}

# Monitor resource usage
monitor_resources() {
    local thresholds
    local cpu_usage
    local memory_usage
    local disk_usage
    
    # Get current thresholds
    if [ -f "$THRESHOLDS_FILE" ]; then
        thresholds=$(cat "$THRESHOLDS_FILE")
    else
        echo "Thresholds not found. Initializing..." >> "$LOG_FILE"
        init_thresholds
        thresholds=$(cat "$THRESHOLDS_FILE")
    fi
    
    # Get CPU usage
    cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | cut -d% -f1)
    
    # Get memory usage
    memory_usage=$(top -l 1 | grep "PhysMem" | awk '{print $2}' | cut -d. -f1)
    
    # Get disk usage
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | cut -d% -f1)
    
    # Check against thresholds and generate alerts
    local cpu_warning=$(echo "$thresholds" | jq -r '.cpu.warning')
    local cpu_critical=$(echo "$thresholds" | jq -r '.cpu.critical')
    local mem_warning=$(echo "$thresholds" | jq -r '.memory.warning')
    local mem_critical=$(echo "$thresholds" | jq -r '.memory.critical')
    local disk_warning=$(echo "$thresholds" | jq -r '.disk.warning')
    local disk_critical=$(echo "$thresholds" | jq -r '.disk.critical')
    
    # Store current resource state
    cat > "$RESOURCES_FILE" << EOF
{
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "cpu": {
        "usage": $cpu_usage,
        "status": "$(get_status $cpu_usage $cpu_warning $cpu_critical)"
    },
    "memory": {
        "usage": $memory_usage,
        "status": "$(get_status $memory_usage $mem_warning $mem_critical)"
    },
    "disk": {
        "usage": $disk_usage,
        "status": "$(get_status $disk_usage $disk_warning $disk_critical)"
    }
}
EOF
    
    # Generate alerts if needed
    check_alerts "$cpu_usage" "$memory_usage" "$disk_usage" \
                "$cpu_warning" "$cpu_critical" \
                "$mem_warning" "$mem_critical" \
                "$disk_warning" "$disk_critical"
}

# Get status based on thresholds
get_status() {
    local value=$1
    local warning=$2
    local critical=$3
    
    if [ "$value" -ge "$critical" ]; then
        echo "critical"
    elif [ "$value" -ge "$warning" ]; then
        echo "warning"
    else
        echo "normal"
    fi
}

# Check and generate alerts
check_alerts() {
    local cpu=$1
    local mem=$2
    local disk=$3
    local cpu_warn=$4
    local cpu_crit=$5
    local mem_warn=$6
    local mem_crit=$7
    local disk_warn=$8
    local disk_crit=$9
    
    # CPU alerts
    if [ "$cpu" -ge "$cpu_crit" ]; then
        echo "[CRITICAL] CPU usage at ${cpu}% (threshold: ${cpu_crit}%)" >> "$LOG_FILE"
    elif [ "$cpu" -ge "$cpu_warn" ]; then
        echo "[WARNING] CPU usage at ${cpu}% (threshold: ${cpu_warn}%)" >> "$LOG_FILE"
    fi
    
    # Memory alerts
    if [ "$mem" -ge "$mem_crit" ]; then
        echo "[CRITICAL] Memory usage at ${mem}% (threshold: ${mem_crit}%)" >> "$LOG_FILE"
    elif [ "$mem" -ge "$mem_warn" ]; then
        echo "[WARNING] Memory usage at ${mem}% (threshold: ${mem_warn}%)" >> "$LOG_FILE"
    fi
    
    # Disk alerts
    if [ "$disk" -ge "$disk_crit" ]; then
        echo "[CRITICAL] Disk usage at ${disk}% (threshold: ${disk_crit}%)" >> "$LOG_FILE"
    elif [ "$disk" -ge "$disk_warn" ]; then
        echo "[WARNING] Disk usage at ${disk}% (threshold: ${disk_warn}%)" >> "$LOG_FILE"
    fi
}

# Update thresholds
update_thresholds() {
    local resource=$1
    local warning=$2
    local critical=$3
    local thresholds
    
    if [ -f "$THRESHOLDS_FILE" ]; then
        thresholds=$(cat "$THRESHOLDS_FILE")
        
        # Update specified resource thresholds
        thresholds=$(echo "$thresholds" | jq ".$resource.warning = $warning | .$resource.critical = $critical")
        
        echo "$thresholds" > "$THRESHOLDS_FILE"
        echo "Updated $resource thresholds: warning=$warning%, critical=$critical%" >> "$LOG_FILE"
    else
        echo "Thresholds not found. Initializing..." >> "$LOG_FILE"
        init_thresholds
        update_thresholds "$resource" "$warning" "$critical"
    fi
}

# Generate resource report
generate_report() {
    if [ -f "$RESOURCES_FILE" ]; then
        local resources=$(cat "$RESOURCES_FILE")
        local thresholds=$(cat "$THRESHOLDS_FILE")
        
        # Generate markdown report
        cat > "$METRICS_DIR/resource_report.md" << EOF
# Resource Utilization Report
Generated: $(date)

## Current Usage
- CPU: $(echo "$resources" | jq -r '.cpu.usage')% ($(echo "$resources" | jq -r '.cpu.status'))
- Memory: $(echo "$resources" | jq -r '.memory.usage')% ($(echo "$resources" | jq -r '.memory.status'))
- Disk: $(echo "$resources" | jq -r '.disk.usage')% ($(echo "$resources" | jq -r '.disk.status'))

## Thresholds
### CPU
- Warning: $(echo "$thresholds" | jq -r '.cpu.warning')%
- Critical: $(echo "$thresholds" | jq -r '.cpu.critical')%

### Memory
- Warning: $(echo "$thresholds" | jq -r '.memory.warning')%
- Critical: $(echo "$thresholds" | jq -r '.memory.critical')%

### Disk
- Warning: $(echo "$thresholds" | jq -r '.disk.warning')%
- Critical: $(echo "$thresholds" | jq -r '.disk.critical')%

## AI Resource Management
- Max Tokens: $(echo "$thresholds" | jq -r '.ai.max_tokens')
- Cost per Token: \$$(echo "$thresholds" | jq -r '.ai.cost_per_token')
- Daily Budget: \$$(echo "$thresholds" | jq -r '.ai.daily_budget')
EOF
        
        echo "Resource report generated" >> "$LOG_FILE"
    else
        echo "Resource data not found" >> "$LOG_FILE"
    fi
}

# Command line interface
case "$1" in
    "init")
        init_thresholds
        ;;
    "monitor")
        monitor_resources
        ;;
    "update")
        if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
            echo "Usage: $0 update <resource> <warning_threshold> <critical_threshold>"
            exit 1
        fi
        update_thresholds "$2" "$3" "$4"
        ;;
    "report")
        generate_report
        ;;
    *)
        echo "Usage: $0 {init|monitor|update|report}"
        exit 1
        ;;
esac

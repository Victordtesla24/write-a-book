#!/bin/zsh

# Create metrics directory
mkdir -p metrics

# Collect metrics
timestamp=$(date +%s)
cpu_usage=$(top -l 1 | awk '/CPU usage/ {gsub(/%/,"",$3); print $3}')
memory_usage=$(vm_stat | awk '/Pages active/ {gsub(/\./,"",$3); print $3 * 4096 / 1024 / 1024}')
disk_usage=$(df -h . | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
io_wait=$(top -l 1 | awk '/CPU usage/ {gsub(/%/,"",$10); print $10}')
load_avg=$(sysctl -n vm.loadavg | awk '{print $2}')

# Create temporary file
temp_file=$(mktemp)

# Write header and metrics to temp file
printf "timestamp,cpu_usage,memory_usage,disk_usage,io_wait,load_avg\n" > "$temp_file"
printf "%d,%.2f,%.2f,%.2f,%.2f,%.2f\n" \
    "$timestamp" \
    "${cpu_usage:-0}" \
    "${memory_usage:-0}" \
    "${disk_usage:-0}" \
    "${io_wait:-0}" \
    "${load_avg:-0}" >> "$temp_file"

# Remove any trailing whitespace and move to final location
sed 's/[[:space:]]*$//' "$temp_file" > metrics/system_metrics.csv
rm "$temp_file"

# Show results
cat metrics/system_metrics.csv

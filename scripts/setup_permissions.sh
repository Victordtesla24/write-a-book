#!/bin/bash

# Make script executable
chmod +x "$0"

# Create necessary directories if they don't exist
directories=(
    "coverage_html"
    "htmlcov"
    "metrics"
    "logs"
    "output"
    "core_scripts"
    "tests"
    "src"
)

for dir in "${directories[@]}"; do
    sudo mkdir -p "$dir"
done

# Set permissions recursively for all project directories
sudo find . -type d -exec chmod 777 {} \;
sudo find . -type f -exec chmod 666 {} \;

# Make all .sh files executable
sudo find . -name "*.sh" -exec chmod +x {} \;

# Set specific permissions for core directories
sudo chmod -R 777 core_scripts/
sudo chmod -R 777 tests/
sudo chmod -R 777 coverage_html/
sudo chmod -R 777 htmlcov/
sudo chmod -R 777 metrics/
sudo chmod -R 777 logs/
sudo chmod -R 777 output/

echo "Permissions have been set successfully"

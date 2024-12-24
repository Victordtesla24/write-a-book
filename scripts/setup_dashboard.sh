#!/bin/zsh

# Dashboard setup script
# Automatically sets up and configures the project dashboard

set -e

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Load configuration
source "${PROJECT_ROOT}/core_scripts/config_manager.sh"

# Initialize logging
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "${LOG_DIR}"
DASHBOARD_LOG="${LOG_DIR}/dashboard_setup.log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${DASHBOARD_LOG}"
}

# Setup dashboard structure
setup_dashboard_structure() {
    log "INFO" "Setting up dashboard structure..."
    
    # Create required directories
    mkdir -p "${PROJECT_ROOT}/dashboard/static"
    mkdir -p "${PROJECT_ROOT}/dashboard/templates"
    mkdir -p "${PROJECT_ROOT}/metrics"
    mkdir -p "${PROJECT_ROOT}/reports"
    
    # Create empty metrics files
    echo "{}" > "${PROJECT_ROOT}/metrics/system.json"
    echo "{}" > "${PROJECT_ROOT}/metrics/test.json"
    touch "${PROJECT_ROOT}/metrics/proj_status.md"
}

# Install dashboard dependencies
install_dependencies() {
    log "INFO" "Installing dashboard dependencies..."
    
    # Install Python packages
    pip install streamlit plotly pytest pytest-cov pylint mypy || {
        log "ERROR" "Failed to install Python packages"
        return 1
    }
    
    # Create requirements file if it doesn't exist
    if [ ! -f "${PROJECT_ROOT}/requirements.txt" ]; then
        cat > "${PROJECT_ROOT}/requirements.txt" << EOF
streamlit>=1.29.0
plotly>=5.18.0
pytest>=7.4.3
pytest-cov>=4.1.0
pylint>=3.0.3
mypy>=1.7.0
EOF
    fi
}

# Configure dashboard
configure_dashboard() {
    log "INFO" "Configuring dashboard..."
    
    # Create Streamlit config directory
    mkdir -p "${PROJECT_ROOT}/.streamlit"
    
    # Create Streamlit config
    cat > "${PROJECT_ROOT}/.streamlit/config.toml" << EOF
[server]
port = 8502
enableCORS = true
enableXsrfProtection = false

[theme]
primaryColor = "#00cc96"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "Inter"

[browser]
gatherUsageStats = false
EOF
    
    # Create dashboard config
    cat > "${PROJECT_ROOT}/dashboard/dashboard_config.json" << EOF
{
    "port": 8502,
    "theme": "light",
    "refresh_interval": 1,
    "verification_interval": 120,
    "features": {
        "historical_metrics": true,
        "predictive_analytics": true,
        "code_complexity": true,
        "technical_debt": true,
        "test_timing": true,
        "github_webhooks": true,
        "collaboration": true,
        "dark_mode": true,
        "cookie_consent": true
    },
    "components": {
        "data_editor": {
            "enabled": true,
            "auto_save": true
        },
        "metric_cards": {
            "enabled": true,
            "animation": true
        },
        "alerts": {
            "enabled": true,
            "sound": false
        },
        "code_viewer": {
            "enabled": true,
            "syntax_highlight": true
        }
    }
}
EOF
}

# Setup monitoring
setup_monitoring() {
    log "INFO" "Setting up monitoring..."
    
    # Create monitoring service
    cat > "${PROJECT_ROOT}/scripts/run_monitoring.sh" << 'EOF'
#!/bin/zsh
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"
source "${PROJECT_ROOT}/core_scripts/config_manager.sh"

# Start monitoring processes
"${PROJECT_ROOT}/core_scripts/monitoring_server.sh" &
echo $! > "${PROJECT_ROOT}/.monitoring.pid"

# Start metrics collection
while true; do
    "${PROJECT_ROOT}/scripts/update_status.sh"
    sleep 60
done &
echo $! > "${PROJECT_ROOT}/.monitor.pid"

wait
EOF
    
    chmod +x "${PROJECT_ROOT}/scripts/run_monitoring.sh"
}

# Setup custom CSS
setup_custom_css() {
    log "INFO" "Setting up custom CSS..."
    
    # Create custom CSS file
    cat > "${PROJECT_ROOT}/dashboard/static/style.css" << EOF
/* Dashboard custom styles */
.stApp {
    max-width: 1200px;
    margin: 0 auto;
}

.metric-card {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.metric-card:hover {
    transform: translateY(-2px);
}

.chart-container {
    margin: 1rem 0;
    padding: 1rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Dark mode styles */
[data-theme="dark"] {
    --background-color: #1e1e1e;
    --text-color: #ffffff;
}

[data-theme="dark"] .metric-card,
[data-theme="dark"] .chart-container {
    background: #2d2d2d;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
EOF
}

# Create dashboard launcher
create_launcher() {
    log "INFO" "Creating dashboard launcher..."
    
    cat > "${PROJECT_ROOT}/launch_dashboard.sh" << EOF
#!/bin/zsh
set -e

# Start monitoring
./scripts/run_monitoring.sh &

# Start dashboard
streamlit run serve_dashboard.py --server.port 8502

# Cleanup
pkill -f "monitoring_server.sh" || true
pkill -f "update_status.sh" || true
EOF
    
    chmod +x "${PROJECT_ROOT}/launch_dashboard.sh"
}

# Main execution
main() {
    log "INFO" "Starting dashboard setup..."
    
    # Setup structure
    setup_dashboard_structure
    
    # Install dependencies
    install_dependencies
    
    # Configure dashboard
    configure_dashboard
    
    # Setup monitoring
    setup_monitoring
    
    # Setup custom CSS
    setup_custom_css
    
    # Create launcher
    create_launcher
    
    log "INFO" "Dashboard setup completed successfully"
    log "INFO" "Run './launch_dashboard.sh' to start the dashboard"
}

# Run if executed directly
if [[ "${(%):-%x}" == "${0}" ]]; then
    main
fi

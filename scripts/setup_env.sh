#!/bin/zsh

# Environment setup script
# Sets up project environment and dependencies

set -e

# Load configuration
source "$(dirname "$0")/../core_scripts/config_manager.sh"

# Initialize logging
LOG_DIR="${CONFIG[project_root]}/logs"
mkdir -p "${LOG_DIR}"
SETUP_LOG="${LOG_DIR}/setup.log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${SETUP_LOG}"
}

# Setup GitHub configuration
setup_github() {
    log "INFO" "Setting up GitHub configuration..."
    
    # Create .env from template if it doesn't exist
    if [[ ! -f "${CONFIG[project_root]}/.env" ]] && [[ -f "${CONFIG[project_root]}/.env.template" ]]; then
        cp "${CONFIG[project_root]}/.env.template" "${CONFIG[project_root]}/.env"
        log "INFO" "Created .env file from template"
    fi
    
    # Initialize Git repository if needed
    if [[ ! -d "${CONFIG[project_root]}/.git" ]]; then
        git init
        log "INFO" "Initialized Git repository"
        
        # Create .gitignore
        cat > "${CONFIG[project_root]}/.gitignore" << EOF
.env
*.log
__pycache__/
*.pyc
.coverage
.pytest_cache/
metrics/
reports/
EOF
        log "INFO" "Created .gitignore file"
    fi
    
    # Configure Git if credentials are available
    if [[ -n "${CONFIG[github_token]}" ]] && [[ -n "${CONFIG[github_username]}" ]]; then
        git config user.name "${CONFIG[github_username]}"
        git config user.email "${CONFIG[github_username]}@users.noreply.github.com"
        
        # Add GitHub remote if repo is configured
        if [[ -n "${CONFIG[github_repo]}" ]]; then
            git remote remove origin 2>/dev/null || true
            git remote add origin "https://${CONFIG[github_token]}@github.com/${CONFIG[github_username]}/${CONFIG[github_repo]}.git"
            log "INFO" "Configured GitHub remote"
        fi
    else
        log "WARN" "GitHub credentials not found in .env file"
    fi
}

# Setup project structure
setup_project() {
    log "INFO" "Setting up project structure..."
    
    # Create necessary directories
    mkdir -p "${CONFIG[project_root]}/{src,tests,docs,config,metrics,reports}"
    
    # Create basic README if it doesn't exist
    if [[ ! -f "${CONFIG[project_root]}/README.md" ]]; then
        cat > "${CONFIG[project_root]}/README.md" << EOF
# ${CONFIG[project_name]}

## Description
${CONFIG[project_name]} - A new project

## Setup
1. Copy .env.template to .env and configure
2. Run setup_env.sh to initialize
3. Configure GitHub repository

## Development
- Use verify_and_fix.sh for code quality
- Monitor progress through dashboard
EOF
    fi
    
    log "INFO" "Project structure setup complete"
}

# Main setup function
main() {
    log "INFO" "Starting environment setup..."
    
    # Setup project structure
    setup_project
    
    # Setup GitHub
    setup_github
    
    # Initial commit if repository is fresh
    if [[ -z "$(git rev-parse --verify HEAD 2>/dev/null)" ]]; then
        git add .
        git commit -m "Initial commit"
        log "INFO" "Created initial commit"
    fi
    
    log "INFO" "Environment setup complete"
}

# Run if executed directly
if [[ "${(%):-%x}" == "${0}" ]]; then
    main
fi

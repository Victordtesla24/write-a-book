#!/bin/bash

# Set up logging with rotation
setup_logging() {
    LOG_DIR="logs"
    LOG_FILE="${LOG_DIR}/verify_and_fix.log"

    # Create logs directory if it doesn't exist
    mkdir -p "$LOG_DIR"

    # Create or truncate log file
    > "$LOG_FILE"

    # Set up logging to both file and console
    exec 1> >(tee -a "$LOG_FILE")
    exec 2> >(tee -a "$LOG_FILE" >&2)
}

# Initialize logging
setup_logging

# Exit on error (but allow error handling)
set -o pipefail

# Progress bar function
progress_bar() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))
    
    printf "\rProgress: ["
    printf "%${completed}s" | tr ' ' '='
    printf "%${remaining}s" | tr ' ' ' '
    printf "] %d%%" "$percentage"
    if [ "$current" -eq "$total" ]; then
        printf "\n"
    fi
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Function to check required commands
check_required_commands() {
    local missing_commands=()
    for cmd in git tree coverage black isort flake8 pylint pytest npm; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [ ${#missing_commands[@]} -ne 0 ]; then
        error_log "Missing required commands: ${missing_commands[*]}"
        error_log "Please install missing commands and try again"
        return 1
    fi
}

# Function to setup markdown tools
setup_markdown_tools() {
    log "Setting up markdown linting tools..."
    
    # Check if markdownlint-cli is installed globally
    if ! command -v markdownlint >/dev/null 2>&1; then
        log "Installing markdownlint-cli globally..."
        npm install -g markdownlint-cli || {
            error_log "Failed to install markdownlint-cli"
            return 1
        }
    fi
    
    # Create markdownlint config if it doesn't exist
    if [ ! -f .markdownlint.json ]; then
        cat > .markdownlint.json << EOL || return 1
{
    "MD022": true,
    "MD031": true,
    "MD032": true,
    "MD034": true,
    "MD041": true,
    "line-length": false
}
EOL
        log "Created .markdownlint.json configuration"
    fi
}

# Function to fix markdown files
fix_markdown_files() {
    log "Fixing markdown files..."
    
    # Find all markdown files, excluding virtual environments and system directories
    local md_files=$(find . -name "*.md" \
        -not -path "./node_modules/*" \
        -not -path "./venv/*" \
        -not -path "./test_venv/*" \
        -not -path "./cursor_env/*" \
        -not -path "./.git/*")
    
    for file in $md_files; do
        log "Processing $file..."
        
        # Run markdownlint --fix if available
        if command -v markdownlint >/dev/null 2>&1; then
            markdownlint --fix "$file" 2>/dev/null || true
        fi
    done
}

# Function to setup Streamlit structure
setup_streamlit_structure() {
    log "Setting up Streamlit directory structure..."
    
    # Create necessary directories
    for dir in pages src/utils data tests docs .streamlit; do
        mkdir -p "$dir" || {
            error_log "Failed to create directory: $dir"
            return 1
        }
    done

    # Create .streamlit/config.toml if it doesn't exist
    if [ ! -f .streamlit/config.toml ]; then
        cat > .streamlit/config.toml << EOL || return 1
[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
enableCORS = false
EOL
        log "Created .streamlit/config.toml"
    fi
}

# Function to cleanup files
cleanup_files() {
    log "Starting file cleanup..."
    
    # Remove any existing backup directories
    find . -type d -name "backup_*" -exec rm -rf {} +
    
    # Create required directories
    mkdir -p src/utils data || {
        error_log "Failed to create required directories"
        return 1
    }
}

# Function to verify Streamlit dependencies
verify_streamlit_deps() {
    log "Verifying Streamlit dependencies..."
    
    # Create requirements.txt if it doesn't exist
    touch requirements.txt || return 1
    
    # Check if streamlit is in requirements.txt
    if ! grep -q "streamlit" requirements.txt; then
        echo "streamlit" >> requirements.txt || return 1
        log "Added streamlit to requirements.txt"
    fi
}

# Function to update project status
update_project_status() {
    log "Updating project status..."
    
    STATUS_FILE="docs/proj_status.md"
    mkdir -p docs
    
    {
        echo "# Project Status Report"
        echo
        echo "Last Updated: $(date)"
        echo
        echo "## Directory Structure"
        echo
        echo "\`\`\`"
        tree -L 3 --dirsfirst 2>/dev/null || echo "tree command not available"
        echo "\`\`\`"
        echo
        echo "## Recent Changes"
        echo
        git log -5 --pretty=format:"- %s" 2>/dev/null || echo "No git history available"
    } > "$STATUS_FILE"
    
    log "Updated $STATUS_FILE"
}

# Function to initialize and configure GitHub repository
setup_github() {
    log "Setting up GitHub repository..."
    
    # Check if git is already initialized
    if [ ! -d ".git" ]; then
        git init || {
            error_log "Failed to initialize git repository"
            return 1
        }
    fi
    
    # Configure git user if not set
    if [ -z "$(git config --get user.email)" ]; then
        if [ -n "$GIT_USER_EMAIL" ] && [ -n "$GIT_USER_NAME" ]; then
            git config --local user.email "$GIT_USER_EMAIL"
            git config --local user.name "$GIT_USER_NAME"
        else
            log "Please set GIT_USER_EMAIL and GIT_USER_NAME environment variables"
            return 1
        fi
    fi
    
    # Check if remote exists
    if ! git remote | grep -q "^origin$"; then
        # Add remote repository - user should configure this manually
        log "Please configure your GitHub remote repository manually using:"
        log "git remote add origin <your-repo-url>"
        return 1
    fi
    
    # Ensure we're on main branch
    git checkout -B main || {
        error_log "Failed to create/switch to main branch"
        return 1
    }
    
    log "GitHub repository setup completed"
}

# Function to generate commit message from project status
generate_commit_message() {
    log "Generating commit message from project status..."
    
    STATUS_FILE="docs/proj_status.md"
    if [ ! -f "$STATUS_FILE" ]; then
        echo "chore: Initial commit"
        return
    fi
    
    # Extract recent changes from status file
    local changes=$(grep -A 1 "^## Recent Changes" "$STATUS_FILE" | tail -n 1)
    if [ -z "$changes" ]; then
        changes="chore: Update project files"
    fi
    
    echo "$changes"
}

# Function to commit and push changes
commit_changes() {
    log "Committing changes to GitHub..."
    
    # Stage all changes
    git add . || {
        error_log "Failed to stage changes"
        return 1
    }
    
    # Generate commit message
    local commit_msg=$(generate_commit_message)
    
    # Commit changes
    git commit -m "$commit_msg" || {
        error_log "Failed to commit changes"
        return 1
    }
    
    # Fetch latest changes
    git fetch origin || {
        error_log "Failed to fetch latest changes"
        return 1
    }
    
    # Try to rebase
    if ! git rebase origin/main; then
        git rebase --abort
        log "Could not automatically merge changes. Please resolve conflicts manually:"
        log "1. git pull origin main"
        log "2. Resolve any conflicts"
        log "3. git push origin main"
        return 1
    fi
    
    # Push to main branch
    if ! git push origin main; then
        error_log "Failed to push changes. Please push manually after resolving conflicts"
        return 1
    fi
    
    log "Successfully pushed changes to GitHub"
}

# Main function
main() {
    log "Starting verification and fixes..."
    
    # Run all checks and fixes
    cleanup_files || exit 1  # Run cleanup first to remove any existing backups
    check_required_commands || exit 1
    setup_markdown_tools || exit 1
    setup_streamlit_structure || exit 1
    verify_streamlit_deps || exit 1
    update_project_status || exit 1
    fix_markdown_files || exit 1
    
    # Setup and push to GitHub
    setup_github || exit 1
    commit_changes || exit 1
    
    log "All verifications and fixes completed successfully!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi

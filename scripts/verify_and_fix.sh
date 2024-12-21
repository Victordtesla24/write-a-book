#!/bin/bash

# Set up logging
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/verify_and_fix.log"
LINT_FILE="${LOG_DIR}/lint_report.log"
PERF_LOG="${LOG_DIR}/performance.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"
touch "$LOG_FILE" "$LINT_FILE" "$PERF_LOG"

# Set up logging to both file and console
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

# Exit on error
set -e
set -o pipefail

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Function to setup virtual environment
setup_venv() {
    log "Setting up virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q -e ".[dev]" 2>/dev/null || {
        error_log "Failed to install package in development mode"
        return 1
    }
}

# Function to run auto_fix_code.sh
run_auto_fix() {
    log "Running auto_fix_code.sh..."
    if [ -f "scripts/auto_fix_code.sh" ]; then
        chmod +x scripts/auto_fix_code.sh
        ./scripts/auto_fix_code.sh
    else
        error_log "auto_fix_code.sh not found"
        return 1
    fi
}

# Function to setup markdown tools
setup_markdown_tools() {
    log "Setting up markdown linting tools..."
    if [ ! -f .markdownlint.json ]; then
        cat > .markdownlint.json << EOL
{
    "MD022": true,
    "MD031": true,
    "MD032": true,
    "MD034": true,
    "MD041": true,
    "line-length": false
}
EOL
    fi
}

# Function to fix markdown files
fix_markdown_files() {
    log "Fixing markdown files..."
    for file in $(find . -name "*.md" \
        -not -path "./node_modules/*" \
        -not -path "./venv/*" \
        -not -path "./test_venv/*" \
        -not -path "./cursor_env/*" \
        -not -path "./.git/*"); do
        log "Processing markdown file: $file..."
        
        # Check if file exists and is not empty
        if [ -f "$file" ] && [ -s "$file" ]; then
            # Remove trailing whitespace
            sed -i '' -e 's/[[:space:]]*$//' "$file"
            
            # Ensure single trailing newline
            if [ "$(tail -c1 "$file" | xxd -p)" != "0a" ]; then
                echo "" >> "$file"
                log "Added trailing newline to $file"
            fi
        fi
    done
}

# Function to fix Python files
fix_python_files() {
    log "Fixing Python files..."
    for file in $(find . -name "*.py" \
        -not -path "./venv/*" \
        -not -path "./test_venv/*" \
        -not -path "./cursor_env/*" \
        -not -path "./.git/*"); do
        log "Processing $file..."
        
        # Fix imports
        isort "$file" 2>/dev/null || true
        
        # Fix code style
        autopep8 --in-place --aggressive --aggressive "$file" 2>/dev/null || true
        
        # Add docstring if missing
        if ! grep -q '"""' "$file"; then
            sed -i '' '1i\
"""Module docstring."""\
\
' "$file" 2>/dev/null || true
        fi
    done
}

# Function to run linting checks
run_linting() {
    log "Running linting checks..."
    
    # Run pytest with coverage
    log "Running pytest..."
    coverage run -m pytest tests/ -v || {
        error_log "Pytest failed"
        return 1
    }
    
    # Generate coverage report
    coverage report > "$LOG_DIR/coverage.txt"
    
    # Run pylint and save report
    pylint src tests --output-format=text | tee -a "$LINT_FILE" || true
    
    # Check if there are any errors
    if grep -q "error" "$LINT_FILE"; then
        log "Found linting errors:"
        grep "error" "$LINT_FILE"
        return 1
    fi
    
    # Show final score
    score=$(tail -n 2 "$LINT_FILE" | grep "rated at" | grep -o "[0-9].[0-9][0-9]" || echo "0.00")
    log "Pylint score: $score/10.00"
}

# Function to setup Streamlit structure
setup_streamlit_structure() {
    log "Setting up advanced Streamlit directory structure..."

    for dir in pages src/utils data tests docs static/images static/css .streamlit scripts; do
        mkdir -p "$dir"
    done

    if [ ! -f .streamlit/config.toml ]; then
        cat > .streamlit/config.toml <<EOL
[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
enableCORS = false
headless = true
EOL
    fi
}

# Function to verify Streamlit dependencies
verify_streamlit_deps() {
    log "Verifying Streamlit dependencies..."
    touch requirements.txt
    if ! grep -q "streamlit" requirements.txt; then
        echo "streamlit" >> requirements.txt
    fi
}

# Function to update project status
update_documentation() {
    log "Updating project documentation..."

    STATUS_FILE="docs/proj_status.md"
    PLAN_FILE="docs/implementation_plan.md"

    # Ensure docs directory exists
    mkdir -p docs

    # Update project status with enriched details
    log "Generating detailed project status..."
    {
        echo "# Project Status Report"
        echo "Last Updated: $(date)"
        echo
        echo "## Summary of Resolved Errors"
        echo
        grep -E "FIXED|RESOLVED" "$LOG_FILE" 2>/dev/null || echo "No errors resolved in this run."
        echo
        echo "## Current Implementation Status"
        echo
        echo "- Python files updated: $(find src -name '*.py' | wc -l)"
        echo "- Test files updated: $(find tests -name 'test_*.py' | wc -l)"
        echo
        echo "## Test Coverage Report"
        echo
        if [ -f "$LOG_DIR/coverage.txt" ]; then
            echo '```'
            cat "$LOG_DIR/coverage.txt"
            echo '```'
        else
            echo "No coverage report available."
        fi
        echo
        echo "## Lint Report"
        echo
        if [ -f "$LINT_FILE" ]; then
            echo '```'
            cat "$LINT_FILE"
            echo '```'
            # Extract and display lint score
            score=$(tail -n 2 "$LINT_FILE" | grep "rated at" | grep -o "[0-9].[0-9][0-9]" || echo "0.00")
            echo
            echo "Pylint Score: $score/10.00"
        else
            echo "No lint report available."
        fi
        echo
        echo "## Recent Changes"
        git log -5 --pretty=format:"- %s" 2>/dev/null || echo "No Git history available."
    } > "$STATUS_FILE"

    # Sync implementation plan with unimplemented features
    log "Syncing implementation plan..."
    if [ -f "$PLAN_FILE" ]; then
        unimplemented_features=$(grep -B 1 "\[ \]" "$STATUS_FILE" 2>/dev/null || echo "None")
        if [ "$unimplemented_features" != "None" ]; then
            echo "## Pending Features" >> "$PLAN_FILE"
            echo "$unimplemented_features" | sed 's/^/- /' >> "$PLAN_FILE"
        fi
    else
        log "Implementation plan not found. Skipping sync."
    fi

    log "Documentation updated successfully."
}

# Function to setup git configuration
setup_git_config() {
    log "Setting up git configuration..."
    if [ -d ".git" ]; then
        # Configure git if not already configured
        if ! git config --get user.email >/dev/null; then
            git config --global user.email "cline@example.com"
        fi
        if ! git config --get user.name >/dev/null; then
            git config --global user.name "Cline"
        fi
        
        # Setup pre-commit hook
        if [ -f "scripts/setup_hooks.sh" ]; then
            chmod +x scripts/setup_hooks.sh
            ./scripts/setup_hooks.sh
        fi
    fi
}

# Function to cleanup git state
cleanup_git() {
    log "Cleaning up git state..."
    if [ -d ".git" ]; then
        # Reset any staged changes that weren't committed
        git reset >/dev/null 2>&1 || true
        # Clean untracked files
        git clean -fd >/dev/null 2>&1 || true
    fi
}

# Enhanced function to generate detailed commit messages and commit to GitHub
auto_commit_to_github() {
    log "Auto-committing changes to GitHub..."

    if [ ! -d ".git" ]; then
        error_log "Git repository not initialized. Skipping commit."
        return 1
    fi

    # Check if we're on main branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "main" ]; then
        log "Not on main branch. Switching to main..."
        git checkout main || {
            error_log "Failed to switch to main branch."
            return 1
        }
    fi

    # Stage all changes
    git add . || {
        error_log "Failed to stage changes."
        return 1
    }

    # Check if there are any changes to commit
    if ! git diff --cached --quiet; then
        # Generate dynamic commit message
        commit_message="Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
        
        # Add error resolution info
        if grep -q "FIXED\|RESOLVED" "$LOG_FILE"; then
            commit_message+=" - Resolved Errors: $(grep -c 'FIXED\|RESOLVED' "$LOG_FILE")"
        fi
        if grep -q "ERROR" "$LOG_FILE"; then
            commit_message+=" - Remaining Errors: $(grep -c 'ERROR' "$LOG_FILE")"
        fi
        
        # Add test results
        test_passed=$(grep -c 'PASSED' "$LOG_FILE" || echo "0")
        test_failed=$(grep -c 'FAILED' "$LOG_FILE" || echo "0")
        commit_message+=" - Test Results: $test_passed passed, $test_failed failed"
        
        # Add lint score if available
        if [ -f "$LINT_FILE" ]; then
            score=$(tail -n 2 "$LINT_FILE" | grep "rated at" | grep -o "[0-9].[0-9][0-9]" || echo "0.00")
            commit_message+=" - Lint Score: $score/10.00"
        fi

        # Commit changes
        git commit -m "$commit_message" || {
            error_log "Failed to commit changes."
            return 1
        }

        # Check if remote exists and push
        if git remote -v | grep -q origin; then
            log "Pushing changes to GitHub..."
            git push origin main || {
                error_log "Failed to push changes to GitHub."
                return 1
            }
        else
            log "No remote repository found. Skipping push."
        fi

        log "Changes committed successfully."
    else
        log "No changes to commit."
    fi
}

# Main function
main() {
    log "Starting verification and fixes..."
    
    # Set up error handling
    trap 'echo "Error: Script failed" >&2; cleanup_git; exit 1' ERR
    trap 'echo "Script interrupted" >&2; cleanup_git; exit 1' INT TERM
    
    # Run all tasks
    setup_venv || exit 1
    run_auto_fix || exit 1
    setup_markdown_tools || exit 1
    setup_streamlit_structure || exit 1
    verify_streamlit_deps || exit 1
    fix_markdown_files || exit 1
    fix_python_files || exit 1
    run_linting || exit 1
    update_documentation || exit 1
    auto_commit_to_github || exit 1
    
    # Clean exit
    log "All verifications and fixes completed successfully!"
    trap - ERR INT TERM
    exit 0
}

# Run main function
main


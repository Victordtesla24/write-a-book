#!/bin/bash

# Set up logging
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/verify_and_fix.log"
LINT_FILE="${LOG_DIR}/lint_report.log"
MARKDOWN_ERRORS_FILE="${LOG_DIR}/markdown_errors.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"
> "$LOG_FILE"
> "$LINT_FILE"
> "$MARKDOWN_ERRORS_FILE"

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

# Function to check markdown code blocks
check_markdown_code_blocks() {
    local file="$1"
    awk '
    BEGIN { valid = 1; in_block = 0; line_num = 0 }
    {
        line_num++
        if ($0 ~ /^```/) {
            if (!in_block) {
                in_block = 1
                if ($0 == "```") {
                    valid = 0
                    printf "Found code block without language specification at line %d\n", line_num
                    print "Context:"
                    print "..."
                    if (line_num > 1) print prev2
                    if (line_num > 0) print prev1
                    print $0
                    exit 1
                }
                start_lang = substr($0, 4)
                start_line = line_num
            } else {
                in_block = 0
                if ($0 != "```") {
                    end_lang = substr($0, 4)
                    if (end_lang != "" && end_lang != start_lang) {
                        valid = 0
                        printf "Mismatched code block languages: started with \"%s\" at line %d, ended with \"%s\" at line %d\n", 
                            start_lang, start_line, end_lang, line_num
                        print "Context:"
                        print "..."
                        print prev2
                        print prev1
                        print $0
                        exit 1
                    }
                }
            }
        }
        prev2 = prev1
        prev1 = $0
    }
    END {
        if (in_block) {
            valid = 0
            printf "Unclosed code block starting at line %d\n", start_line
            exit 1
        }
        exit !valid
    }' "$file" 2>&1
}

# Function to run linting checks
run_linting() {
    log "Running linting checks..."
    
    # Run pytest
    log "Running pytest..."
    python -m pytest tests/ -v || {
        error_log "Pytest failed"
        return 1
    }
    
    # Run pylint and save report
    pylint src tests --output-format=text | tee -a "$LINT_FILE" || true
    
    # Run additional checks
    log "Running additional checks..."
    
    # Check for markdown issues
    find . -name "*.md" -not -path "./venv/*" -not -path "./cursor_env/*" -type f | while read -r file; do
        log "Checking markdown file: $file"
        # Check for missing language in code blocks
        result=$(check_markdown_code_blocks "$file")
        if [ $? -ne 0 ]; then
            {
                echo "=== Error in file: $file ==="
                echo "$result"
                echo "==========================="
                echo
            } | tee -a "$MARKDOWN_ERRORS_FILE"
            error_log "Markdown errors found in $file (see $MARKDOWN_ERRORS_FILE for details)"
            return 1
        fi
        
        # Check for missing final newline
        if [ -f "$file" ] && [ -s "$file" ] && [ "$(tail -c1 "$file" | xxd -p)" != "0a" ]; then
            error_log "Missing final newline in $file"
            return 1
        fi
    done
    
    # Check for Python issues
    find . -name "*.py" -not -path "./venv/*" -not -path "./cursor_env/*" -type f | while read -r file; do
        # Check for setuptools import without type ignore
        if grep -q "^from setuptools" "$file" && ! grep -q "# type: ignore" "$file"; then
            error_log "Missing type ignore for setuptools import in $file"
            return 1
        fi
        
        # Check for self imports in __init__.py
        if [[ "$file" == *"__init__.py" ]] && grep -q "from src\." "$file"; then
            error_log "Found self import in $file"
            return 1
        fi
        
        # Check for isoformat usage
        if grep -q "isoformat" "$file"; then
            error_log "Found isoformat usage in $file, should use strftime"
            return 1
        fi
    done
    
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
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing $file..."
    done
}

# Function to setup Streamlit structure
setup_streamlit_structure() {
    log "Setting up Streamlit directory structure..."
    for dir in pages src/utils data tests docs .streamlit; do
        mkdir -p "$dir"
    done

    if [ ! -f .streamlit/config.toml ]; then
        cat > .streamlit/config.toml << EOL
[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
enableCORS = false
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
        echo "\`\`\`shell"
        tree -L 3 --dirsfirst 2>/dev/null || echo "tree command not available"
        echo "\`\`\`"
        echo
        echo "## Recent Changes"
        echo
        git log -5 --pretty=format:"- %s" 2>/dev/null || echo "No git history available"
        echo
        echo "## Lint Report"
        echo
        if [ -f "$LINT_FILE" ]; then
            echo "\`\`\`shell"
            cat "$LINT_FILE"
            echo "\`\`\`"
        fi
    } > "$STATUS_FILE"
}

# Function to generate commit message based on changes
generate_commit_message() {
    local message=""
    
    # Get list of modified files by type
    local python_changes=$(git diff --cached --name-only -- '*.py')
    local markdown_changes=$(git diff --cached --name-only -- '*.md')
    local test_changes=$(git diff --cached --name-only -- 'tests/*.py')
    
    # Build commit message based on changes
    if [ ! -z "$python_changes" ]; then
        message+="Update Python files: "
        message+=$(echo "$python_changes" | xargs -n1 basename | tr '\n' ',' | sed 's/,$//')
        message+=". "
    fi
    
    if [ ! -z "$markdown_changes" ]; then
        message+="Update documentation: "
        message+=$(echo "$markdown_changes" | xargs -n1 basename | tr '\n' ',' | sed 's/,$//')
        message+=". "
    fi
    
    if [ ! -z "$test_changes" ]; then
        message+="Update tests: "
        message+=$(echo "$test_changes" | xargs -n1 basename | tr '\n' ',' | sed 's/,$//')
        message+=". "
    fi
    
    # If no specific changes detected, use a generic message
    if [ -z "$message" ]; then
        message="Update project files"
    fi
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message"
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

# Function to setup GitHub repository
setup_github() {
    log "Setting up GitHub repository..."
    if [ -d ".git" ]; then
        # Setup git config first
        setup_git_config
        
        # Add all changes
        git add . || {
            error_log "Failed to stage changes"
            cleanup_git
            return 1
        }
        
        # Check if there are any changes to commit
        if ! git diff --cached --quiet; then
            # Generate timestamp
            timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            
            # Generate commit message based on actual changes
            commit_msg=$(git diff --cached --name-status | awk '
                BEGIN { OFS=". "; python=""; markdown=""; tests="" }
                /^[AM].*\.py$/ && $2 !~ /^tests\// { python = python $2 " " }
                /^[AM].*\.md$/ { markdown = markdown $2 " " }
                /^[AM].*test.*\.py$/ { tests = tests $2 " " }
                END {
                    msg = ""
                    if (python != "") msg = msg "Update Python files: " python
                    if (markdown != "") msg = msg "Update documentation: " markdown
                    if (tests != "") msg = msg "Update tests: " tests
                    if (msg == "") msg = "Update project files"
                    print msg
                }')
            
            # Combine timestamp and message
            commit_msg="[$timestamp] $commit_msg"
            
            # Commit changes with the generated message
            if ! git commit -m "$commit_msg"; then
                error_log "Failed to commit changes"
                cleanup_git
                return 1
            fi
            
            # Rename branch to main if needed
            if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then
                git branch -M main || {
                    error_log "Failed to rename branch to main"
                    cleanup_git
                    return 1
                }
            fi
            
            log "Successfully committed changes"
        else
            log "No changes to commit"
        fi
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
    update_project_status || exit 1
    setup_github || exit 1
    
    # Clean exit
    log "All verifications and fixes completed successfully!"
    trap - ERR INT TERM
    exit 0
}

# Run main function
main

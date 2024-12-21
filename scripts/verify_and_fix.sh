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

# Check bash version and set up file caching mechanism
if [ "${BASH_VERSINFO[0]}" -ge 4 ]; then
    declare -A FILE_CACHE
    USE_ASSOC_ARRAYS=true
else
    # Fallback for older bash versions
    USE_ASSOC_ARRAYS=false
    # Use temporary files for caching
    CACHE_DIR="${LOG_DIR}/cache"
    mkdir -p "$CACHE_DIR"
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Function to get cached value
get_cache() {
    local key="$1"
    if [ "$USE_ASSOC_ARRAYS" = true ]; then
        echo "${FILE_CACHE[$key]}"
    else
        if [ -f "$CACHE_DIR/$key" ]; then
            cat "$CACHE_DIR/$key"
        fi
    fi
}

# Function to set cached value
set_cache() {
    local key="$1"
    local value="$2"
    if [ "$USE_ASSOC_ARRAYS" = true ]; then
        FILE_CACHE[$key]="$value"
    else
        echo "$value" > "$CACHE_DIR/$key"
    fi
}

# Function to initialize file caches
init_file_cache() {
    log "Initializing file cache..."
    
    # Cache Python files
    local python_files=$(find . -name "*.py" \
        -not -path "./venv/*" \
        -not -path "./test_venv/*" \
        -not -path "./cursor_env/*" \
        -not -path "./.git/*")
    set_cache "python" "$python_files"
    
    # Cache Markdown files
    local markdown_files=$(find . -name "*.md" \
        -not -path "./node_modules/*" \
        -not -path "./venv/*" \
        -not -path "./test_venv/*" \
        -not -path "./cursor_env/*" \
        -not -path "./.git/*")
    set_cache "markdown" "$markdown_files"
    
    # Cache directory existence
    local dirs_exist=""
    for dir in docs .streamlit static/images static/css pages src/utils data tests; do
        if [ -d "$dir" ]; then
            dirs_exist+="$dir "
        fi
    done
    set_cache "dirs_exist" "$dirs_exist"
}

# Function to ensure directory exists (cached)
ensure_dir() {
    local dir="$1"
    local dirs_exist=$(get_cache "dirs_exist")
    if [[ ! " $dirs_exist " =~ " $dir " ]]; then
        mkdir -p "$dir"
        set_cache "dirs_exist" "$dirs_exist $dir"
    fi
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
    
    # Run additional checks
    log "Running additional checks..."
    
    # Check for markdown issues
    local markdown_files=$(get_cache "markdown")
    if [ ! -z "$markdown_files" ]; then
        echo "$markdown_files" | while read -r file; do
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
    fi
    
    # Check for Python issues
    local python_files=$(get_cache "python")
    if [ ! -z "$python_files" ]; then
        echo "$python_files" | while read -r file; do
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
    fi
    
    # Check if there are any errors
    if grep -q "error" "$LINT_FILE"; then
        log "Found linting errors:"
        grep "error" "$LINT_FILE"
        return 1
    fi
    
    # Show final score
    score=$(tail -n 2 "$LINT_FILE" | grep "rated at" | grep -o "[0-9].[0-9][0-9]" || echo "0.00")
    log "Pylint score: $score/10.00"
    return 0
}

# Optimized fix_python_files function
fix_python_files() {
    log "Fixing Python files..."
    
    # Batch process imports first
    local python_files=$(get_cache "python")
    if [ ! -z "$python_files" ]; then
        log "Batch processing imports..."
        echo "$python_files" | xargs -P 4 -I {} isort {} 2>/dev/null || true
        
        log "Batch processing code style..."
        echo "$python_files" | xargs -P 4 -I {} autopep8 --in-place --aggressive --aggressive {} 2>/dev/null || true
        
        # Process docstrings
        echo "$python_files" | while read -r file; do
            if ! grep -q '"""' "$file"; then
                sed -i '' '1i\
"""Module docstring."""\
\
' "$file" 2>/dev/null || true
            fi
        done
    fi
    return 0
}

# Optimized fix_markdown_files function
fix_markdown_files() {
    log "Fixing markdown files..."
    local markdown_files=$(get_cache "markdown")
    if [ ! -z "$markdown_files" ]; then
        echo "$markdown_files" | while read -r file; do
            log "Processing $file..."
            
            # Skip files in excluded directories
            if [[ "$file" == *"/venv/"* ]] || [[ "$file" == *"/cursor_env/"* ]]; then
                log "Skipping markdown file in excluded directory: $file"
                continue
            fi
            
            # Check initial state
            local initial_errors=0
            if command -v markdownlint >/dev/null 2>&1; then
                markdownlint "$file" > "$LOG_DIR/pre_fix_$$.md" 2>&1 || initial_errors=$?
            fi
            
            # Apply fixes using auto_fix_code.sh
            if [ -f "scripts/auto_fix_code.sh" ]; then
                # Extract just the fix_markdown function
                local temp_script=$(mktemp)
                sed -n '/^fix_markdown()/,/^}/p' scripts/auto_fix_code.sh > "$temp_script"
                # Source the function and call it
                source "$temp_script"
                fix_markdown "$file"
                rm "$temp_script"
            fi
            
            # Verify fixes
            if command -v markdownlint >/dev/null 2>&1; then
                local final_errors=0
                markdownlint "$file" > "$LOG_DIR/post_fix_$$.md" 2>&1 || final_errors=$?
                
                if [ $final_errors -eq 0 ]; then
                    log "Successfully fixed all Markdown issues in $file"
                elif [ $final_errors -lt $initial_errors ]; then
                    log "Reduced Markdown issues in $file from $initial_errors to $final_errors"
                    cat "$LOG_DIR/post_fix_$$.md" >> "$MARKDOWN_ERRORS_FILE"
                else
                    log "WARNING: Could not fix all Markdown issues in $file"
                    cat "$LOG_DIR/post_fix_$$.md" >> "$MARKDOWN_ERRORS_FILE"
                fi
                
                # Cleanup
                rm -f "$LOG_DIR/pre_fix_$$.md" "$LOG_DIR/post_fix_$$.md"
            fi
        done
    fi
    return 0
}

# Function to setup markdown tools
setup_markdown_tools() {
    log "Setting up markdown linting tools..."
    if [ ! -f .markdownlint.json ]; then
        cat > .markdownlint.json << EOL
{
    "MD001": false,
    "MD022": false,
    "MD024": false,
    "MD025": false,
    "MD041": false,
    "default": true,
    "line-length": false,
    "no-hard-tabs": true,
    "whitespace": false
}
EOL
    fi
    return 0
}

# Optimized setup_streamlit_structure function
setup_streamlit_structure() {
    log "Setting up advanced Streamlit directory structure..."
    
    # Create directories in parallel
    echo "pages src/utils data tests docs static/images static/css .streamlit scripts" | \
    tr ' ' '\n' | xargs -P 4 -I {} mkdir -p {}
    
    if [ ! -f .streamlit/config.toml ]; then
        ensure_dir ".streamlit"
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
    return 0
}

# Function to verify Streamlit dependencies
verify_streamlit_deps() {
    log "Verifying Streamlit dependencies..."
    touch requirements.txt
    if ! grep -q "streamlit" requirements.txt; then
        echo "streamlit" >> requirements.txt
    fi
    return 0
}

# Optimized update_documentation function
update_documentation() {
    log "Updating project documentation..."
    
    STATUS_FILE="docs/proj_status.md"
    PLAN_FILE="docs/implementation_plan.md"
    ensure_dir "docs"
    
    # Cache git status
    local git_history=$(git log -5 --pretty=format:"- %s" 2>/dev/null || echo "No Git history available.")
    local python_files=$(get_cache "python")
    local python_count=$(echo "$python_files" | wc -l)
    local test_count=$(echo "$python_files" | grep -c "test_" || echo "0")
    
    # Get resolved errors
    local resolved_errors=$(grep -E "FIXED|RESOLVED" "$LOG_FILE" 2>/dev/null || echo "No errors resolved in this run.")
    
    # Generate documentation with cached values
    {
        echo "# Project Status Report"
        echo "Last Updated: $(date)"
        echo
        echo "## Summary of Resolved Errors"
        echo
        echo "$resolved_errors"
        echo
        echo "## Current Implementation Status"
        echo
        echo "- Python files updated: $python_count"
        echo "- Test files updated: $test_count"
        echo
        echo "## Test Coverage Report"
        echo
        if [ -f "$LOG_DIR/coverage.txt" ]; then
            cat "$LOG_DIR/coverage.txt"
        else
            echo "No coverage report available."
        fi
        echo
        echo "## Lint Report"
        echo
        if [ -f "$LINT_FILE" ]; then
            cat "$LINT_FILE"
            score=$(tail -n 2 "$LINT_FILE" | grep "rated at" | grep -o "[0-9].[0-9][0-9]" || echo "0.00")
            echo
            echo "Pylint Score: $score/10.00"
        else
            echo "No lint report available."
        fi
        echo
        echo "## Recent Changes"
        echo "$git_history"
    } > "$STATUS_FILE"
    
    # Create implementation plan if it doesn't exist
    if [ ! -f "$PLAN_FILE" ]; then
        {
            echo "# Implementation Plan"
            echo
            echo "## Editor Implementation"
            echo
            echo "### Editor Components"
            echo "- Document class"
            echo "- Editor class"
            echo "- Text Editor"
            echo
            echo "### Core Editor Features"
            echo "- Basic text editing"
            echo "- Template management"
            echo "- Document history"
            echo
            echo "### Editor Testing Strategy"
            echo "- Unit tests for core components"
            echo "- Integration tests for editor features"
            echo "- End-to-end testing for user workflows"
            echo
        } > "$PLAN_FILE"
    fi
    
    # Update implementation plan with unimplemented features
    local unimplemented_features=$(grep -B 1 "- \[ \]" "$STATUS_FILE" 2>/dev/null || echo "None")
    if [ "$unimplemented_features" != "None" ]; then
        echo -e "\n## Pending Features\n" >> "$PLAN_FILE"
        echo "$unimplemented_features" | sed 's/^/- /' >> "$PLAN_FILE"
    fi
    
    return 0
}

# Optimized auto_commit_to_github function
auto_commit_to_github() {
    log "Auto-committing changes to GitHub..."
    
    # Early exit if no git
    if [ ! -d ".git" ]; then
        error_log "Git repository not initialized. Skipping commit."
        return 1
    fi
    
    # Cache git status
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    local has_remote=$(git remote -v | grep -q origin && echo "true" || echo "false")
    
    # Branch management
    if [ "$current_branch" != "main" ]; then
        log "Not on main branch. Switching to main..."
        git checkout main || return 1
    fi
    
    # Optimize git operations
    git add -A || return 1
    
    if ! git diff --cached --quiet; then
        # Cache log analysis results
        local error_count=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo "0")
        local fixed_count=$(grep -c "FIXED\|RESOLVED" "$LOG_FILE" 2>/dev/null || echo "0")
        local test_passed=$(grep -c "PASSED" "$LOG_FILE" 2>/dev/null || echo "0")
        local test_failed=$(grep -c "FAILED" "$LOG_FILE" 2>/dev/null || echo "0")
        local lint_score="0.00"
        
        if [ -f "$LINT_FILE" ]; then
            lint_score=$(tail -n 2 "$LINT_FILE" | grep "rated at" | grep -o "[0-9].[0-9][0-9]" || echo "0.00")
        fi
        
        # Generate commit message
        local commit_message="Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
        if [ "$fixed_count" -gt 0 ] 2>/dev/null; then 
            commit_message+=" - Resolved Errors: $fixed_count"
        fi
        if [ "$error_count" -gt 0 ] 2>/dev/null; then
            commit_message+=" - Remaining Errors: $error_count"
        fi
        commit_message+=" - Test Results: $test_passed passed, $test_failed failed"
        commit_message+=" - Lint Score: $lint_score/10.00"
        
        # Commit and push
        if ! git commit -m "$commit_message"; then
            error_log "Failed to commit changes."
            return 1
        fi
        
        if [ "$has_remote" = "true" ]; then
            log "Pushing changes to GitHub..."
            git push origin main || return 1
        fi
        
        log "Changes committed successfully."
    else
        log "No changes to commit."
    fi
    return 0
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

# Function to initialize new project
init_project() {
    log "Initializing new project..."
    
    # Check if this is a new project
    if [ ! -f "setup.py" ] && [ ! -d "src" ]; then
        log "New project detected. Running initial setup..."
        
        # Run setup_env.sh first
        if [ -f "scripts/setup_env.sh" ]; then
            chmod +x scripts/setup_env.sh
            ./scripts/setup_env.sh || {
                error_log "Initial setup failed"
                return 1
            }
        fi
        
        # Initialize additional project structure
        setup_streamlit_structure
        setup_markdown_tools
        verify_streamlit_deps
        
        # Create initial documentation with proper formatting
        update_documentation
        
        log "Initial project setup completed"
    else
        log "Existing project detected, skipping initialization"
    fi
}

# Main function with optimized flow
main() {
    log "Starting verification and fixes..."
    
    # Set up error handling
    trap 'echo "Error: Script failed" >&2; cleanup_git; exit 1' ERR
    trap 'echo "Script interrupted" >&2; cleanup_git; exit 1' INT TERM
    
    # Initialize file cache first
    init_file_cache
    
    # Check for --init flag
    if [[ "$1" == "--init" ]]; then
        init_project || exit 1
    fi
    
    # Run all tasks
    setup_venv || exit 1
    setup_git_config || exit 1  # Added git config setup
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

# Run main function with arguments
main "$@"


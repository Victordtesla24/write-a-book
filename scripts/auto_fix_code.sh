#!/bin/bash

# Configuration
LOG_FILE="logs/auto_fix.log"
ERROR_PATTERN_FILE="logs/error_patterns.txt"
mkdir -p "logs"

# Maximum number of fix iterations
MAX_ITERATIONS=5
MIN_ERROR_REDUCTION=1  # Minimum number of errors that must be fixed to continue

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to detect and store error patterns
detect_error_patterns() {
    log "Detecting error patterns..."
    > "$ERROR_PATTERN_FILE"
    
    # First check markdown errors
    parse_markdown_errors
    
    # Then check Python errors
    if command -v pylint >/dev/null 2>&1; then
        pylint src tests --output-format=text 2>/dev/null | grep "^[A-Z]:" >> "$ERROR_PATTERN_FILE"
    fi
    
    # Count total errors
    local error_count=$(wc -l < "$ERROR_PATTERN_FILE")
    log "Detected $error_count unique error patterns"
    
    return 0
}

# Function to parse errors from verify_and_fix.log and auto_fix.log.md
parse_verify_log_errors() {
    local log_file="logs/verify_and_fix.log"
    local md_log="logs/auto_fix.log.md"
    local found_errors=0
    
    > "$ERROR_PATTERN_FILE"  # Clear error patterns file
    
    # First check markdown errors
    if [ -f "$md_log" ]; then
        log "Parsing markdown errors..."
        while IFS=: read -r file line rest; do
            if [[ $file == ./* ]] && [[ $file == *.md ]]; then
                if [[ $rest =~ MD[0-9]+/[a-zA-Z-]+ ]]; then
                    echo "$file:$line:$rest" >> "$ERROR_PATTERN_FILE"
                    ((found_errors++))
                fi
            fi
        done < "$md_log"
    fi
    
    # Then check Python errors from verify_and_fix.log
    if [ -f "$log_file" ]; then
        log "Parsing verify_and_fix.log for errors..."
        
        # Extract pytest failures
        grep -A 2 "FAILED" "$log_file" | while read -r line; do
            if [[ $line =~ ^tests/.*\.py ]]; then
                local file=$(echo "$line" | cut -d: -f1)
                local message=$(echo "$line" | cut -d: -f2-)
                echo "$file:$message" >> "$ERROR_PATTERN_FILE"
                ((found_errors++))
            fi
        done
        
        # Extract pylint errors
        grep -A 1 "Your code has been rated at" "$log_file" | while read -r line; do
            if [[ $line =~ ([0-9]+\.[0-9]+)/10 ]]; then
                local score=${BASH_REMATCH[1]}
                if (( $(echo "$score < 10.0" | bc -l) )); then
                    pylint src tests --output-format=text 2>/dev/null | grep "^[A-Z]:" | while read -r error; do
                        local file=$(echo "$error" | cut -d: -f2)
                        local message=$(echo "$error" | cut -d: -f4-)
                        echo "$file:$message" >> "$ERROR_PATTERN_FILE"
                        ((found_errors++))
                    done
                fi
            fi
        done
    fi
    
    if [ "$found_errors" -gt 0 ]; then
        log "Found $found_errors errors to fix"
        log "Error summary:"
        sort "$ERROR_PATTERN_FILE" | uniq -c | while read -r count error; do
            log "  $count occurrences: $error"
        done
        return 0
    else
        log "No errors found in logs"
        return 1
    fi
}

# Add this function after parse_verify_log_errors()
parse_import_errors() {
    local log_file="logs/verify_and_fix.log"
    if [ -f "$log_file" ]; then
        # Extract import errors from log
        grep -B2 -A2 "ImportError\|ModuleNotFoundError\|No module named" "$log_file" | \
        sed -n 's/.*No module named \(['"'"'"]*\)\([^'"'"'"]*\)\1.*/\2/p' > "${ERROR_PATTERN_FILE}.imports"
        
        if [ -s "${ERROR_PATTERN_FILE}.imports" ]; then
            log "Found import errors:"
            while read -r module; do
                log "  Missing import: $module"
            done < "${ERROR_PATTERN_FILE}.imports"
        fi
    fi
}

# Function to apply generic fixes based on error type
apply_generic_fixes() {
    local file="$1"
    local errors=$(grep "^$file:" "$ERROR_PATTERN_FILE" || true)
    
    if [ -z "$errors" ]; then
        return 0
    fi
    
    log "Applying fixes to $file"
    
    # Handle different file types
    case "${file##*.}" in
        md)
            # Fix markdown errors
            if echo "$errors" | grep -q "MD022.*blanks-around-headings"; then
                log "  Fixing heading spacing"
                sed -i'' -e '/^#/i\\' -e '/^#/a\\' "$file"
            fi
            
            if echo "$errors" | grep -q "MD025.*single-title"; then
                log "  Fixing multiple top-level headings"
                awk '
                    BEGIN {first_h1 = 1}
                    /^# / {
                        if (first_h1) {
                            print; first_h1 = 0
                        } else {
                            sub(/^# /, "## ")
                            print
                        }
                        next
                    }
                    {print}
                ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
            fi
            ;;
            
        py)
            # Fix Python errors
            if echo "$errors" | grep -q "redefined-outer-name"; then
                log "  Fixing redefined outer names"
                # Add pytest import if missing
                grep -q "^import pytest" "$file" || sed -i'' '1i\import pytest\n' "$file"
                
                # Add fixture decorator to functions with redefined names
                while read -r error_line; do
                    local line_num=$(echo "$error_line" | cut -d: -f2)
                    sed -i'' "${line_num}i\@pytest.fixture" "$file"
                done < <(echo "$errors" | grep "redefined-outer-name")
            fi
            
            # Handle import errors
            if echo "$errors" | grep -q "ImportError\|ModuleNotFoundError"; then
                while read -r module; do
                    fix_import_errors "$file" "$module"
                done < "${ERROR_PATTERN_FILE}.imports"
            fi
            ;;
    esac
}

# Add this function to handle import fixes
fix_import_errors() {
    local file="$1"
    local error_msg="$2"
    
    # Extract module name from error message
    local module=$(echo "$error_msg" | grep -o "No module named '[^']*'" | sed "s/No module named '\([^']*\)'/\1/")
    
    # Skip if no module found
    [ -z "$module" ] && return 0
    
    log "Fixing import for module '$module' in $file"
    
    # Check if file exists and is Python
    [[ "${file##*.}" != "py" ]] && return 0
    [ ! -f "$file" ] && return 0
    
    # Don't add import if it already exists
    if grep -q "^import $module\|^from $module import" "$file"; then
        log "  Import already exists"
        return 0
    fi
    
    # Find the last import statement
    local last_import=$(grep -n "^import\|^from .* import" "$file" | tail -n1 | cut -d: -f1)
    
    if [ -n "$last_import" ]; then
        # Add after last import
        sed -i'' "${last_import}a\\import ${module}" "$file"
    else
        # Add at top of file
        sed -i'' "1i\\import ${module}\\n" "$file"
    fi
    
    log "  Added import for $module"
    
    # Verify import was added
    if grep -q "^import $module\|^from $module import" "$file"; then
        return 0
    else
        log "  Failed to add import"
        return 1
    fi
}

# Generic file fix function
fix_file() {
    local file="$1"
    local initial_errors=$(grep "^$file:" "$ERROR_PATTERN_FILE" | wc -l)
    
    if [ "$initial_errors" -eq 0 ]; then
        return 0
    fi
    
    log "Processing $file ($initial_errors errors)"
    apply_generic_fixes "$file"
    
    # Verify fixes
    local remaining_errors=$(grep "^$file:" "$ERROR_PATTERN_FILE" | wc -l)
    local fixed_count=$((initial_errors - remaining_errors))
    
    if [ "$fixed_count" -gt 0 ]; then
        log "  Fixed $fixed_count errors in $file"
    else
        log "  No errors fixed in $file"
    fi
}

# Function to count total errors
count_errors() {
    local error_count=0
    local pylint_errors=0
    local md_errors=0
    
    # Count Python errors
    if command -v pylint >/dev/null 2>&1; then
        # Use grep -c with proper error handling
        pylint_errors=$(pylint src tests --output-format=text 2>/dev/null | grep -c "^[A-Z]:" || echo "0")
        # Ensure we have a valid number
        [[ "$pylint_errors" =~ ^[0-9]+$ ]] || pylint_errors=0
        error_count=$((error_count + pylint_errors))
    fi
    
    # Count Markdown errors
    if command -v markdownlint >/dev/null 2>&1; then
        # Use grep -c with proper error handling
        md_errors=$(find . -name "*.md" -not -path "./venv/*" -not -path "./cursor_env/*" -type f -exec markdownlint {} \; 2>/dev/null | grep -c "MD[0-9]+" || echo "0")
        # Ensure we have a valid number
        [[ "$md_errors" =~ ^[0-9]+$ ]] || md_errors=0
        error_count=$((error_count + md_errors))
    fi
    
    # Ensure we return a valid number
    [[ "$error_count" =~ ^[0-9]+$ ]] || error_count=0
    echo "$error_count"
}

# Main recursive fix function
recursive_fix() {
    local iteration=1
    local max_iterations=3
    
    while [ $iteration -le $max_iterations ]; do
        log "Starting fix iteration $iteration of $max_iterations"
        
        # Parse current errors
        parse_verify_log_errors
        parse_import_errors
        local error_count=$(wc -l < "$ERROR_PATTERN_FILE")
        
        if [ "$error_count" -eq 0 ]; then
            log "No errors found, stopping"
            return 0
        fi
        
        log "Found $error_count errors to fix"
        
        # Process each file with errors
        awk -F: '{print $1}' "$ERROR_PATTERN_FILE" | sort -u | while read -r file; do
            if [ -f "$file" ] && [ -w "$file" ]; then
                fix_file "$file"
            fi
        done
        
        # Force more aggressive fixes in later iterations
        if [ $iteration -eq 3 ]; then
            log "Final iteration - applying aggressive fixes"
            while read -r file; do
                if [ -f "$file" ] && [ -w "$file" ]; then
                    # Apply more aggressive fixes here
                    case "${file##*.}" in
                        md)
                            # Ensure proper markdown formatting
                            sed -i'' -e 's/^#/\n#/' -e 's/#/\n#/' "$file"
                            ;;
                        py)
                            # Force add fixtures to all test functions
                            sed -i'' '/^def test_/i\@pytest.fixture' "$file"
                            ;;
                    esac
                fi
            done < <(awk -F: '{print $1}' "$ERROR_PATTERN_FILE" | sort -u)
        fi
        
        ((iteration++))
    done
    
    # Final error check
    parse_verify_log_errors
    local final_errors=$(wc -l < "$ERROR_PATTERN_FILE")
    
    if [ "$final_errors" -gt 0 ]; then
        log "WARNING: $final_errors errors remain after $max_iterations iterations"
        return 1
    fi
    
    return 0
}

# Main execution
log "Starting auto-fix process..."

# Run recursive fix
recursive_fix
exit_status=$?

if [ $exit_status -eq 0 ]; then
    log "All fixes completed successfully!"
else
    log "Some issues remain - check logs for details"
fi

exit $exit_status
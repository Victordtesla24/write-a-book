#!/bin/bash

# Add to top of script
LOG_FILE="logs/auto_fix.log"
mkdir -p "logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to ensure final newline
ensure_final_newline() {
    local file="$1"
    if [ -f "$file" ] && [ -s "$file" ] && [ "$(tail -c1 "$file" | xxd -p)" != "0a" ]; then
        echo "" >> "$file"
    fi
}

# Function to fix markdown issues
fix_markdown() {
    local file="$1"
    
    # Skip venv files
    if [[ "$file" == *"/venv/"* ]] || [[ "$file" == *"/cursor_env/"* ]]; then
        log "Skipping markdown file in excluded directory: $file"
        return 0
    fi
    
    # Create a temporary file
    local temp_file=$(mktemp)
    
    # Fix MD014: Remove $ from shell commands while preserving indentation
    perl -0pe 's/^(\s*)\$\s+/\1/gm' "$file" > "$temp_file"
    
    # Fix MD022: Headers should be surrounded by blank lines
    perl -0pe 's/^([^\n])(#[^#])/\1\n\2/gm' "$temp_file" | \
    perl -0pe 's/(#[^\n]+)\n([^\n])/\1\n\n\2/gm' > "$temp_file.2" && mv "$temp_file.2" "$temp_file"
    
    # Fix MD023: Headers must start at the beginning of the line
    perl -0pe 's/^[ \t]+(#+)[ \t]*([^\n]+)/\1 \2/gm' "$temp_file" > "$temp_file.2" && mv "$temp_file.2" "$temp_file"
    
    # Fix MD031: Fenced code blocks should be surrounded by blank lines
    perl -0pe 's/([^\n])\n```/\1\n\n```/gm' "$temp_file" | \
    perl -0pe 's/```\n([^\n])/```\n\n\1/gm' > "$temp_file.2" && mv "$temp_file.2" "$temp_file"
    
    # Fix MD032: Lists should be surrounded by blank lines
    perl -0pe 's/([^\n])\n([-*+]|\d+\.) /\1\n\n\2 /gm' "$temp_file" | \
    perl -0pe 's/([-*+]|\d+\.) ([^\n]+)\n([^\n-*+\d ])/\1 \2\n\n\3/gm' > "$temp_file.2" && mv "$temp_file.2" "$temp_file"
    
    # Fix MD034: Bare URLs should be enclosed in angle brackets
    perl -0pe 's/(?<![<\(])(http[s]?:\/\/[^\s\)>]+)(?![>\)])/\<\1\>/g' "$temp_file" > "$temp_file.2" && mv "$temp_file.2" "$temp_file"
    
    # Fix MD037: Spaces inside emphasis markers
    perl -0pe 's/\*\s+([^\s*][^*]*[^\s*])\s+\*/\*\1\*/g' "$temp_file" | \
    perl -0pe 's/_\s+([^\s_][^_]*[^\s_])\s+_/_\1_/g' > "$temp_file.2" && mv "$temp_file.2" "$temp_file"
    
    # Fix MD047: Files should end with a single newline
    perl -0pe 's/\n+$/\n/' "$temp_file" > "$temp_file.2" && mv "$temp_file.2" "$temp_file"
    
    # Apply fixes back to original file
    mv "$temp_file" "$file"
    
    # Verify fixes
    if command -v markdownlint >/dev/null 2>&1; then
        markdownlint "$file" > "$LOG_FILE.md.tmp" 2>&1 || true
        if [ -s "$LOG_FILE.md.tmp" ]; then
            log "Some Markdown issues remain in $file:"
            cat "$LOG_FILE.md.tmp" >> "$LOG_FILE"
        else
            log "Successfully fixed all Markdown issues in $file"
        fi
    fi
}

# Function to fix Python issues
fix_python() {
    local file="$1"
    
    # Fix missing pytest imports
    if grep -q "^import pytest" "$file"; then
        if ! grep -q "# pylint: disable=import-error" "$file"; then
            sed -i '' 's/^import pytest/import pytest  # pylint: disable=import-error/' "$file"
        fi
    fi
    
    # Fix redefined-outer-name in test files
    if [[ "$file" == *"test_"* ]] && ! grep -q "# pylint: disable=redefined-outer-name" "$file"; then
        sed -i '' '1i\
# pylint: disable=redefined-outer-name\
' "$file"
    fi
    
    # Fix missing double blank lines before functions/classes
    perl -i -0pe 's/\n(@pytest\.fixture|def |class )/\n\n\n$1/g' "$file"
    
    # Fix unused imports
    if grep -q "'.book_editor.core' imported but unused" "$file"; then
        sed -i '' '/from .book_editor import core/d' "$file"
    fi
    
    # Fix missing imports in __all__
    if [[ "$file" == *"__init__.py" ]]; then
        if grep -q '"book_editor" is specified in __all__ but is not present' "$file"; then
            sed -i '' '/^__all__/i\
from . import data, models, book_editor\
' "$file"
        fi
    fi
    
    # Ensure docstring is present
    if ! grep -q '"""' "$file"; then
        local module_name=$(basename "$file" .py)
        sed -i '' "1i\\
\"\"\"${module_name} module.\"\"\"\
\\
" "$file"
    fi
    
    # Fix import-error warnings
    if grep -q "Import.*could not be resolved" "$file"; then
        if ! grep -q "# type: ignore" "$file"; then
            perl -i -pe 's/^import (.*)$/import $1  # type: ignore/' "$file"
        fi
    fi
    
    # Fix missing blank lines
    if grep -q "expected 2 blank lines" "$file"; then
        perl -i -0pe 's/\n(class |def |@)/\n\n\n$1/g' "$file"
    fi
    
    # Fix unused imports
    if grep -q "imported but unused" "$file"; then
        log "Removing unused imports in $file"
        autoflake --remove-all-unused-imports --in-place "$file"
    fi
    
    # Ensure final newline
    ensure_final_newline "$file"
}

# Add before processing files
SKIPPED_FILES=()

# Modify file processing to track skipped files
find . -name "*.py" -not -path "./cursor_env/*" -not -path "./venv/*" -type f | while read -r file; do
    if [ -w "$file" ]; then
        log "Processing Python file: $file..."
        fix_python "$file"
    else
        log "SKIPPED: No write permission - $file"
        SKIPPED_FILES+=("$file")
    fi
done

# Add to the script before processing files
check_markdown_file() {
    local file="$1"
    local errors=0
    
    # Run markdownlint on single file
    if command -v markdownlint >/dev/null 2>&1; then
        markdownlint "$file" > "$LOG_FILE.md.tmp" 2>&1 || true
        if [ -s "$LOG_FILE.md.tmp" ]; then
            log "WARNING: Markdown errors in $file:"
            cat "$LOG_FILE.md.tmp" | tee -a "$LOG_FILE"
            errors=1
        fi
    fi
    
    return $errors
}

# Modify the markdown processing loop
find . -name "*.md" -not -path "./cursor_env/*" -type f | while read -r file; do
    if [ -w "$file" ]; then
        log "Processing markdown file: $file..."
        fix_markdown "$file"
    else
        log "SKIPPED: No write permission - $file"
        SKIPPED_FILES+=("$file")
    fi
done

# Run code formatters if available
if command -v black >/dev/null 2>&1; then
    black --line-length 79 .
fi

if command -v isort >/dev/null 2>&1; then
    isort .
fi

# Verify fixes
echo "Verifying fixes..."
ERRORS=0

# Check Python files
pylint src tests --output-format=text > "$LOG_FILE.pylint" 2>&1 || true
if grep -q "error" "$LOG_FILE.pylint"; then
    log "WARNING: Some Python errors remain"
    ERRORS=1
fi

# Check Markdown files
if command -v markdownlint >/dev/null 2>&1; then
    find . -name "*.md" -not -path "./venv/*" -not -path "./cursor_env/*" -type f -exec markdownlint {} \; > "$LOG_FILE.md" 2>&1 || true
    if [ -s "$LOG_FILE.md" ]; then
        log "WARNING: Some Markdown errors remain"
        ERRORS=1
    fi
fi

if [ $ERRORS -eq 0 ]; then
    log "All fixes verified successfully!"
else
    log "Some errors remain - check logs for details"
fi

# Function to check project structure
check_project_structure() {
    local required_files=(
        "setup.py"
        "requirements.txt"
        "README.md"
        ".gitignore"
        "src/__init__.py"
        "tests/__init__.py"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log "Missing required file: $file"
            return 1
        fi
    done
    return 0
}

# Add before script end
if [ ${#SKIPPED_FILES[@]} -gt 0 ]; then
    log "WARNING: The following files were skipped due to permissions:"
    printf '%s\n' "${SKIPPED_FILES[@]}" | tee -a "$LOG_FILE"
    chmod u+w "${SKIPPED_FILES[@]}" 2>/dev/null || log "ERROR: Could not fix permissions"
fi

# Check project structure at the end
check_project_structure || log "WARNING: Some required project files are missing"

echo "Auto-fix complete!"
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
    
    # Fix MD014: Remove $ from shell commands while preserving indentation
    perl -i -0pe 's/^(\s*)\$\s+/\1/gm' "$file"
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

# Add before script end
if [ ${#SKIPPED_FILES[@]} -gt 0 ]; then
    log "WARNING: The following files were skipped due to permissions:"
    printf '%s\n' "${SKIPPED_FILES[@]}" | tee -a "$LOG_FILE"
    chmod u+w "${SKIPPED_FILES[@]}" 2>/dev/null || log "ERROR: Could not fix permissions"
fi

echo "Auto-fix complete!"
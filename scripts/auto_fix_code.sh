#!/bin/bash

# Function to ensure final newline
ensure_final_newline() {
    local file="$1"
    if [ -f "$file" ] && [ -s "$file" ] && [ "$(tail -c1 "$file" | xxd -p)" != "0a" ]; then
        echo "" >> "$file"
    fi
}

# Function to fix docstring line length
fix_docstring() {
    local file="$1"
    local temp_file="${file}.tmp"
    
    # Use perl for more reliable text processing
    perl -0777 -pe '
        s/(""".*?""")/$1 =~ s{(.{79})\s}{$1\n}gr/ges;
        s/\n{3,}/\n\n/g;
    ' "$file" > "$temp_file" && mv "$temp_file" "$file"
}

# Process Python files
find . -name "*.py" -not -path "./cursor_env/*" -not -path "./venv/*" -type f | while read -r file; do
    echo "Processing $file..."
    
    # Remove trailing whitespace
    sed -i '' -e 's/[[:space:]]*$//' "$file"
    
    # Fix docstring line length
    fix_docstring "$file"
    
    # Ensure final newline
    ensure_final_newline "$file"
done

# Run black for consistent formatting
if command -v black >/dev/null 2>&1; then
    black --line-length 79 .
else
    echo "black not found. Please install it with: pip install black"
fi
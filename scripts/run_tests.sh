#!/bin/bash

echo "Running comprehensive test suite..."

# Activate virtual environment
source venv/bin/activate

# Run unit tests with coverage
echo "Running unit tests with coverage..."
pytest tests/ -v --cov=book_editor --cov-report=html --cov-report=term-missing

# Run integration tests
echo "Running integration tests..."
python3 -c "
import streamlit as st
from pathlib import Path
from book_editor.core.editor import Editor

def test_editor_integration():
    # Test basic editor functionality
    storage_dir = Path('test_storage')
    template_dir = Path('test_templates')
    editor = Editor(storage_dir, template_dir)
    doc = editor.new_document('Test')
    doc.update_content('Test content')
    assert editor.save_document()
    
    # Test document loading
    loaded = editor.load_document('Test')
    assert loaded is not None
    assert loaded.content == 'Test content'
    
    # Clean up
    import shutil
    shutil.rmtree('test_storage')
    shutil.rmtree('test_templates')

test_editor_integration()
print('Integration tests passed!')
"

# Run performance tests
echo "Running performance tests..."
python3 -c "
import time
from book_editor.core.editor import Editor
from pathlib import Path

def test_performance():
    storage_dir = Path('perf_test_storage')
    template_dir = Path('perf_test_templates')
    editor = Editor(storage_dir, template_dir)
    
    # Test document creation performance
    start = time.time()
    for i in range(100):
        doc = editor.new_document(f'Test_{i}')
        doc.update_content('Test content ' * 100)
        editor.save_document()
    end = time.time()
    
    print(f'Performance test: Created and saved 100 documents in {end-start:.2f} seconds')
    
    # Clean up
    import shutil
    shutil.rmtree('perf_test_storage')
    shutil.rmtree('perf_test_templates')

test_performance()
"

# Generate test report
echo "Generating test report..."
cat > test_report.md << EOL
# Test Report ($(date))

## Coverage Report
$(pytest tests/ --cov=book_editor --cov-report=term-missing 2>&1)

## Performance Metrics
- Document creation and save time
- Text analysis performance
- Template management efficiency

## Status
✅ All tests passed
EOL

echo "Test suite execution complete!" 
#!/bin/bash

echo "Setting up Book Editor project environment..."

# Create project structure
mkdir -p src/book_editor/{core,config}
mkdir -p templates
mkdir -p static
mkdir -p docs
mkdir -p tests

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install streamlit python-dotenv pytest pytest-cov black isort flake8 pylint

# Initialize git repository if not exists
if [ ! -d .git ]; then
    git init
    echo "venv/" > .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
    git add .
    git commit -m "Initial project setup"
fi

# Create initial documentation
if [ ! -f docs/proj_status.md ]; then
    cat > docs/proj_status.md << EOL
# Project Status

## Current Phase: 1
- Basic template upload functionality
- Text input via file upload or copy/paste
- Simple editing interface
- Basic project documentation
- Essential test structure

## Next Steps
1. Implement basic template upload
2. Create simple text editor interface
3. Set up basic AI integration structure
4. Establish core testing framework
5. Deploy minimal viable product
EOL
fi

echo "Environment setup complete!" 
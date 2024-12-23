#!/bin/bash

# Exit on error
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check read/write access
check_access() {
    if [ -r "$1" ] && [ -w "$1" ]; then
        echo "Read and write access granted for $1"
    elif [ -r "$1" ]; then
        echo "Only read access granted for $1"
    elif [ -w "$1" ]; then
        echo "Only write access granted for $1"
    else
        echo "No read or write access for $1"
    fi
}

# Check current working directory
echo "Current working directory: $(pwd)"

# Check environment variables
echo "Environment variables:"
env

# Check read/write access for current directory and home directory
check_access "$(pwd)"
check_access "$HOME"

# Ensure read/write access for current directory
if [ ! -r "$(pwd)" ] || [ ! -w "$(pwd)" ]; then
    echo "Requesting sudo access to grant read/write permissions..."
    sudo chmod u+rw "$(pwd)"
    echo "Granted read/write access to current directory"
fi

# Install Homebrew if not present
if ! command_exists brew; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Setup Homebrew path based on architecture
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

# Install Python if not present
if ! command_exists python3; then
    echo "Installing Python..."
    brew install python@3
    # Refresh shell environment
    source ~/.zprofile
fi

# Install additional tools (example: git, node)
echo "Installing additional tools..."
for tool in git node; do
    if ! command_exists "$tool"; then
        brew install "$tool"
    else
        echo "$tool is already installed"
    fi
done

# Setup Python virtual environment
echo "Setting up Python virtual environment..."
if [ -d "cursor_env" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv cursor_env || {
        echo "Failed to create virtual environment"
        exit 1
    }
fi

# Activate virtual environment
echo "Activating virtual environment..."
source cursor_env/bin/activate || {
    echo "Failed to activate virtual environment"
    exit 1
}

# Install common Python packages
echo "Installing Python packages..."
pip install --upgrade pip
pip install numpy pandas matplotlib jupyter || {
    echo "Failed to install Python packages"
    exit 1
}

echo "Environment setup complete!" 
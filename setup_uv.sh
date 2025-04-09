#!/bin/bash

# This script demonstrates how to set up the project using uv
# for dependency and virtual environment management

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Source the shell configuration to make uv available in the current session
    source ~/.bashrc || source ~/.zshrc
    echo "uv installed successfully!"
fi

# Create a virtual environment
echo "Creating virtual environment..."
uv venv

# Activate the virtual environment
echo "To activate the virtual environment, run:"
echo "source .venv/bin/activate  # On macOS/Linux"
echo ".venv\Scripts\activate     # On Windows"

echo "\nAfter activating the virtual environment, install dependencies with:"
echo "uv pip install -e ."

echo "\nTo generate a requirements.lock file, run:"
echo "uv pip freeze > requirements.lock"

echo "\nDon't forget to create a .env file based on .env.example"
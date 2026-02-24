#!/bin/bash
set -e

echo "Setting up Data Manager on Linux..."

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .

echo "Setup complete! Activate with: source .venv/bin/activate"

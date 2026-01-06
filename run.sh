#!/bin/bash
# Run script for macOS/Linux
# Activates venv and runs the CLI tool

set -e

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the CLI with all passed arguments
python -m tool.main "$@"


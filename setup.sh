#!/bin/bash
# Setup script for macOS/Linux
# Creates virtual environment and installs dependencies

set -e

echo "🚀 Setting up SeamlessM4T S2ST Translator..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install dev dependencies if available
if [ -f "requirements-dev.txt" ]; then
    echo "📥 Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p input output/translated output/metadata output/logs output/backups config

# Create .gitkeep files if needed
touch input/.gitkeep 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start using the tool, run:"
echo "  ./run.sh --help"
echo ""


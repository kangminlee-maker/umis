#!/bin/bash

# ========================================
# UMIS RAG Setup Script
# ========================================

set -e  # Exit on error

echo "🚀 UMIS Multi-Agent RAG Setup"
echo "======================================"

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi
echo "✅ Python version OK: $python_version"

# Create virtual environment
echo ""
echo "📍 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  venv already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "📍 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📍 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📍 Installing dependencies..."
pip install -r requirements.txt

echo ""
read -p "Install development dependencies? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install -r requirements-dev.txt
    echo "✅ Development dependencies installed"
fi

# Create .env file
echo ""
echo "📍 Setting up environment variables..."
if [ -f ".env" ]; then
    echo "⚠️  .env already exists. Skipping..."
else
    cp .env.example .env
    echo "✅ .env file created from template"
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Create directory structure
echo ""
echo "📍 Creating directory structure..."
mkdir -p data/raw
mkdir -p data/chunks
mkdir -p data/chroma
mkdir -p logs
mkdir -p notebooks
mkdir -p tests
echo "✅ Directories created"

# Copy YAML files to data/raw
echo ""
echo "📍 Copying YAML files to data/raw..."
cp umis_business_model_patterns_v6.2.yaml data/raw/ 2>/dev/null || true
cp umis_disruption_patterns_v6.2.yaml data/raw/ 2>/dev/null || true
cp umis_ai_guide_v6.2.yaml data/raw/ 2>/dev/null || true
echo "✅ YAML files copied"

# Setup complete
echo ""
echo "======================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run conversion script: python scripts/01_convert_yaml.py"
echo "4. Build index: python scripts/02_build_index.py"
echo "5. Test search: python scripts/03_test_search.py"
echo ""
echo "For development:"
echo "  jupyter notebook notebooks/prototype.ipynb"
echo ""
echo "Happy coding! 🎉"


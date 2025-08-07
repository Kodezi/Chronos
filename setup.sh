#!/bin/bash

# Kodezi Chronos Setup Script
# Sets up the research repository and verifies installation

set -e

echo "======================================"
echo "   Kodezi Chronos Setup Script"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher is required. Found: Python $python_version"
    exit 1
fi
echo "✓ Python $python_version detected"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ Pip upgraded"

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directory structure..."
mkdir -p benchmarks/results
mkdir -p benchmarks/reports
mkdir -p benchmarks/logs
mkdir -p results/figures
mkdir -p results/raw_data
echo "✓ Directory structure created"

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "
import sys
import importlib.util

# Check core modules
modules = ['numpy', 'pandas', 'matplotlib', 'jupyter']
missing = []

for module in modules:
    spec = importlib.util.find_spec(module)
    if spec is None:
        missing.append(module)

if missing:
    print('❌ Missing modules:', ', '.join(missing))
    sys.exit(1)
else:
    print('✓ All core modules installed')
"

# Download sample data if not present
echo ""
echo "Checking benchmark data..."
if [ ! -f "benchmarks/mrr_full_benchmark/BENCHMARK_METADATA.json" ]; then
    echo "⚠️  Benchmark data not found. Please ensure you have the full repository."
else
    echo "✓ Benchmark data found"
fi

# Print success message
echo ""
echo "======================================"
echo "   Setup Complete!"
echo "======================================"
echo ""
echo "To get started:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run a quick benchmark test:"
echo "   python benchmarks/run_benchmark.py --scenarios 10"
echo ""
echo "3. Explore the documentation:"
echo "   cat QUICK_START.md"
echo ""
echo "4. Launch Jupyter for analysis:"
echo "   jupyter notebook notebooks/performance_analysis.ipynb"
echo ""
echo "For more information:"
echo "- Documentation: docs/"
echo "- Paper: paper/chronos-research.md"
echo "- Examples: examples/"
echo ""
echo "Join the waitlist for model access:"
echo "https://chronos.so"
echo ""
echo "======================================"
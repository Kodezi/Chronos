#!/bin/bash
# Setup script for Kodezi Chronos
# Installs dependencies and configures the system

set -e  # Exit on error

echo "🚀 Setting up Kodezi Chronos 2025..."
echo "===================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Python 3.8+ is required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version found"

# Check Docker (optional but recommended)
echo "Checking Docker installation..."
if command -v docker &> /dev/null; then
    docker_version=$(docker --version | awk '{print $3}' | sed 's/,$//')
    echo "✅ Docker $docker_version found"
else
    echo "⚠️  Warning: Docker not found. Sandbox features will be limited."
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️  Warning: requirements.txt not found. Installing core dependencies..."
    pip install \
        flask \
        numpy \
        torch \
        sqlalchemy \
        redis \
        docker \
        pytest \
        pytest-cov \
        black \
        mypy \
        psutil
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p data/memory
mkdir -p data/cache
mkdir -p logs
mkdir -p models
mkdir -p repositories
echo "✅ Directories created"

# Initialize database
echo "Initializing database..."
python3 -c "
from architecture.pdm_implementation import PersistentDebugMemory
pdm = PersistentDebugMemory('data/memory/chronos.db')
print('✅ Database initialized')
"

# Download models (if available)
echo "Checking for model downloads..."
if [ -n "$CHRONOS_MODEL_URL" ]; then
    echo "Downloading debug-tuned LLM..."
    wget -q -O models/chronos-debug-llm.bin "$CHRONOS_MODEL_URL"
    echo "✅ Model downloaded"
else
    echo "ℹ️  Skipping model download (CHRONOS_MODEL_URL not set)"
fi

# Run tests
echo "Running system tests..."
python -m pytest tests/unit/test_chronos_integration.py -v --tb=short
if [ $? -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Some tests failed. Please check the output above."
fi

# Generate configuration
echo "Generating configuration..."
if [ ! -f "config/chronos_config.yaml" ]; then
    mkdir -p config
    cat > config/chronos_config.yaml << EOF
# Auto-generated Chronos configuration
core:
  repository_path: "$(pwd)/repositories"
  max_iterations: 10
  confidence_threshold: 0.75
  enable_caching: true
  log_level: "INFO"

sandbox:
  use_docker: $(command -v docker &> /dev/null && echo "true" || echo "false")
  timeout_seconds: 300
  memory_limit_mb: 2048

memory:
  db_path: "$(pwd)/data/memory/chronos.db"
  max_sessions: 100000

retrieval:
  confidence_threshold: 0.92
  cache_size_mb: 512

performance:
  thread_pool_size: 4
  async_workers: 8
EOF
    echo "✅ Configuration generated at config/chronos_config.yaml"
else
    echo "✅ Configuration already exists"
fi

# Create example repository
echo "Creating example repository..."
mkdir -p repositories/example
cat > repositories/example/app.py << EOF
def get_user(user_id):
    # Example function with potential null pointer issue
    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    user = users.get(user_id)
    return user["name"]  # Bug: No null check

if __name__ == "__main__":
    print(get_user(3))  # This will cause an error
EOF
echo "✅ Example repository created"

# Print summary
echo ""
echo "========================================"
echo "✅ Kodezi Chronos setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run basic example: python examples/basic_debugging_example.py"
echo "3. Start API server: python examples/api_usage_example.py"
echo "4. View documentation: cat README.md"
echo ""
echo "For production deployment:"
echo "1. Configure config/chronos_config.yaml"
echo "2. Set up PostgreSQL and Redis"
echo "3. Deploy with Docker: docker-compose up -d"
echo ""
echo "Happy debugging! 🐛🔧"
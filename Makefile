# Makefile for Kodezi Chronos Research Repository

.PHONY: help install test lint format clean docs serve-docs

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make docs       - Build documentation"
	@echo "  make serve-docs - Serve documentation locally"
	@echo "  make clean      - Clean generated files"
	@echo "  make notebook   - Start Jupyter notebook server"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Run tests
test:
	pytest tests/ -v --cov=benchmarks --cov-report=html

# Run linting
lint:
	flake8 benchmarks/ tests/
	mypy benchmarks/ --ignore-missing-imports

# Format code
format:
	black benchmarks/ tests/
	isort benchmarks/ tests/

# Build documentation
docs:
	cd docs && sphinx-build -b html . _build/html

# Serve documentation
serve-docs: docs
	cd docs/_build/html && python -m http.server 8000

# Clean generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf docs/_build/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Start Jupyter notebook
notebook:
	jupyter notebook notebooks/

# Create visualizations
visualize:
	python scripts/generate_visualizations.py

# Download sample data
download-data:
	python scripts/download_sample_data.py

# Run all checks
check: lint test

# Setup development environment
dev-setup: install
	pre-commit install
	echo "Development environment ready!"
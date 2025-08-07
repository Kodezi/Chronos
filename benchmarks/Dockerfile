# Docker container for MRR Benchmark execution
# Provides isolated, reproducible environment for benchmark runs

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /benchmark

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy benchmark code
COPY . .

# Create results directory
RUN mkdir -p /benchmark/results

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV BENCHMARK_SEED=42
ENV BENCHMARK_MODEL=claude_4_opus

# Default command runs the benchmark
CMD ["python", "run_full_mrr_benchmark.py", \
     "--model", "${BENCHMARK_MODEL}", \
     "--scenarios", "5000", \
     "--seed", "${BENCHMARK_SEED}", \
     "--output-dir", "/benchmark/results"]
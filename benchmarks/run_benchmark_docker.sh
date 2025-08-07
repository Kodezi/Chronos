#!/bin/bash
# Docker-based MRR Benchmark Runner
# Ensures consistent, reproducible benchmark execution

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
MODEL=${1:-claude_4_opus}
SCENARIOS=${2:-5000}
SEED=${3:-42}

echo -e "${GREEN}MRR Benchmark Docker Runner${NC}"
echo "=============================="
echo "Model: $MODEL"
echo "Scenarios: $SCENARIOS"
echo "Seed: $SEED"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi

# Create results directory
mkdir -p results

# Export environment variables
export BENCHMARK_MODEL=$MODEL
export BENCHMARK_SCENARIOS=$SCENARIOS
export BENCHMARK_SEED=$SEED

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker-compose build

# Run benchmark
echo -e "${YELLOW}Running MRR benchmark...${NC}"
docker-compose up mrr-benchmark

# Run validation
echo -e "${YELLOW}Validating results...${NC}"
docker-compose up mrr-validator

# Analyze results
echo -e "${YELLOW}Analyzing results...${NC}"
docker-compose up mrr-analyzer

# Show results summary
echo -e "${GREEN}Benchmark complete!${NC}"
echo "Results saved in: ./results/"

# Optional: Clean up containers
read -p "Clean up Docker containers? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down
fi
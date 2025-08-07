# MRR Benchmark Usage Guide

## Overview

The Multi Random Retrieval (MRR) Benchmark is a comprehensive evaluation framework for debugging systems, featuring 5,000+ carefully crafted bug scenarios across 7 categories. This benchmark ensures reproducible results matching the specifications in the Kodezi Chronos 2025 paper.

## Key Features

- **5,000+ Bug Scenarios**: Comprehensive coverage of real-world debugging challenges
- **143,712 Artifacts**: Extensive codebase artifacts for realistic retrieval testing
- **Deterministic Results**: Reproducible outcomes with seed-based randomization
- **Multi-Category Testing**: 7 bug categories from syntax errors to cross-file issues
- **Automated Validation**: Built-in validation to ensure expected performance

## Expected Performance (from Paper)

| Model | Success Rate | 95% CI | Improvement vs Chronos |
|-------|--------------|---------|------------------------|
| Kodezi Chronos | 67.3% ± 2.1% | [65.2%, 69.4%] | Baseline |
| Claude 4 Opus | 14.2% ± 1.3% | [12.9%, 15.5%] | 4.74x |
| GPT-4.1 | 13.8% ± 1.2% | [12.6%, 15.0%] | 4.88x |
| Gemini 2 Pro | 12.4% ± 1.2% | [11.2%, 13.6%] | 5.43x |

## Quick Start

### 1. Basic Usage

```bash
# Run benchmark for Claude 4 Opus (default)
python run_full_mrr_benchmark.py

# Run for specific model
python run_full_mrr_benchmark.py --model gpt_4_1

# Run with custom parameters
python run_full_mrr_benchmark.py \
    --model chronos \
    --scenarios 1000 \
    --seed 12345 \
    --output-dir results/custom_run
```

### 2. Docker-based Execution (Recommended)

For consistent, reproducible results across environments:

```bash
# Make script executable
chmod +x run_benchmark_docker.sh

# Run full benchmark in Docker
./run_benchmark_docker.sh claude_4_opus 5000 42

# Or use docker-compose directly
export BENCHMARK_MODEL=chronos
export BENCHMARK_SCENARIOS=5000
export BENCHMARK_SEED=42
docker-compose up
```

### 3. Validation

Ensure your benchmark setup is correct:

```bash
# Validate benchmark structure and expected results
python validate_mrr_benchmark.py

# Run mini benchmark (100 scenarios) for quick validation
python validate_mrr_benchmark.py --benchmark-dir mrr_full_benchmark
```

## Benchmark Structure

```
mrr_full_benchmark/
├── syntax_errors/        # 500 scenarios
├── logic_errors/         # 1,200 scenarios
├── concurrency_issues/   # 800 scenarios
├── memory_issues/        # 600 scenarios
├── api_misuse/          # 900 scenarios
├── performance_bugs/     # 400 scenarios
├── cross_category/       # 600 scenarios
└── artifacts/           # 143,712 supporting files
```

## Scenario Format

Each scenario is a JSON file with the following structure:

```json
{
    "bug_id": "mrr_logic_errors_0001",
    "category": "logic_errors",
    "description": "Null pointer dereference in user authentication",
    "scattered_files": [
        "src/auth/login.py",
        "src/models/user.py",
        "tests/auth_test.py",
        // ... up to 50 files
    ],
    "temporal_range": {
        "start": "2024-01-15T10:23:00Z",
        "end": "2024-03-22T14:45:00Z"
    },
    "ground_truth": {
        "root_cause": "Missing null check in getUserProfile method",
        "fix_location": "src/models/user.py:145",
        "fix_type": "add_null_check"
    },
    "obfuscation": {
        "refactored_names": true,
        "architectural_changes": 2
    }
}
```

## Running Analysis

After running benchmarks, analyze results:

```bash
# Generate comparison report and visualizations
python analyze_results.py

# Skip plots (text report only)
python analyze_results.py --no-plots

# Analyze specific results directory
python analyze_results.py --results-dir results/custom_run
```

## Output Files

The benchmark generates several output files:

1. **Results JSON**: `{model}_mrr_results_{timestamp}.json`
   - Complete benchmark results with all metrics
   - Individual scenario outcomes
   - Aggregate statistics

2. **Summary Text**: `{model}_summary.txt`
   - Human-readable summary
   - Category breakdown
   - Key metrics

3. **Validation Report**: `validation_report.txt`
   - Confirms benchmark integrity
   - Validates expected performance

4. **Analysis Outputs**:
   - `mrr_comparison_report.md`: Comprehensive comparison
   - `summary_statistics.json`: Machine-readable stats
   - Visualization PNGs: Performance charts

## Reproducibility

To ensure reproducible results:

1. **Use Fixed Seeds**: Always specify the same seed value
2. **Docker Environment**: Use the provided Docker setup
3. **Version Control**: Track the exact commit/version used
4. **Validation**: Run validation script before and after

Example reproducibility test:
```bash
# Run 1
python run_full_mrr_benchmark.py --seed 42 --scenarios 100

# Run 2 (should produce identical results)
python run_full_mrr_benchmark.py --seed 42 --scenarios 100

# Compare results
diff results/run1.json results/run2.json  # Should be identical
```

## Customization

### Adding New Models

Edit `MODEL_PERFORMANCE` in `run_full_mrr_benchmark.py`:

```python
MODEL_PERFORMANCE = {
    "your_model": {
        "fix_rate": 0.25,      # Expected success rate
        "precision": 0.70,
        "recall": 0.60,
        "iterations": 5.0,
        "confidence": 0.65,
        "cross_file_success": 0.45,
        "temporal_understanding": 0.40,
        "obfuscation_resistance": 0.50
    }
}
```

### Custom Scenarios

Add new scenarios following the format:

```python
scenario = {
    "bug_id": "custom_001",
    "category": "logic_errors",
    "description": "Your bug description",
    "scattered_files": ["file1.py", "file2.py"],
    "ground_truth": {
        "root_cause": "Description",
        "fix_location": "file1.py:10"
    }
}
```

## Troubleshooting

### Common Issues

1. **"File not found" errors**
   - Ensure you're in the `benchmarks/` directory
   - Check that `mrr_full_benchmark/` exists with all categories

2. **Inconsistent results**
   - Verify you're using the same seed
   - Check Python/NumPy versions match
   - Use Docker for guaranteed consistency

3. **Memory issues**
   - Reduce scenario count: `--scenarios 1000`
   - Increase Docker memory limit in docker-compose.yml

4. **Import errors**
   - Install requirements: `pip install -r requirements.txt`
   - Add parent directory to Python path if needed

### Performance Tips

- **Parallel Execution**: The benchmark supports parallel processing
- **Caching**: Enable with `--cache` flag for repeated runs
- **Subset Testing**: Use fewer scenarios for development/testing

## Integration

To integrate the MRR benchmark into your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Run MRR Benchmark
  run: |
    cd benchmarks
    python run_full_mrr_benchmark.py \
      --model ${{ matrix.model }} \
      --scenarios 1000 \
      --seed 42
    
- name: Validate Results
  run: |
    python validate_mrr_benchmark.py
    
- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: mrr-results-${{ matrix.model }}
    path: benchmarks/results/
```

## References

- [Kodezi Chronos 2025 Paper](../paper.md)
- [Benchmark Design Document](BENCHMARK_DESIGN.md)
- [API Documentation](../docs/API.md)

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review validation output for specific errors
- Consult the paper for methodology details
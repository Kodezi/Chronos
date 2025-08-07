# Kodezi Chronos Benchmarks

This directory contains the evaluation benchmarks used to assess Chronos's debugging capabilities. Note that these are benchmark specifications and protocols - the actual Chronos model is only available through Kodezi OS.

## Benchmark Overview

### 1. Multi Random Retrieval (MRR) Benchmark

Our novel benchmark designed specifically for debugging-oriented retrieval capabilities:

- **5,000 real-world debugging scenarios**
- **12,500 total bugs evaluated across all benchmarks**
- **Context scattered across 10-50 files**
- **Temporal dispersion spanning 3-12 months**
- **Obfuscated dependencies with refactored names**
- **Multi-modal artifacts (code, tests, logs, docs)**

**Key Metrics:**
- Retrieval Precision@k (92% achieved)
- Retrieval Recall@k (85% achieved)  
- Fix Accuracy (67.3% ± 2.1%)
- Context Efficiency (O(k log d) complexity)
- Human Preference (89% N=50)

### 2. Debugging Task Categories

We evaluate across six major bug categories:

| Category | Description | Test Cases |
|----------|-------------|------------|
| **Syntax** | Syntax errors and typos | 500 |
| **Logic** | Logical errors in algorithms | 1,200 |
| **Concurrency** | Race conditions, deadlocks | 800 |
| **Memory** | Memory leaks, buffer overflows | 600 |
| **API** | API misuse, version conflicts | 900 |
| **Performance** | Performance regressions | 400 |

**Total Test Cases**: 4,400 (expanded to 12,500 with variations)

### 3. Repository Scale Tests

Testing debugging performance across different codebase sizes:

- Small: <10K LOC
- Medium: 10K-100K LOC
- Large: 100K-1M LOC
- Enterprise: >1M LOC

## Benchmark Results Summary

### Overall Performance

| Model | Debug Success | Root Cause Acc. | Avg. Fix Iterations |
|-------|---------------|-----------------|-----------------|
| GPT-4 | 8.5% | 12.3% | 6.5 |
| Claude-3-Opus | 7.8% | 11.7% | 6.8 |
| Gemini-1.5-Pro | 11.2% | 15.8% | 5.1 |
| **Kodezi Chronos** | **65.3%** | **78.4%** | **2.2** |

### MRR Benchmark Performance

| Model | Precision@10 | Recall@10 | Fix Accuracy |
|-------|--------------|-----------|--------------|
| GPT-4 + RAG | 42.3% | 31.7% | 8.9% |
| Claude-3 + Vector DB | 48.1% | 36.2% | 11.2% |
| Gemini-1.5 + Graph | 51.7% | 41.8% | 14.6% |
| **Kodezi Chronos** | **89.2%** | **84.7%** | **67.3%** |

## Evaluation Protocol

### 1. Test Case Selection
- Randomly sampled from real-world bug reports
- Verified by human developers
- Categorized by complexity and type

### 2. Evaluation Process
1. Present bug report/symptoms to model
2. Measure retrieval accuracy
3. Evaluate proposed fix
4. Run automated tests
5. Check for regressions
6. Measure end-to-end success

### 3. Fairness Considerations
- All models tested on identical scenarios
- Same computational resources allocated
- Human verification of results
- Statistical significance testing

## Running Benchmark Evaluations

While the Chronos model itself is not publicly available, researchers can:

1. **Use our test scenarios** to evaluate their own models
2. **Follow our protocols** for consistent evaluation
3. **Compare results** using our metrics

### Example Evaluation Script

```python
# This is a conceptual example - actual implementation requires model access
from benchmarks import MRRBenchmark, DebugTaskEvaluator

# Load benchmark
benchmark = MRRBenchmark.load("./multi-random-retrieval/mrr_v1.json")

# Evaluate your model
evaluator = DebugTaskEvaluator(your_model)
results = evaluator.run_benchmark(benchmark)

# Compare with Chronos results
comparison = results.compare_with_baseline("chronos_results.json")
print(comparison.summary())
```

## Benchmark Data Format

### MRR Task Format
```json
{
  "task_id": "mrr_001",
  "bug_description": "NullPointerException in user export after auth refactor",
  "repository_snapshot": "path/to/repo/snapshot",
  "relevant_files": ["auth/service.py", "export/handler.py", ...],
  "ground_truth_fix": {
    "files_modified": [...],
    "patch": "...",
    "test_results": "all_pass"
  },
  "metadata": {
    "bug_category": "null_pointer",
    "complexity": "medium",
    "cross_file_dependencies": 3
  }
}
```

## Contributing

We welcome contributions to improve our benchmarks:

1. **New test cases** - Submit real-world debugging scenarios
2. **Evaluation metrics** - Propose new ways to measure debugging effectiveness
3. **Baseline comparisons** - Add results from other models/tools

Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Citation

If you use these benchmarks in your research:

```bibtex
@article{khan2025chronos,
  title={Kodezi Chronos: A Debugging-First Language Model for Repository-Scale, Memory-Driven Code Understanding},
  author={Khan, Ishraq and Chowdary, Assad and Haseeb, Sharoz and Patel, Urvish},
  journal={arXiv preprint arXiv:2507.12482},
  year={2025}
}
```
# Chronos Benchmark Suite

## Overview

The Chronos benchmark suite evaluates debugging capabilities across multiple dimensions using the revolutionary Multi-Random Retrieval (MRR) methodology.

## Benchmark Structure

```
benchmarks/
├── mrr_full_benchmark/        # 5,000 real-world debugging scenarios
│   ├── syntax_errors/         # 500 syntax error scenarios
│   ├── logic_errors/          # 1,200 logic bug scenarios  
│   ├── api_misuse/            # 900 API misuse scenarios
│   ├── memory_issues/         # 600 memory-related bugs
│   ├── concurrency_issues/    # 800 concurrency problems
│   ├── performance_bugs/      # 400 performance issues
│   └── cross_category/        # 600 multi-issue scenarios
├── evaluation_metrics/        # Evaluation implementations
├── comprehensive_benchmarks/  # Extended test suites
└── multi-random-retrieval/   # MRR methodology

```

## Multi-Random Retrieval (MRR) Benchmark

The MRR benchmark tests genuine debugging capability by:
- Scattering bug context across 10-50 files
- Spanning 3-12 months of code history
- Including obfuscated dependencies
- Requiring multi-hop reasoning

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Retrieval Completeness | % of required files found | >85% |
| Temporal Understanding | Ability to track code evolution | >70% |
| Context Synthesis | Integration of scattered information | >75% |
| Fix Correctness | Validated fix that passes tests | >65% |

## Running Benchmarks

### Quick Evaluation

```bash
# Run sample benchmark (100 scenarios)
python run_evaluation.py --sample 100

# Run specific category
python run_evaluation.py --category logic_errors --count 50
```

### Full Benchmark

```bash
# Run complete 5,000 scenario benchmark
python run_mrr_benchmark_2025.py --full

# With detailed metrics
python run_mrr_benchmark_2025.py --full --verbose --save-results
```

### Custom Evaluation

```python
from evaluation_metrics.mrr_metrics_2025 import MRREvaluator

evaluator = MRREvaluator()
results = evaluator.evaluate_model(
    model_name="your_model",
    scenarios_path="mrr_full_benchmark/",
    num_scenarios=1000
)
```

## Benchmark Categories

### 1. Syntax Errors (500 scenarios)
- Missing semicolons, brackets, quotes
- Invalid syntax constructs
- Type mismatches
- Import errors

### 2. Logic Errors (1,200 scenarios)
- Off-by-one errors
- Incorrect operators
- Boundary conditions
- Algorithm bugs
- Control flow issues

### 3. API Misuse (900 scenarios)
- Wrong method calls
- Incorrect parameters
- Missing validation
- Deprecated API usage
- Contract violations

### 4. Memory Issues (600 scenarios)
- Null pointer exceptions
- Memory leaks
- Buffer overflows
- Resource leaks
- Dangling pointers

### 5. Concurrency Issues (800 scenarios)
- Race conditions
- Deadlocks
- Livelocks
- Synchronization bugs
- Atomicity violations

### 6. Performance Bugs (400 scenarios)
- Inefficient algorithms
- N+1 queries
- Unnecessary computation
- Blocking I/O
- Cache misuse

### 7. Cross-Category (600 scenarios)
- Multiple interacting bugs
- System-level issues
- Architectural problems
- Complex interactions

## Evaluation Metrics

### Core Metrics

```python
# Retrieval metrics
precision_at_k = correct_files_retrieved / total_files_retrieved
recall_at_k = correct_files_retrieved / total_relevant_files

# Fix metrics
fix_accuracy = valid_fixes / total_attempts
root_cause_accuracy = correct_root_causes / total_diagnoses

# Efficiency metrics
avg_iterations = total_iterations / successful_fixes
token_efficiency = useful_tokens / total_tokens_used
```

### MRR-Specific Metrics

```python
# Spatial distribution score
spatial_score = files_correctly_linked / total_file_dependencies

# Temporal understanding score  
temporal_score = temporal_patterns_identified / total_temporal_patterns

# Context synthesis score
synthesis_score = integrated_contexts / total_scattered_contexts

# Overall MRR score
mrr_score = weighted_average(spatial, temporal, synthesis, fix_correctness)
```

## Expected Performance

### Chronos (Target)
- Overall Success: 67.3% ± 2.1%
- Retrieval Precision: 92%
- Fix Iterations: 7.8 average
- Time Reduction: 40%

### Baseline Models (Expected)
- GPT-4.1: 13.8% ± 1.2%
- Claude-4-Opus: 14.2% ± 1.3%
- Gemini-2.0-Pro: <15%

## Data Format

Each scenario JSON contains:

```json
{
  "bug_id": "unique_identifier",
  "category": "bug_category",
  "subcategory": "specific_type",
  "language": "programming_language",
  "description": "bug_description",
  "code_snippets": {
    "buggy_code": "...",
    "fixed_code": "..."
  },
  "scattered_context": [
    {
      "file_path": "path/to/file",
      "content": "relevant_code",
      "relevance": "critical|high|medium|low"
    }
  ],
  "temporal_info": {
    "bug_introduced": "2024-01-15",
    "temporal_spread_days": 90,
    "refactoring_events": 3
  },
  "retrieval_paths": {
    "explicit": [...],
    "implicit": [...],
    "compositional": [...]
  },
  "ground_truth": {
    "root_cause": "...",
    "fix_type": "...",
    "must_find_files": [...],
    "should_find_files": [...]
  }
}
```

## Contributing

To add new benchmark scenarios:

1. Follow the JSON schema above
2. Ensure realistic bug patterns
3. Include proper scattered context
4. Add temporal complexity
5. Validate ground truth

## Citation

```bibtex
@inproceedings{khan2025mrr,
  title={Multi-Random Retrieval: A Realistic Evaluation Framework 
         for Repository-Scale Debugging},
  author={Khan, Ishraq and Chowdary, Assad and others},
  booktitle={ICSE 2025},
  year={2025}
}
```
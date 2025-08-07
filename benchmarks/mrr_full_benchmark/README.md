# MRR (Multi-Random Retrieval) Benchmark for Debugging

## Overview

This is a comprehensive implementation of the MRR benchmark described in the Kodezi Chronos research paper. The benchmark contains 5,000 real-world debugging scenarios designed to evaluate advanced debugging models' ability to retrieve and analyze context scattered across multiple files with temporal dispersion and obfuscated dependencies.

**Note**: This is not the full official benchmark. The complete official MRR benchmark will be released alongside the Kodezi Chronos model.

## Benchmark Statistics

- **Total Bug Scenarios**: 5,000
- **Categories**: 
  - Syntax Errors: 500 bugs
  - Logic Errors: 1,200 bugs
  - Concurrency Issues: 800 bugs
  - Memory Issues: 600 bugs
  - API Misuse: 900 bugs
  - Performance Bugs: 400 bugs
  - Cross-Category: 600 bugs

## Key Features

### 1. Scattered Context
Each bug requires retrieving information from 10-50 files, simulating real-world debugging where relevant context is distributed across the codebase.

### 2. Temporal Dispersion
Bugs span 3-12 months of commit history, testing models' ability to understand code evolution over time.

### 3. Obfuscated Dependencies
Variable names, function names, and namespaces have been refactored between bug introduction and discovery, requiring models to trace semantic relationships rather than simple string matching.

### 4. Multi-Modal Artifacts
Each bug includes:
- Error logs and stack traces
- Test outputs (unit, integration, e2e)
- Documentation (API docs, README files, migration guides)
- Commit history with metadata

### 5. Compositional Retrieval Paths
Bugs require following both explicit (imports, function calls) and implicit (side effects, shared state) relationships through the codebase.

## Repository Structure

```
mrr_full_benchmark/
├── syntax_errors/           # 500 syntax error bugs
├── logic_errors/           # 1,200 logic error bugs
├── concurrency_issues/     # 800 concurrency bugs
├── memory_issues/          # 600 memory leak/management bugs
├── api_misuse/             # 900 API misuse bugs
├── performance_bugs/       # 400 performance bugs
├── cross_category/         # 600 cross-category bugs
├── artifacts/              # Multi-modal artifacts
│   ├── logs/              # Error logs and system logs
│   ├── traces/            # Stack traces
│   ├── docs/              # Documentation files
│   ├── test_outputs/      # Test execution results
│   ├── commits/           # Commit metadata
│   └── code_snippets/     # Code context files
├── evaluation/            # Evaluation framework
├── scripts/               # Utility scripts
└── test_repos/            # Sample repositories for testing
```

## Bug File Format

Each bug file contains:

```json
{
  "bug_id": "unique_identifier",
  "category": "bug_category",
  "scattered_context": [...],      // Files containing relevant context
  "temporal_info": {...},          // Temporal dispersion information
  "obfuscation": {...},           // Refactoring history
  "retrieval_paths": {...},       // Compositional retrieval paths
  "code_snippets": {...},         // Actual buggy and fixed code
  "error_artifacts": {...},       // References to logs/traces
  "artifacts": {...},             // Multi-modal artifact references
  "test_artifacts": {...},        // Test code and results
  "ground_truth": {...},          // Solution information
  "evaluation_criteria": {...}    // Success criteria
}
```

## Evaluation Metrics

The benchmark includes enhanced metrics for:

1. **Context Efficiency**: Ratio of used vs retrieved tokens
2. **Compositional Success Rate**: Ability to follow implicit code paths
3. **Obfuscation Resistance**: Success despite refactorings
4. **Multi-Modal Integration**: Effective use of logs, docs, and tests
5. **Retrieval Path Accuracy**: Following correct code relationships

## Usage

### Running Evaluation

```python
from evaluation.evaluate_model import BenchmarkEvaluator
from evaluation.enhanced_metrics import EnhancedMetricsCalculator

# Initialize evaluator
evaluator = BenchmarkEvaluator("path/to/benchmark")

# Evaluate a model
results = evaluator.evaluate_model(model_api, "model_name")

# Generate metrics report
metrics = EnhancedMetricsCalculator.calculate_enhanced_retrieval_metrics(results)
```

### Sample Model API Implementation

```python
class YourDebugModel:
    def debug_issue(self, bug_data: Dict[str, Any]) -> Dict[str, Any]:
        # Your model implementation
        return {
            "files_retrieved": [...],
            "files_modified": [...],
            "solution": "...",
            "artifacts_used": [...]
        }
```

## Performance Baselines

Based on the Chronos paper:
- **Traditional LLMs**: <12% success rate
- **Kodezi Chronos**: 65.3% success rate (not publicly available)

## Artifacts Created

- **Error Logs**: 10,000 files
- **Stack Traces**: 5,000 files
- **Documentation**: 16,576 files
- **Test Outputs**: 14,578 files
- **Commit Data**: 32,013 files
- **Code Snippets**: 141,702 files

## Requirements

- Python 3.8+
- 50GB+ disk space for full benchmark
- Dependencies: `pip install -r requirements.txt`

## Citation

If you use this benchmark in your research, please cite:

```
@article{chronos2024,
  title={Kodezi Chronos: Advancing Automated Debugging through Adaptive Graph-Guided Retrieval},
  author={Kodezi Research Team},
  year={2024}
}
```

## License

This benchmark is released under the MIT License. See LICENSE file for details.

## Acknowledgments

This implementation is based on the MRR benchmark described in the Kodezi Chronos research paper. The full official benchmark will be released by the Kodezi team.
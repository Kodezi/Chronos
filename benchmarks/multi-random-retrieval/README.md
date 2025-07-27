# Multi Random Retrieval (MRR) Benchmark

## 📊 Overview

The Multi Random Retrieval (MRR) benchmark is a novel evaluation framework specifically designed to test debugging-oriented retrieval capabilities in real-world scenarios. Unlike traditional benchmarks that focus on simple code completion, MRR evaluates a model's ability to find and correlate debugging information scattered across large codebases.

## ⚠️ Model Access Notice

The Kodezi Chronos model that achieves the reported performance metrics is **proprietary** and only available through [Kodezi OS](https://kodezi.com/os) starting Q1 2026. This benchmark framework is provided for:
- Understanding our evaluation methodology
- Comparing other models using the same framework
- Research and academic purposes

## 🎯 Benchmark Design

### Core Characteristics

The MRR benchmark consists of **5,000 real-world debugging scenarios** with the following properties:

1. **Context Scattering**: Relevant debugging information is randomly distributed across 10-50 files
2. **Temporal Dispersion**: Critical bug context spans 3-12 months of commit history
3. **Obfuscated Dependencies**: Variable names and function calls are refactored between bug introduction and discovery
4. **Multi-Modal Artifacts**: Solutions require combining code, tests, logs, and documentation

### Difficulty Levels

| Level | Files | Time Span | Refactoring | Description |
|-------|-------|-----------|-------------|-------------|
| Easy | 10-20 | 3-6 months | Minimal | Direct dependencies, clear naming |
| Medium | 20-35 | 6-9 months | Moderate | Indirect dependencies, some renaming |
| Hard | 35-50 | 9-12 months | Extensive | Complex dependencies, significant refactoring |

## 📈 Evaluation Metrics

### Primary Metrics

1. **Retrieval Precision@k**: Fraction of retrieved artifacts that are relevant to the bug fix
   - k ∈ {5, 10, 20}
   - Relevance determined by expert annotation

2. **Retrieval Recall@k**: Fraction of all relevant artifacts successfully retrieved
   - Critical for ensuring complete context
   - Measured at same k values as precision

3. **Fix Accuracy**: Whether the generated fix passes all tests and doesn't introduce regressions
   - Binary metric (pass/fail)
   - Includes regression testing

4. **Context Efficiency**: Ratio of used vs retrieved tokens in the final solution
   - Measures retrieval quality
   - Efficiency = tokens_used / tokens_retrieved

### Secondary Metrics

- **Time to Solution**: Wall-clock time from bug report to validated fix
- **Iteration Count**: Number of fix-test-refine cycles needed
- **Cross-File Accuracy**: Success rate for bugs spanning multiple files
- **Temporal Accuracy**: Success rate for bugs requiring historical context

## 🏆 Benchmark Results

### Overall Performance

| Model | Precision@10 | Recall@10 | Fix Accuracy | Context Efficiency |
|-------|--------------|-----------|--------------|-------------------|
| **Kodezi Chronos** | **89.2%** | **84.7%** | **67.3%** | **0.71** |
| GPT-4 + RAG | 42.3% | 31.7% | 8.9% | 0.23 |
| Claude-3 + Vector DB | 48.1% | 36.2% | 11.2% | 0.28 |
| Gemini-1.5 + Graph | 51.7% | 41.8% | 14.6% | 0.31 |

### Performance by Difficulty

| Model | Easy | Medium | Hard |
|-------|------|--------|------|
| **Kodezi Chronos** | **78.4%** | **69.2%** | **54.3%** |
| GPT-4 + RAG | 15.2% | 7.8% | 3.4% |
| Claude-3 + Vector DB | 18.7% | 9.3% | 5.1% |
| Gemini-1.5 + Graph | 22.1% | 12.4% | 6.9% |

## 🗂️ Dataset Structure

### Bug Instance Format

```json
{
  "bug_id": "mrr_python_001",
  "language": "python",
  "difficulty": "medium",
  "bug_type": "null_pointer",
  "repository_size": "~50K LOC",
  "file_count": 28,
  "time_span_months": 7,
  "description": "Application crashes with AttributeError when processing user exports",
  "ground_truth": {
    "root_cause": "Missing null check after authentication refactor",
    "files_involved": ["auth.py", "export.py", "models.py"],
    "commits_relevant": ["a1b2c3", "d4e5f6", "789abc"],
    "fix_location": {
      "file": "export.py",
      "line": 142,
      "function": "process_user_export"
    }
  },
  "test_suite": "tests/test_export.py",
  "validation_criteria": "All 47 tests must pass"
}
```

### Evaluation Protocol

1. **Setup**: Initialize model with repository state at bug report time
2. **Retrieval**: Model retrieves relevant context using its retrieval mechanism
3. **Generation**: Model proposes bug fix based on retrieved context
4. **Validation**: Run test suite to verify fix correctness
5. **Metrics**: Calculate precision, recall, accuracy, and efficiency

## 🔧 Running the Benchmark

### Prerequisites

```bash
# Install evaluation framework
pip install mrr-benchmark

# Download dataset (public subset)
wget https://github.com/kodezi/mrr-benchmark/releases/download/v1.0/mrr_dataset_public.tar.gz
tar -xzf mrr_dataset_public.tar.gz
```

### Basic Usage

```python
from mrr_benchmark import MRRBenchmark, evaluate_model

# Initialize benchmark
benchmark = MRRBenchmark(dataset_path="./mrr_dataset_public")

# Evaluate your model
results = evaluate_model(
    model=your_model,
    benchmark=benchmark,
    k_values=[5, 10, 20],
    verbose=True
)

# Print results
print(f"Precision@10: {results['precision_at_10']:.2%}")
print(f"Recall@10: {results['recall_at_10']:.2%}")
print(f"Fix Accuracy: {results['fix_accuracy']:.2%}")
print(f"Context Efficiency: {results['context_efficiency']:.2f}")
```

### Custom Evaluation

```python
# For models with custom retrieval mechanisms
class YourCustomEvaluator(MRREvaluator):
    def retrieve_context(self, bug_instance):
        # Your retrieval logic here
        return retrieved_artifacts
    
    def generate_fix(self, bug_instance, context):
        # Your generation logic here
        return proposed_fix

# Run evaluation
evaluator = YourCustomEvaluator(your_model)
results = benchmark.evaluate(evaluator)
```

## 📊 Detailed Analysis

### Why Chronos Excels

1. **Adaptive Graph-Guided Retrieval (AGR)**
   - Dynamic k-hop expansion based on query complexity
   - Achieves 89.2% precision vs 42.3% for flat retrieval

2. **Debug-Specific Training**
   - Trained on 15M+ real debugging sessions
   - Understands debugging patterns, not just code syntax

3. **Persistent Memory**
   - Learns from repository history
   - Recognizes recurring bug patterns

4. **Multi-Modal Understanding**
   - Correlates code, logs, tests, and documentation
   - 84.7% recall ensures comprehensive context

### Common Failure Modes

Even Chronos struggles with:
- **Extreme scattering**: Bugs requiring 50+ files (54.3% accuracy)
- **Domain-specific**: Bugs needing specialized knowledge (42.1% accuracy)
- **Hardware-dependent**: Platform-specific issues (31.2% accuracy)

## 🔬 Research Opportunities

### Open Questions

1. How can retrieval mechanisms better handle temporal code evolution?
2. What's the optimal balance between precision and recall for debugging?
3. How can models learn domain-specific debugging patterns?
4. Can we reduce the computational cost while maintaining accuracy?

### Extending the Benchmark

We welcome contributions to:
- Add more programming languages
- Include domain-specific scenarios
- Develop new evaluation metrics
- Create visualization tools

## 📚 Citation

If you use the MRR benchmark in your research, please cite:

```bibtex
@article{khan2025chronos,
  title={Kodezi Chronos: A Debugging-First Language Model for 
         Repository-Scale, Memory-Driven Code Understanding},
  author={Khan, Ishraq and Chowdary, Assad and 
          Haseeb, Sharoz and Patel, Urvish},
  journal={arXiv preprint arXiv:2507.12482},
  year={2025}
}
```

## 📞 Contact

- **Benchmark Questions**: mrr-benchmark@kodezi.com
- **Research Collaboration**: research@kodezi.com
- **Chronos Access**: [kodezi.com/os](https://kodezi.com/os)

---

**Note**: The MRR benchmark is designed to push the boundaries of debugging-oriented retrieval. Current models struggle with this benchmark, highlighting the need for specialized architectures like Chronos.
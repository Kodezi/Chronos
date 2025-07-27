# Multi-Random Retrieval (MRR) Benchmark Implementation

<div align="center">

## The Revolutionary Debugging-Oriented Evaluation Framework

[![Paper](https://img.shields.io/badge/Paper-arXiv:2507.12482-red.svg?style=for-the-badge)](https://arxiv.org/abs/2507.12482)
[![Performance](https://img.shields.io/badge/Chronos%20Precision-89.2%25-brightgreen.svg?style=for-the-badge)](../../results/performance_tables/mrr_benchmark_results.csv)
[![Benchmark](https://img.shields.io/badge/Test%20Suite-5000%20Bugs-blue.svg?style=for-the-badge)](dataset/)

</div>

---

## 🎯 Overview

The Multi-Random Retrieval (MRR) benchmark is a novel evaluation framework specifically designed for debugging-oriented retrieval. Unlike classical benchmarks that test simple pattern matching, MRR simulates real-world debugging scenarios where context is scattered across dozens of files over months of development history.

### Why MRR is Different

<div align="center">

| Traditional Benchmarks | MRR Benchmark |
|:--------------------|:--------------|
| Single-file context | 10-50 files scattered context |
| Static snapshots | 3-12 months temporal dispersion |
| Direct relationships | Obfuscated dependencies |
| Pattern matching | Causal reasoning required |
| Synthetic examples | Real debugging scenarios |

</div>

---

## 📊 Benchmark Design

### 1. Context Scattering

MRR deliberately scatters debugging context to simulate real-world scenarios:

```python
class MRRScenario:
    def __init__(self):
        self.bug_location = "src/api/handler.py:142"
        self.root_cause = "lib/cache/invalidator.py:89"
        self.related_files = [
            "config/cache_settings.yaml",      # Config change 3 months ago
            "migrations/20240115_schema.sql",  # Schema change 2 months ago
            "tests/integration/cache_test.py", # Failing test
            "docs/architecture/caching.md",    # Design decisions
            "commits/a3f42b1/diff.patch"       # Related fix 6 weeks ago
        ]
        self.temporal_span = "3-12 months"
        self.obfuscation_level = "high"
```

### 2. Evaluation Metrics

MRR evaluates four critical aspects:

1. **Retrieval Precision@k**: Fraction of retrieved artifacts relevant to bug fix
2. **Retrieval Recall@k**: Fraction of all relevant artifacts successfully retrieved
3. **Fix Accuracy**: Whether the generated fix passes all tests
4. **Context Efficiency**: Ratio of used vs retrieved tokens

### 3. Dataset Composition

<div align="center">

| Bug Category | Count | Temporal Span | File Distribution |
|:------------|:------|:--------------|:------------------|
| **Null Pointer** | 823 | 1-6 months | 5-15 files |
| **Race Condition** | 547 | 3-12 months | 10-30 files |
| **Memory Leak** | 612 | 2-8 months | 8-25 files |
| **API Breaking** | 891 | 1-12 months | 15-50 files |
| **Performance** | 734 | 2-9 months | 10-40 files |
| **Logic Errors** | 1,393 | 1-10 months | 5-35 files |
| **Total** | **5,000** | **1-12 months** | **5-50 files** |

</div>

---

## 🚀 Implementation

### 1. Scenario Generation

```python
class MRRGenerator:
    def generate_scenario(self, bug_type: str) -> MRRScenario:
        # Select base repository
        repo = self.select_repository(bug_type)
        
        # Identify bug manifestation point
        bug_location = self.inject_bug(repo, bug_type)
        
        # Determine root cause location
        root_cause = self.select_root_cause(repo, bug_location)
        
        # Scatter related context
        related_context = self.scatter_context(
            repo=repo,
            bug=bug_location,
            root=root_cause,
            min_files=10,
            max_files=50,
            temporal_range=(30, 365)  # days
        )
        
        # Add obfuscation
        obfuscated = self.obfuscate_relationships(
            context=related_context,
            refactor_probability=0.3,
            rename_probability=0.2
        )
        
        return MRRScenario(
            bug_location=bug_location,
            root_cause=root_cause,
            scattered_context=obfuscated,
            ground_truth_fix=self.generate_fix(root_cause)
        )
```

### 2. Evaluation Protocol

```python
class MRREvaluator:
    def evaluate_model(self, model, scenario: MRRScenario) -> MRRResults:
        start_time = time.time()
        
        # Phase 1: Retrieval
        retrieved_context = model.retrieve_context(
            error=scenario.bug_location,
            repository=scenario.repo
        )
        
        # Phase 2: Root Cause Analysis
        predicted_root = model.identify_root_cause(
            error=scenario.bug_location,
            context=retrieved_context
        )
        
        # Phase 3: Fix Generation
        generated_fix = model.generate_fix(
            root_cause=predicted_root,
            context=retrieved_context
        )
        
        # Phase 4: Validation
        validation_result = self.validate_fix(
            fix=generated_fix,
            tests=scenario.test_suite
        )
        
        # Calculate metrics
        return MRRResults(
            precision=self.calculate_precision(retrieved_context, scenario.ground_truth_context),
            recall=self.calculate_recall(retrieved_context, scenario.ground_truth_context),
            fix_accuracy=validation_result.all_tests_pass,
            context_efficiency=self.calculate_efficiency(retrieved_context, generated_fix),
            time_taken=time.time() - start_time
        )
```

---

## 📈 Results

### Overall Performance Comparison

<div align="center">

| Model | Precision@10 | Recall@10 | Fix Accuracy | Context Efficiency |
|:------|:------------|:----------|:-------------|:------------------|
| **Chronos** | **89.2%±1.4%** | **84.7%±1.8%** | **67.3%±2.1%** | **0.71±0.03** |
| GPT-4 + RAG | 42.3%±3.2% | 31.7%±3.5% | 8.9%±2.4% | 0.23±0.05 |
| Claude-3 + VectorDB | 48.1%±2.9% | 36.2%±3.1% | 11.2%±2.2% | 0.28±0.04 |
| Gemini-1.5 + Graph | 51.7%±2.7% | 41.8%±2.8% | 14.6%±2.0% | 0.31±0.04 |

***p < 0.001 for all Chronos comparisons (n=5,000)**

</div>

### Performance by Temporal Dispersion

<div align="center">

| Temporal Span | Chronos | Best Baseline | Improvement |
|:-------------|:--------|:--------------|:------------|
| 0-3 months | 71.2% | 16.3% (Gemini) | 4.4x |
| 3-6 months | 68.4% | 12.7% (Gemini) | 5.4x |
| 6-9 months | 65.8% | 9.1% (Claude) | 7.2x |
| 9-12 months | 62.3% | 5.8% (GPT-4) | 10.7x |

</div>

---

## 🔬 Key Insights

### 1. Retrieval Strategy Impact

```
Flat Retrieval (Baseline):
- Searches for similar code snippets
- Misses causal relationships
- Limited to syntactic similarity
- Result: 23.4% debug success

Graph-Guided Retrieval (Chronos):
- Follows semantic relationships
- Understands code evolution
- Captures hidden dependencies
- Result: 87.1% debug success
```

### 2. Context Scattering Challenge

Real bugs involve context scattered across:
- **Multiple files**: Average 23.7 files contain relevant context
- **Time periods**: Average 4.3 months between bug introduction and manifestation
- **Refactoring**: 34% of bugs involve refactored code
- **Dependencies**: Average 6.2 dependency chains to traverse

### 3. Why Traditional Models Fail

1. **Token Window Limitations**: Even 1M tokens can't hold months of history
2. **Flat Attention**: No understanding of code structure
3. **No Temporal Awareness**: Can't track code evolution
4. **Missing Causality**: Treat symptoms, not root causes

---

## 🛠️ Running the Benchmark

### Prerequisites

```bash
pip install -r requirements.txt
# Requires: numpy, pandas, scikit-learn, pytest
```

### Basic Usage

```python
from mrr_benchmark import MRRBenchmark, MRREvaluator

# Initialize benchmark
benchmark = MRRBenchmark(dataset_path="./dataset/")

# Load your model
model = YourDebugModel()

# Run evaluation
evaluator = MRREvaluator()
results = evaluator.evaluate(
    model=model,
    benchmark=benchmark,
    n_scenarios=1000
)

# Print results
print(f"Precision@10: {results.precision:.1%}")
print(f"Recall@10: {results.recall:.1%}")
print(f"Fix Accuracy: {results.fix_accuracy:.1%}")
print(f"Context Efficiency: {results.context_efficiency:.2f}")
```

### Advanced Configuration

```python
# Configure evaluation parameters
config = MRRConfig(
    max_retrieval_depth=5,
    temporal_weight=0.3,
    structural_weight=0.7,
    obfuscation_levels=["low", "medium", "high"],
    bug_categories=["all"],  # or specific categories
    confidence_threshold=0.9
)

results = evaluator.evaluate(model, benchmark, config)
```

---

## 📊 Detailed Metrics

### Precision and Recall Calculation

```python
def calculate_precision(retrieved: List[Artifact], ground_truth: List[Artifact]) -> float:
    """
    Precision = |retrieved ∩ ground_truth| / |retrieved|
    """
    relevant_retrieved = set(retrieved) & set(ground_truth)
    return len(relevant_retrieved) / len(retrieved) if retrieved else 0.0

def calculate_recall(retrieved: List[Artifact], ground_truth: List[Artifact]) -> float:
    """
    Recall = |retrieved ∩ ground_truth| / |ground_truth|
    """
    relevant_retrieved = set(retrieved) & set(ground_truth)
    return len(relevant_retrieved) / len(ground_truth) if ground_truth else 0.0
```

### Context Efficiency Metric

```python
def calculate_efficiency(retrieved_context: Context, generated_fix: Fix) -> float:
    """
    Efficiency = tokens_used_in_fix / total_retrieved_tokens
    
    Measures how much of the retrieved context was actually useful
    """
    used_tokens = count_referenced_tokens(generated_fix, retrieved_context)
    total_tokens = count_total_tokens(retrieved_context)
    
    return used_tokens / total_tokens if total_tokens > 0 else 0.0
```

---

## 🏆 Leaderboard

### Current Rankings (as of paper publication)

<div align="center">

| Rank | Model | MRR Score | Fix Accuracy | Efficiency |
|:-----|:------|:----------|:-------------|:-----------|
| 1 | **Kodezi Chronos** | **0.853** | **67.3%** | **0.71** |
| 2 | Gemini-1.5 + Graph | 0.367 | 14.6% | 0.31 |
| 3 | Claude-3 + VectorDB | 0.342 | 11.2% | 0.28 |
| 4 | GPT-4 + RAG | 0.291 | 8.9% | 0.23 |
| 5 | CodeT5 + Retrieval | 0.187 | 5.2% | 0.19 |

**MRR Score** = 0.4 × Precision + 0.3 × Recall + 0.2 × Fix Accuracy + 0.1 × Efficiency

</div>

---

## 🔮 Future Extensions

### Planned Enhancements

1. **Cross-Language Debugging**: Bugs spanning multiple programming languages
2. **Microservice Scenarios**: Distributed system debugging
3. **Security Vulnerabilities**: CVE-based scenarios
4. **Performance Regressions**: Subtle performance degradation bugs

### Contributing New Scenarios

We welcome contributions! See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on:
- Adding new bug categories
- Creating realistic scenarios
- Improving evaluation metrics
- Submitting benchmark results

---

## 📚 References

1. Khan, I., Chowdary, A., Haseeb, S., & Patel, U. (2025). Kodezi Chronos: A Debugging-First Language Model. *arXiv:2507.12482*

2. The MRR benchmark dataset and evaluation scripts are available in this repository for research purposes.

---

<div align="center">

**Revolutionizing debugging evaluation, one scattered context at a time**

[Learn More](https://kodezi.com/chronos) | [Paper](https://arxiv.org/abs/2507.12482) | [Chronos Access](https://kodezi.com/os)

</div>
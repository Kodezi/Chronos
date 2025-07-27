# How to Evaluate Your Model Against Chronos Benchmarks

## ⚠️ Important Notice

Kodezi Chronos is **proprietary technology** and will be available exclusively through [Kodezi OS](https://kodezi.com/os) starting Q1 2026. This framework allows you to:
- Compare your model using the same benchmarks
- Understand Chronos's evaluation methodology
- Prepare for integration with Kodezi OS

## 📊 Benchmark Suite Overview

### 1. Multi Random Retrieval (MRR)
- 5,000 real-world debugging scenarios
- Tests retrieval across scattered context
- Measures precision, recall, and fix accuracy

### 2. Debug Categories
- 6 bug types: syntax, logic, concurrency, memory, API, performance
- 3 difficulty levels per category
- Language-specific test cases

### 3. Repository Scale Tests
- Small (<10K LOC)
- Medium (10K-100K LOC)
- Large (100K-1M LOC)
- Enterprise (>1M LOC)

## 🚀 Getting Started

### Prerequisites

```bash
# Install evaluation framework
pip install kodezi-benchmark-suite

# Download public test data
wget https://github.com/kodezi/chronos-benchmarks/releases/latest/benchmarks.tar.gz
tar -xzf benchmarks.tar.gz
```

### Basic Evaluation

```python
from kodezi_benchmarks import BenchmarkSuite, ModelAdapter

# Implement your model adapter
class YourModelAdapter(ModelAdapter):
    def __init__(self, model):
        self.model = model
    
    def retrieve_context(self, bug_description, repository):
        # Your retrieval logic
        return self.model.retrieve(bug_description, repository)
    
    def generate_fix(self, bug_context, retrieved_artifacts):
        # Your fix generation logic
        return self.model.generate(bug_context, retrieved_artifacts)
    
    def validate_fix(self, fix, test_suite):
        # Run tests to validate
        return self.run_tests(fix, test_suite)

# Run benchmarks
adapter = YourModelAdapter(your_model)
suite = BenchmarkSuite()
results = suite.evaluate(adapter)

# Compare with Chronos
chronos_results = suite.load_baseline('chronos')
comparison = suite.compare(results, chronos_results)
print(comparison.summary())
```

## 📈 Evaluation Metrics

### Primary Metrics

1. **Debug Success Rate**
   - Percentage of bugs correctly fixed
   - Must pass all regression tests
   - Chronos achieves: 65.3%

2. **Root Cause Accuracy**
   - Correctly identifies bug source
   - Measured by expert annotation
   - Chronos achieves: 78.4%

3. **Fix Cycles**
   - Number of iterations to valid fix
   - Lower is better
   - Chronos average: 2.2

4. **Retrieval Quality**
   - Precision@10: 89.2% (Chronos)
   - Recall@10: 84.7% (Chronos)
   - Context efficiency: 0.71 (Chronos)

### Detailed Evaluation

```python
# Evaluate specific bug categories
category_results = suite.evaluate_by_category(adapter, [
    'syntax_errors',
    'logic_errors',
    'concurrency_issues',
    'memory_issues',
    'api_misuse',
    'performance_issues'
])

# Evaluate by repository scale
scale_results = suite.evaluate_by_scale(adapter, [
    'small',
    'medium', 
    'large',
    'enterprise'
])

# Generate detailed report
report = suite.generate_report(results, include_statistics=True)
report.save('evaluation_report.pdf')
```

## 🔬 Advanced Evaluation

### Custom Metrics

```python
from kodezi_benchmarks import Metric

class TimeToFirstFixMetric(Metric):
    """Measure time until first valid fix attempt"""
    
    def calculate(self, debug_session):
        first_valid = next(
            (i for i, attempt in enumerate(debug_session.attempts) 
             if attempt.passes_tests),
            None
        )
        if first_valid is None:
            return float('inf')
        return debug_session.attempts[first_valid].timestamp

# Add custom metric
suite.add_metric('time_to_first_fix', TimeToFirstFixMetric())
```

### Ablation Studies

```python
# Test without specific capabilities
ablation_results = {
    'full_model': suite.evaluate(adapter),
    'no_retrieval': suite.evaluate(adapter, disable_retrieval=True),
    'no_memory': suite.evaluate(adapter, disable_memory=True),
    'single_file_only': suite.evaluate(adapter, max_files=1)
}

# Analyze component importance
importance = suite.analyze_ablation(ablation_results)
```

## 📊 Interpreting Results

### Success Criteria

Your model is considered successful if it achieves:
- Debug success rate > 50%
- Root cause accuracy > 60%
- Average fix cycles < 4
- Retrieval precision@10 > 70%

### Performance Tiers

| Tier | Debug Success | vs Chronos | Classification |
|------|---------------|------------|----------------|
| S | >60% | >90% | State-of-the-art |
| A | 40-60% | 60-90% | Production-ready |
| B | 20-40% | 30-60% | Promising |
| C | 10-20% | 15-30% | Experimental |
| D | <10% | <15% | Needs work |

## 🎯 Tips for Better Performance

### 1. Retrieval Optimization
- Implement semantic code search
- Use AST-based retrieval
- Consider temporal context
- Index commit history

### 2. Context Understanding
- Parse error messages thoroughly
- Trace stack traces to source
- Understand test assertions
- Correlate logs with code

### 3. Fix Generation
- Start with minimal changes
- Validate against test suite
- Consider side effects
- Handle edge cases

### 4. Iterative Refinement
- Learn from failed attempts
- Adjust based on test results
- Maintain fix history
- Implement rollback

## 🤝 Sharing Results

We encourage sharing benchmark results:

1. **Submit to Leaderboard**
   ```bash
   kodezi-benchmark submit results.json \
     --model-name "YourModel" \
     --organization "YourOrg" \
     --paper-url "arxiv.org/..."
   ```

2. **Publish Analysis**
   - Include full methodology
   - Report all metrics
   - Discuss failure cases
   - Compare with baselines

3. **Contribute Improvements**
   - Suggest new test cases
   - Report benchmark issues
   - Share evaluation tools

## 📚 Resources

### Documentation
- [Benchmark Details](https://docs.kodezi.com/chronos/benchmarks)
- [Evaluation Guide](https://docs.kodezi.com/chronos/evaluation)
- [API Reference](https://docs.kodezi.com/chronos/api)

### Papers
- [Chronos Paper](https://arxiv.org/abs/2507.12482)
- [MRR Benchmark](https://arxiv.org/abs/2507.12483)

### Community
- [Forum](https://forum.kodezi.com/benchmarks)
- [GitHub](https://github.com/kodezi/chronos/discussions)

## ❓ FAQ

### Can I use these benchmarks commercially?
Yes, the benchmark suite is open for research and commercial use. The Chronos model itself is proprietary.

### How often are benchmarks updated?
We add new test cases quarterly and update baselines with each Chronos release.

### Can I test on private code?
Yes, the framework supports private repositories. Results remain confidential.

### Is there a cloud evaluation service?
Coming Q2 2026 with Kodezi OS launch.

---

**Ready to benchmark your model? Join the community of researchers pushing the boundaries of automated debugging.**
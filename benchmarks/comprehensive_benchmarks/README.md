# Comprehensive Benchmarks for Kodezi Chronos 2025

This directory contains comprehensive benchmark implementations based on the 2025 research paper findings.

## Overview

These benchmarks test Kodezi Chronos across various challenging debugging scenarios, including the identified limitations from the paper.

## Benchmark Categories

### 1. Debugging Benchmarks (`debugging_benchmarks.py`)
- **Purpose**: Test general debugging capabilities across 16 bug categories
- **Scenarios**: 5,000 MRR scenarios with 12,500 total bugs
- **Bug Categories**:
  - Syntax errors (10%)
  - Logic bugs (24%)
  - Concurrency issues (16%)
  - Memory problems (12%)
  - API misuse (18%)
  - Performance bugs (8%)
  - And 10 additional categories
- **Features**:
  - Context scattering (10-50 files)
  - Temporal dispersion (3-12 months)
  - Multi-modal artifacts
  - Complexity scoring

### 2. Retrieval Benchmarks (`retrieval_benchmarks.py`)
- **Purpose**: Test AGR (Adaptive Graph-Guided Retrieval) performance
- **Key Metrics**:
  - 92% precision at 85% recall
  - O(k log d) complexity verification
  - Comparison with flat retrieval, BM25, Graph RAG
- **Features**:
  - Code graph generation (10,000 nodes)
  - Query complexity levels (1-5 hops)
  - Edge type weighting
  - Semantic similarity integration

### 3. Temporal Benchmarks (`temporal_benchmarks.py`)
- **Purpose**: Test PDM (Persistent Debug Memory) effectiveness
- **Key Metrics**:
  - Cross-session learning rate
  - Pattern recognition over time
  - Codebase evolution handling
- **Features**:
  - 365-day bug event sequences
  - Pattern learning simulation
  - Temporal distribution analysis
  - Codebase evolution tracking

### 4. Hardware-Dependent Benchmarks (`hardware_dependent_benchmarks.py`)
- **Purpose**: Test debugging on hardware-specific issues
- **Expected Success Rate**: 23.4% (limitation from paper)
- **Bug Types**:
  - Cache coherence issues
  - Memory alignment problems
  - False sharing
  - NUMA performance
  - Endianness bugs
- **Features**:
  - Multiple hardware configurations
  - Architecture-specific issues
  - Reproducibility challenges

### 5. Dynamic Language Benchmarks (`dynamic_language_benchmarks.py`)
- **Purpose**: Test debugging on dynamic language issues
- **Expected Success Rate**: 41.2% (limitation from paper)
- **Languages**: Python, JavaScript, Ruby, PHP, etc.
- **Bug Types**:
  - Type confusion
  - Duck typing failures
  - Metaprogramming errors
  - Async timing bugs
  - Runtime type errors

### 6. Distributed Systems Benchmarks (`distributed_systems_benchmarks.py`)
- **Purpose**: Test debugging on distributed systems
- **Expected Success Rate**: ~30% (limitation from paper)
- **System Types**:
  - Replicated databases
  - Microservices
  - Distributed caches
  - Consensus clusters
- **Bug Types**:
  - Network partitions
  - Byzantine failures
  - Clock skew
  - Consistency violations
  - Cascading failures

### 7. Performance Regression Benchmarks (`performance_regression_benchmarks.py`)
- **Purpose**: Test performance debugging with flame graph analysis
- **Features**:
  - Flame graph generation
  - Performance profiling simulation
  - Hotspot detection
  - Optimization validation
- **Issue Types**:
  - CPU bottlenecks
  - Memory leaks
  - Lock contention
  - Cache misses
  - Algorithmic complexity

### 8. Multi-Language Benchmarks (`multi_language_benchmarks.py`)
- **Purpose**: Test debugging across multiple programming languages
- **Architectures**:
  - Full-stack web (TypeScript + Python + Go + Rust)
  - Mobile + backend (Swift + Kotlin + Java + C++)
  - Data pipeline (Python + Scala + Java + Go)
  - Polyglot microservices
- **Challenges**:
  - Type mismatches across boundaries
  - Serialization incompatibilities
  - Different concurrency models
  - Memory management differences

## Running the Benchmarks

### Individual Benchmark Execution

```bash
# Run debugging benchmarks
python debugging_benchmarks.py

# Run retrieval benchmarks with complexity verification
python retrieval_benchmarks.py

# Run temporal learning benchmarks
python temporal_benchmarks.py

# Run limitation benchmarks
python hardware_dependent_benchmarks.py
python dynamic_language_benchmarks.py
python distributed_systems_benchmarks.py

# Run performance benchmarks
python performance_regression_benchmarks.py

# Run multi-language benchmarks
python multi_language_benchmarks.py
```

### Full Benchmark Suite

```bash
# Run all benchmarks with evaluation
python ../run_full_evaluation.py
```

## Benchmark Output

Each benchmark generates:
1. Scenario statistics
2. Performance metrics
3. Success rates by category
4. Timing analysis
5. Key insights
6. Example scenarios

## Evaluation Metrics

### Primary Metrics
- **Fix Accuracy**: Tests passed after fix
- **Root Cause Accuracy**: Correct identification
- **Retrieval Precision/Recall**: Context quality
- **Time to Resolution**: End-to-end timing

### Secondary Metrics
- **Iterations Required**: Debugging cycles
- **Context Efficiency**: Tokens used
- **Cross-Session Learning**: Pattern reuse
- **Complexity Correlation**: Success vs complexity

## Expected Results (from Paper)

- **Overall**: 67.3% debug success rate
- **Syntax Errors**: 94.2% (1.1x improvement)
- **Logic Bugs**: 72.8% (6.0x improvement)
- **Concurrency**: 58.3% (18.2x improvement)
- **Memory Issues**: 61.7% (10.8x improvement)
- **API Misuse**: 79.1% (4.2x improvement)
- **Performance**: 65.4% (8.8x improvement)

### Known Limitations
- **Hardware-dependent**: 23.4% success
- **Dynamic languages**: 41.2% success
- **Distributed systems**: ~30% success

## Customization

Benchmarks can be customized by modifying:
- Number of scenarios (`n_scenarios`)
- Bug distributions
- Complexity factors
- System architectures
- Language combinations

## Integration with Chronos

These benchmarks are designed to:
1. Test the full Chronos architecture
2. Validate AGR and PDM components
3. Measure real-world performance
4. Identify areas for improvement
5. Track progress over time

## Contributing

When adding new benchmarks:
1. Follow the existing structure
2. Include realistic scenarios
3. Add evaluation metrics
4. Document expected results
5. Test with sample data first

## References

Based on the Kodezi Chronos 2025 research paper:
- Multi Random Retrieval (MRR) benchmark
- Adaptive Graph-Guided Retrieval (AGR)
- Persistent Debug Memory (PDM)
- Statistical validation methods
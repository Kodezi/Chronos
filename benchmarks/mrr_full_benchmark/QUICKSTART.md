# MRR Benchmark Quick Start Guide

## Overview
The Kodezi Chronos MRR Benchmark evaluates debugging capabilities of language models with 5,000 real-world debugging scenarios.

## Prerequisites
- Python 3.8+
- 50GB free disk space
- Git

## Installation

```bash
# Clone the repository
git clone https://github.com/kodezi/chronos-benchmark.git
cd chronos-benchmark/Chronos/benchmarks/mrr_full_benchmark

# Install dependencies
pip install -r requirements.txt
```

## Quick Test Run

Run evaluation on a small subset (10 cases) to verify setup:

```bash
python evaluation/evaluate_model.py \
    --model "test_model" \
    --benchmark-path . \
    --output-dir ./test_results \
    --subset 10
```

## Implementing Your Model

Create a file `my_model.py`:

```python
from pathlib import Path
from typing import Dict, List, Any

class MyModelAPI:
    def __init__(self):
        # Initialize your model
        pass
    
    def debug_bug(self, 
                  bug_description: str,
                  symptoms: List[str],
                  repository_path: Path,
                  scattered_context: List[Dict],
                  time_limit: int) -> Dict[str, Any]:
        """
        Debug a bug and return the fix
        
        Args:
            bug_description: Natural language description of the bug
            symptoms: List of error messages/symptoms
            repository_path: Path to the code repository
            scattered_context: List of relevant file paths with metadata
            time_limit: Maximum time allowed in seconds
        
        Returns:
            Dictionary containing:
            - root_cause: str (identified root cause)
            - iterations: int (number of debugging iterations)
            - tokens_used: int (total tokens consumed)
            - memory_used_mb: float (peak memory usage)
            - files_retrieved: List[str] (files accessed during debugging)
            - files_modified: List[str] (files that were changed)
        """
        
        # Step 1: Analyze the bug description and symptoms
        
        # Step 2: Retrieve relevant files based on scattered_context
        
        # Step 3: Identify the root cause
        
        # Step 4: Generate and apply the fix
        
        # Step 5: Return results
        return {
            'root_cause': 'Your identified root cause',
            'iterations': 1,
            'tokens_used': 10000,
            'memory_used_mb': 256.0,
            'files_retrieved': ['file1.py', 'file2.py'],
            'files_modified': ['file1.py']
        }
```

## Full Evaluation

Run on the complete benchmark:

```bash
python evaluation/evaluate_model.py \
    --model "my_model" \
    --benchmark-path . \
    --output-dir ./results
```

## Understanding Results

Results are saved in three formats:

1. **JSON Results** (`my_model_results_TIMESTAMP.json`): Raw evaluation data
2. **Performance Summary** (`my_model_performance_TIMESTAMP.json`): Aggregated metrics
3. **Markdown Report** (`my_model_report_TIMESTAMP.md`): Human-readable report

### Key Metrics to Watch

- **Success Rate**: Percentage of bugs correctly fixed (target: >60%)
- **Root Cause Accuracy**: How often the correct root cause is identified
- **MRR (Mean Reciprocal Rank)**: Quality of file retrieval
- **Average Iterations**: Efficiency of debugging process

## Sample Bug Case

```json
{
  "bug_id": "mrr_logic_errors_0042",
  "description": "Function returns incorrect result for edge case",
  "symptoms": [
    "Test test_calculate_discount fails",
    "AssertionError: Expected 15.0 but got 0.0"
  ],
  "scattered_context": [
    {
      "file_path": "src/pricing/calculator.py",
      "relevance": "critical",
      "key_elements": ["calculate_discount", "edge_case_handling"]
    },
    {
      "file_path": "tests/test_calculator.py",
      "relevance": "high",
      "key_elements": ["test_calculate_discount"]
    }
  ]
}
```

## Tips for Better Performance

1. **Efficient Context Retrieval**: Use the scattered_context hints effectively
2. **Iterative Debugging**: Multiple small fixes often work better than one large change
3. **Test Validation**: Always validate fixes against the symptoms
4. **Memory Management**: Clean up large objects between iterations

## Baseline Comparison

Your model should aim to beat these baselines:

| Metric | GPT-4 | Claude-3 | Target |
|--------|-------|----------|--------|
| Success Rate | 8.5% | 7.8% | >60% |
| Root Cause Accuracy | 12.3% | 11.7% | >70% |
| Avg Iterations | 6.5 | 6.8 | <3 |

## Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce batch size or implement streaming
2. **Timeout**: Optimize retrieval strategy or increase time limit
3. **Low Success Rate**: Focus on better root cause identification

### Debug Mode

Enable verbose logging:

```bash
export MRR_DEBUG=1
python evaluation/evaluate_model.py --model "my_model" ...
```

## Next Steps

1. Start with category-specific evaluation:
   ```bash
   python evaluation/evaluate_model.py \
       --model "my_model" \
       --category "syntax_errors" \
       --subset 50
   ```

2. Analyze failure cases in the results JSON

3. Iterate on your retrieval and fixing strategies

4. Compare against baseline models

## Support

- GitHub Issues: https://github.com/kodezi/chronos-benchmark/issues
- Documentation: See README.md for detailed information
- Research Paper: https://arxiv.org/abs/xxxx.xxxxx (coming Q1 2026)

---

**Note**: This is a preview release. The full Kodezi Chronos model will be released in Q1 2026.
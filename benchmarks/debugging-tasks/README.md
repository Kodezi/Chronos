# Debugging Task Categories

This directory contains specifications for the different categories of debugging tasks used to evaluate Kodezi Chronos. Each category represents real-world debugging scenarios that developers face daily.

## Task Categories Overview

| Category | Description | Test Cases | Avg. Complexity |
|----------|-------------|------------|-----------------|
| Syntax | Syntax errors and typos | 500 | Low |
| Logic | Logical errors in algorithms | 1,200 | Medium |
| Concurrency | Race conditions, deadlocks | 800 | High |
| Memory | Memory leaks, buffer overflows | 600 | High |
| API | API misuse, version conflicts | 900 | Medium |
| Performance | Performance regressions | 400 | Medium |

## Category Details

### 1. Syntax Errors
- **Description**: Basic syntax mistakes, typos, missing brackets
- **Examples**: Missing semicolons, unclosed parentheses, typos in variable names
- **Chronos Success Rate**: 94.2%
- **Why High Success**: Pattern matching and syntax tree analysis

### 2. Logic Errors
- **Description**: Flawed algorithm logic, incorrect conditions, off-by-one errors
- **Examples**: Wrong loop conditions, incorrect boolean logic, algorithm mistakes
- **Chronos Success Rate**: 72.8%
- **Key Challenge**: Requires understanding intended behavior

### 3. Concurrency Bugs
- **Description**: Multi-threading issues, race conditions, deadlocks
- **Examples**: Unsynchronized access, ordering violations, atomicity violations
- **Chronos Success Rate**: 58.3%
- **Key Challenge**: Non-deterministic behavior, timing dependencies

### 4. Memory Issues
- **Description**: Memory management problems, leaks, buffer overflows
- **Examples**: Null pointer dereferences, use-after-free, memory leaks
- **Chronos Success Rate**: 61.7%
- **Key Challenge**: Requires tracking object lifecycles

### 5. API Misuse
- **Description**: Incorrect API usage, version incompatibilities
- **Examples**: Wrong parameter types, deprecated methods, breaking changes
- **Chronos Success Rate**: 79.1%
- **Why High Success**: Good documentation retrieval

### 6. Performance Regressions
- **Description**: Code changes that degrade performance
- **Examples**: O(n²) algorithms, excessive I/O, cache misses
- **Chronos Success Rate**: 65.4%
- **Key Challenge**: Requires performance profiling integration

## Task Format

Each debugging task follows this structure:

```json
{
  "task_id": "TASK_001",
  "category": "logic",
  "difficulty": "medium",
  "bug_description": "Function returns incorrect result for edge cases",
  "code_context": {
    "file": "calculator.py",
    "function": "calculate_average",
    "line_range": [45, 67]
  },
  "test_case": {
    "input": "[1, 2, 3, 4, 5]",
    "expected": "3.0",
    "actual": "2.5"
  },
  "ground_truth": {
    "root_cause": "Integer division instead of float division",
    "fix": "Change sum(numbers) / len(numbers) to sum(numbers) / float(len(numbers))",
    "fixed_code": "return sum(numbers) / float(len(numbers))"
  },
  "metadata": {
    "language": "python",
    "framework": "none",
    "real_world": true,
    "source": "github_issue_12345"
  }
}
```

## Evaluation Metrics

### Primary Metrics
1. **Fix Success Rate**: Does the fix make tests pass?
2. **Root Cause Accuracy**: Is the identified cause correct?
3. **No Regression**: Does the fix break other tests?

### Secondary Metrics
1. **Fix Quality**: Is the fix idiomatic and maintainable?
2. **Explanation Quality**: Is the reasoning clear?
3. **Time to Fix**: How many iterations needed?

## Difficulty Levels

### Easy (20% of tasks)
- Single file fixes
- Clear error messages
- Direct cause-effect relationship
- Example: Typo in variable name

### Medium (50% of tasks)
- 2-3 file involvement
- Requires some inference
- Common patterns
- Example: Null pointer from refactoring

### Hard (30% of tasks)
- Many files involved
- Complex dependencies
- Subtle interactions
- Example: Race condition in distributed system

## Real-World Sources

Our debugging tasks come from:
1. **Open Source Projects** (40%)
   - Popular GitHub repositories
   - Real bug reports with fixes
   - Verified by maintainers

2. **Industry Partners** (30%)
   - Anonymized production bugs
   - Enterprise-scale issues
   - Complex integration problems

3. **Synthetic Generation** (30%)
   - Systematic coverage of bug types
   - Edge cases and corner cases
   - Controlled difficulty progression

## Task Validation

Each task goes through validation:
1. **Human Review**: Developers verify bug and fix
2. **Automated Testing**: Fix must pass all tests
3. **Multiple Solutions**: Accept alternative correct fixes
4. **Quality Check**: Fix must be production-ready

## Usage

To run evaluation on a specific category:

```python
from benchmarks import DebugTaskEvaluator

evaluator = DebugTaskEvaluator()
results = evaluator.evaluate_category(
    model=your_model,
    category="logic",
    num_tasks=100
)

print(f"Success Rate: {results.success_rate}%")
print(f"Avg Time: {results.avg_time}s")
```

## Contributing

To contribute new debugging tasks:
1. Use the task format template
2. Ensure real-world relevance
3. Provide verified ground truth
4. Include comprehensive test cases

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.
# Adaptive Graph-Guided Retrieval (AGR)

## Overview

Adaptive Graph-Guided Retrieval (AGR) is Chronos's breakthrough mechanism for achieving unlimited effective context through intelligent, dynamic retrieval. Unlike flat retrieval systems, AGR understands code structure and relationships, expanding its search adaptively based on query complexity.

## Core Concepts

### 1. Graph-Based Code Representation

Code elements are represented as nodes in a directed graph:

```
Nodes:
- Functions/Methods
- Classes/Modules  
- Variables/Constants
- Tests
- Documentation
- Commits/PRs
- Issues/Bugs

Edges (with weights):
- Calls (1.0)
- Imports (0.9)
- Inherits (0.9)
- Tests (0.8)
- Documents (0.7)
- Modifies (0.8)
- Fixes (0.9)
```

### 2. Adaptive Depth Expansion

AGR dynamically determines retrieval depth (k-hops) based on:

```
k = f(query_complexity, confidence, information_gain)

where:
- query_complexity ∈ [0, 1]
- confidence = current retrieval confidence
- information_gain = diminishing returns metric
```

### 3. Retrieval Process

```
1. Initial Query Analysis
   - Decompose query into semantic components
   - Identify seed nodes in code graph
   - Estimate complexity score

2. Iterative Expansion
   for k in 1 to max_depth:
     - Retrieve k-hop neighbors
     - Calculate confidence score
     - Check diminishing returns
     - If confidence > threshold: stop
     
3. Context Assembly
   - Rank retrieved nodes by relevance
   - Filter redundant information
   - Construct focused context window
```

## AGR vs Traditional Retrieval

### Traditional Flat Retrieval

```
Query: "Fix authentication bug in export"

Traditional approach:
1. Vector similarity search
2. Return top-k documents
3. Hope relevant context included

Results:
- Often misses critical dependencies
- No understanding of code relationships
- Fixed retrieval depth
```

### AGR Approach

```
Query: "Fix authentication bug in export"

AGR approach:
1. Identify seed nodes: auth_service, export_handler
2. k=1: Direct calls and imports
   - Found: refreshToken(), exportUserData()
3. k=2: Dependencies and tests  
   - Found: token_cache, auth_tests
4. k=3: Historical context
   - Found: Recent refactoring commit
5. Confidence > 0.9: Stop

Results:
- Complete dependency chain
- Relevant historical context
- Optimal context size
```

## Performance Characteristics

### Retrieval Metrics by Depth

| k-depth | Precision | Recall | Debug Success | Time |
|---------|-----------|--------|---------------|------|
| k=1 | 84.3% | 72.1% | 58.2% | 8ms |
| k=2 | 91.2% | 86.4% | 72.4% | 23ms |
| k=3 | 88.7% | 89.2% | 71.8% | 67ms |
| **k=adaptive** | **92.8%** | **90.3%** | **87.1%** | **31ms** |
| Flat | 71.4% | 68.2% | 23.4% | 12ms |

### Complexity Analysis

- **Best case**: O(k) where k is typically 1-2 for simple queries
- **Average case**: O(k * branching_factor) with early termination
- **Worst case**: O(n) for full repository traversal (rare)

## Edge Type Priorities

Different edge types have different weights for traversal:

```python
edge_weights = {
    'calls': 1.0,        # Direct function calls
    'imports': 0.9,      # Module imports
    'inherits': 0.9,     # Class inheritance
    'overrides': 0.85,   # Method overriding
    'uses_type': 0.8,    # Type dependencies
    'tests': 0.8,        # Test coverage
    'modifies': 0.8,     # Variable modifications
    'documents': 0.7,    # Documentation links
    'related_pr': 0.6,   # Pull request associations
    'similar_pattern': 0.5  # Code similarity
}
```

## Confidence Scoring

AGR uses multi-factor confidence scoring:

```
confidence = w1 * node_relevance + 
             w2 * path_coherence +
             w3 * context_completeness +
             w4 * historical_success

where:
- node_relevance: Similarity to query
- path_coherence: Logical connection strength  
- context_completeness: Information sufficiency
- historical_success: Past debugging success rate
```

## Real-World Example

### Debugging a Null Pointer Exception

```
Initial State:
- Error: NullPointerException in ExportService
- Query: "Fix null pointer in user export"

AGR Execution:

Step 1 (k=1): Direct Context
Retrieved:
- ExportService.exportUserData() 
- AuthService.refreshToken()
Confidence: 0.72 (continue)

Step 2 (k=2): Extended Dependencies  
Retrieved:
- TokenCache implementation
- Recent refactoring commits
- Test_auth_null_cases
Confidence: 0.89 (continue)

Step 3 (k=3): Historical Patterns
Retrieved:
- Similar fix in UserService
- Team's null-handling patterns
- Related bug report #1234
Confidence: 0.94 (stop)

Final Context:
- 8 code files
- 3 test files  
- 2 commits
- 1 bug report
Total: ~4K tokens (vs 50K+ for full context)
```

## Optimization Strategies

### 1. Early Termination

Stop expansion when:
- Confidence exceeds threshold (0.9)
- Information gain < 0.1
- Time budget exceeded
- Maximum depth reached

### 2. Parallel Exploration

For complex queries, explore multiple paths simultaneously:
```
Thread 1: Code dependencies
Thread 2: Test coverage
Thread 3: Historical fixes
Merge results with deduplication
```

### 3. Caching and Memoization

- Cache frequently accessed subgraphs
- Memoize confidence calculations
- Reuse previous retrieval paths

## Limitations and Trade-offs

### Advantages
- Optimal context size
- Relationship-aware retrieval
- Adaptive to query complexity
- High precision and recall

### Limitations
- Initial graph construction cost
- Complex queries may timeout
- Requires well-structured code
- May miss non-obvious connections

## Future Enhancements

1. **Learning-based k-prediction**: ML model to predict optimal k
2. **Multi-modal edges**: Include runtime traces, logs
3. **Temporal weighting**: Prioritize recent changes
4. **Cross-repository retrieval**: Federated graph search

## Conclusion

AGR enables Chronos to achieve unlimited effective context by:
- Understanding code as a graph, not flat text
- Adapting retrieval depth to query needs
- Prioritizing relevant relationships
- Terminating when sufficient context acquired

This approach yields 5x better debugging success compared to flat retrieval while maintaining computational efficiency.